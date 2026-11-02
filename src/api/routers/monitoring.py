"""System and model monitoring API.

The monitoring page used to call ``/api/monitoring/*`` endpoints that did not
exist. This router provides real observations from the host and from the
database. Resource history is persisted as samples so charts build up over time
instead of displaying fabricated data.
"""

import logging
import shutil
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from ..security import get_current_active_user
from ...database import PROJECT_ROOT, get_db
from ...utils.time import utcnow
from ...database.models import (
    ComplianceRecord,
    ModelVersion,
    MonitoringLog,
    SystemMetricSample,
    User,
)

try:  # psutil provides the most accurate cross-platform readings
    import psutil
except ImportError:  # pragma: no cover - dependency is declared in requirements.txt
    psutil = None

logger = logging.getLogger(__name__)

router = APIRouter()

RESOURCES = ("cpu", "memory", "storage", "network")
SAMPLE_RETENTION = timedelta(hours=24)
NETWORK_BASELINE_BYTES_PER_SECOND = 12.5 * 1024 * 1024  # 100 Mbps link

_network_state: Dict[str, float] = {"timestamp": 0.0, "bytes": 0.0}


def _network_utilization() -> float:
    """Estimate network activity as a percentage of a 100 Mbps baseline."""
    if psutil is None:
        return 0.0

    counters = psutil.net_io_counters()
    total = float(counters.bytes_sent + counters.bytes_recv)
    now = time.monotonic()
    previous_time = _network_state["timestamp"]
    previous_total = _network_state["bytes"]
    _network_state.update({"timestamp": now, "bytes": total})

    if previous_time == 0.0:
        return 0.0

    elapsed = max(now - previous_time, 0.001)
    rate = max(total - previous_total, 0.0) / elapsed
    return round(min(100.0, (rate / NETWORK_BASELINE_BYTES_PER_SECOND) * 100.0), 1)


def _read_system_metrics() -> Dict[str, float]:
    """Read current host resource utilization."""
    if psutil is not None:
        try:
            cpu = float(psutil.cpu_percent(interval=0.1))
            memory = float(psutil.virtual_memory().percent)
            storage = float(psutil.disk_usage(str(PROJECT_ROOT)).percent)
            return {
                "cpu": round(cpu, 1),
                "memory": round(memory, 1),
                "storage": round(storage, 1),
                "network": _network_utilization(),
            }
        except Exception:  # pragma: no cover - host-specific psutil failure
            logger.exception("psutil metrics read failed; using fallback")

    load = 0.0
    try:
        import os

        load = os.getloadavg()[0]
    except (AttributeError, OSError):
        pass
    cpu_count = max(1, (psutil.cpu_count() if psutil else 1) or 1)
    usage = shutil.disk_usage(str(PROJECT_ROOT))
    return {
        "cpu": round(min(100.0, (load / cpu_count) * 100.0), 1),
        "memory": 0.0,
        "storage": round((usage.used / usage.total) * 100.0, 1) if usage.total else 0.0,
        "network": 0.0,
    }


def _record_samples(db: Session, values: Dict[str, float]) -> None:
    now = utcnow()
    for resource, value in values.items():
        db.add(SystemMetricSample(resource=resource, value=value, timestamp=now))
    db.query(SystemMetricSample).filter(
        SystemMetricSample.timestamp < now - SAMPLE_RETENTION
    ).delete(synchronize_session=False)
    db.commit()


def _latest_sample_time(db: Session, resource: str) -> Optional[datetime]:
    row = (
        db.query(SystemMetricSample)
        .filter(SystemMetricSample.resource == resource)
        .order_by(SystemMetricSample.timestamp.desc())
        .first()
    )
    return row.timestamp if row else None


def _metric_value(log: MonitoringLog) -> float:
    value = log.metric_value
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        for key in (
            "value",
            "score",
            "accuracy",
            "latency",
            "latency_ms",
            "throughput",
            "error_rate",
        ):
            candidate = value.get(key)
            if isinstance(candidate, (int, float)):
                return float(candidate)
    return 0.0


def _model_status(model: ModelVersion, metrics: Dict[str, float]) -> str:
    if model.status in {"healthy", "degraded", "error"}:
        return model.status
    if metrics["errorRate"] > 0.1 or (metrics["accuracy"] and metrics["accuracy"] < 0.8):
        return "error"
    if metrics["errorRate"] > 0.05 or (metrics["accuracy"] and metrics["accuracy"] < 0.9):
        return "degraded"
    return "healthy"


@router.get("/system")
async def get_system_metrics(
    current_user: User = Security(get_current_active_user, scopes=["user"]),
    db: Session = Depends(get_db),
) -> Any:
    """Current host CPU, memory, storage and relative network activity."""
    values = _read_system_metrics()
    _record_samples(db, values)
    return values


@router.get("/resources/{resource}")
async def get_resource_history(
    resource: str,
    current_user: User = Security(get_current_active_user, scopes=["user"]),
    db: Session = Depends(get_db),
) -> Any:
    """Return up to 120 recent samples for one resource."""
    if resource not in RESOURCES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown resource '{resource}'",
        )

    last = _latest_sample_time(db, resource)
    if last is None or (utcnow() - last).total_seconds() > 5:
        _record_samples(db, {resource: _read_system_metrics()[resource]})

    samples = (
        db.query(SystemMetricSample)
        .filter(SystemMetricSample.resource == resource)
        .order_by(SystemMetricSample.timestamp.desc())
        .limit(120)
        .all()
    )
    return [
        {"timestamp": int(sample.timestamp.timestamp() * 1000), "value": sample.value}
        for sample in reversed(samples)
    ]


def _collect_model_metrics(db: Session) -> Dict[str, float]:
    models = db.query(ModelVersion).all()
    logs = db.query(MonitoringLog).order_by(MonitoringLog.timestamp.desc()).limit(500).all()

    accuracies: List[float] = []
    latencies: List[float] = []
    errors: List[float] = []
    throughputs: List[float] = []
    for log in logs:
        value = _metric_value(log)
        name = log.metric_name.lower()
        if "accuracy" in name:
            accuracies.append(value)
        elif "latency" in name:
            latencies.append(value)
        elif "error" in name:
            errors.append(value)
        elif "throughput" in name:
            throughputs.append(value)

    recent_cutoff = utcnow() - timedelta(minutes=1)
    recent_requests = (
        db.query(MonitoringLog).filter(MonitoringLog.timestamp >= recent_cutoff).count()
    )

    def average(values: List[float]) -> float:
        return round(sum(values) / len(values), 4) if values else 0.0

    return {
        "activeModels": len([m for m in models if (m.status or "").lower() != "retired"]),
        "responseTime": average(latencies),
        "errorRate": average(errors),
        "requestsPerMinute": recent_requests,
        "accuracy": average(accuracies),
        "latency": average(latencies),
        "throughput": average(throughputs),
    }


@router.get("/models/metrics")
async def get_model_metrics(
    current_user: User = Security(get_current_active_user, scopes=["user"]),
    db: Session = Depends(get_db),
) -> Any:
    """Aggregate model metrics derived from registered versions and logs."""
    return _collect_model_metrics(db)


@router.get("/models/performance")
async def get_model_performance(
    current_user: User = Security(get_current_active_user, scopes=["user"]),
    db: Session = Depends(get_db),
) -> Any:
    """Per-model snapshot using the latest monitoring log for each version."""
    models = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).limit(50).all()
    result = []
    for model in models:
        logs = (
            db.query(MonitoringLog)
            .filter(MonitoringLog.version_id == model.id)
            .order_by(MonitoringLog.timestamp.desc())
            .limit(100)
            .all()
        )
        metrics = {"accuracy": 0.0, "latency": 0.0, "throughput": 0.0, "errorRate": 0.0}
        for log in logs:
            name = log.metric_name.lower()
            value = _metric_value(log)
            if "accuracy" in name and not metrics["accuracy"]:
                metrics["accuracy"] = value
            elif "latency" in name and not metrics["latency"]:
                metrics["latency"] = value
            elif "throughput" in name and not metrics["throughput"]:
                metrics["throughput"] = value
            elif "error" in name and not metrics["errorRate"]:
                metrics["errorRate"] = value

        last_updated = logs[0].timestamp if logs else model.created_at
        result.append(
            {
                "modelId": str(model.id),
                "modelName": f"{model.name} v{model.version}",
                "metrics": metrics,
                "status": _model_status(model, metrics),
                "lastUpdated": last_updated.isoformat() if last_updated else None,
            }
        )
    return result


@router.get("/performance")
async def get_performance_history(
    timeRange: str = "24h",
    current_user: User = Security(get_current_active_user, scopes=["user"]),
    db: Session = Depends(get_db),
) -> Any:
    """Return recent accuracy observations as a time series."""
    cutoff = utcnow() - timedelta(hours=24)
    logs = (
        db.query(MonitoringLog)
        .filter(
            MonitoringLog.timestamp >= cutoff,
            MonitoringLog.metric_name.ilike("%accuracy%"),
        )
        .order_by(MonitoringLog.timestamp)
        .limit(500)
        .all()
    )
    return [
        {
            "timestamp": int(log.timestamp.timestamp() * 1000),
            "value": _metric_value(log),
        }
        for log in logs
    ]


@router.get("/alerts")
async def get_alerts(
    current_user: User = Security(get_current_active_user, scopes=["user"]),
    db: Session = Depends(get_db),
) -> Any:
    """Derive alerts from compliance and model state."""
    alerts = []
    for record in db.query(ComplianceRecord).order_by(ComplianceRecord.created_at.desc()).limit(50):
        if record.status in {"non_compliant", "needs_review"}:
            alerts.append(
                {
                    "id": f"compliance-{record.id}",
                    "type": "compliance",
                    "severity": ("high" if record.status == "non_compliant" else "medium"),
                    "message": f"{record.regulation_type} is {record.status.replace('_', ' ')}",
                    "timestamp": record.created_at.isoformat(),
                }
            )
    performance = await get_model_performance(current_user=current_user, db=db)
    for model in performance:
        if model["status"] != "healthy":
            alerts.append(
                {
                    "id": f"model-{model['modelId']}",
                    "type": "model",
                    "severity": "high" if model["status"] == "error" else "medium",
                    "message": f"{model['modelName']} is {model['status']}",
                    "timestamp": model["lastUpdated"],
                }
            )
    return alerts
