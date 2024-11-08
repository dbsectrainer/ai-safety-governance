import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging
from dataclasses import dataclass
from statsmodels.tsa.holtwinters import ExponentialSmoothing

@dataclass
class PredictiveAlert:
    metric_name: str
    current_value: float
    predicted_value: float
    threshold: float
    probability: float
    severity: str
    timestamp: str
    root_cause: Optional[Dict] = None

class RootCauseAnalyzer:
    def __init__(self):
        """Initialize root cause analyzer"""
        self.logger = logging.getLogger(__name__)
        self.correlation_threshold = 0.7
        
    def analyze(self, metrics: Dict[str, np.ndarray], 
                alert_metric: str, alert_time_idx: int) -> Dict:
        """
        Perform root cause analysis
        
        Args:
            metrics: Dictionary of metric name to time series data
            alert_metric: Name of the metric that triggered the alert
            alert_time_idx: Time index when alert occurred
            
        Returns:
            dict: Root cause analysis results
        """
        try:
            # Convert metrics to DataFrame
            df = pd.DataFrame(metrics)
            
            # Calculate correlations
            correlations = df.corr()[alert_metric].abs()
            
            # Find highly correlated metrics
            related_metrics = correlations[
                correlations > self.correlation_threshold
            ].index.tolist()
            
            # Analyze temporal patterns
            temporal_patterns = self._analyze_temporal_patterns(
                df[related_metrics], alert_time_idx
            )
            
            # Identify anomalous metrics
            anomalous_metrics = self._identify_anomalous_metrics(
                df[related_metrics], alert_time_idx
            )
            
            # Combine analyses
            root_causes = {
                'correlated_metrics': related_metrics,
                'temporal_patterns': temporal_patterns,
                'anomalous_metrics': anomalous_metrics,
                'impact_score': self._calculate_impact_scores(
                    df, related_metrics, alert_time_idx
                )
            }
            
            return root_causes
            
        except Exception as e:
            self.logger.error(f"Error in root cause analysis: {str(e)}")
            return {}
            
    def _analyze_temporal_patterns(self, df: pd.DataFrame, 
                                 alert_time_idx: int) -> Dict:
        """Analyze temporal patterns leading to the alert"""
        window_size = min(24, len(df))  # 24 hours or max available
        alert_window = df.iloc[max(0, alert_time_idx - window_size):alert_time_idx + 1]
        
        patterns = {}
        for column in df.columns:
            # Calculate trend
            trend = np.polyfit(range(len(alert_window)), 
                             alert_window[column].values, 1)[0]
            
            # Calculate volatility
            volatility = alert_window[column].std()
            
            # Detect sudden changes
            changes = np.diff(alert_window[column].values)
            max_change = np.max(np.abs(changes))
            
            patterns[column] = {
                'trend': trend,
                'volatility': volatility,
                'max_change': max_change
            }
            
        return patterns
        
    def _identify_anomalous_metrics(self, df: pd.DataFrame, 
                                  alert_time_idx: int) -> Dict:
        """Identify anomalous metrics at alert time"""
        anomalies = {}
        
        # Use Isolation Forest for anomaly detection
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df)
        
        detector = IsolationForest(contamination=0.1, random_state=42)
        detector.fit(scaled_data)
        
        # Get anomaly scores for alert time
        alert_scores = detector.score_samples(
            scaled_data[alert_time_idx:alert_time_idx+1]
        )
        
        for idx, column in enumerate(df.columns):
            anomalies[column] = {
                'anomaly_score': alert_scores[0],
                'is_anomalous': alert_scores[0] < -0.5
            }
            
        return anomalies
        
    def _calculate_impact_scores(self, df: pd.DataFrame, 
                               metrics: List[str], alert_time_idx: int) -> Dict:
        """Calculate impact scores for related metrics"""
        impact_scores = {}
        
        for metric in metrics:
            # Calculate percentage change
            current = df[metric].iloc[alert_time_idx]
            previous = df[metric].iloc[max(0, alert_time_idx - 1)]
            pct_change = (current - previous) / previous if previous != 0 else 0
            
            # Calculate z-score
            mean = df[metric].mean()
            std = df[metric].std()
            z_score = (current - mean) / std if std != 0 else 0
            
            impact_scores[metric] = {
                'percentage_change': pct_change,
                'z_score': z_score,
                'impact_level': 'high' if abs(z_score) > 2 else 'medium' if abs(z_score) > 1 else 'low'
            }
            
        return impact_scores

class PredictiveMonitor:
    def __init__(self, config: Dict):
        """
        Initialize PredictiveMonitor with configuration
        
        Args:
            config: Configuration dictionary containing monitoring settings
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Initialize settings
        self.prediction_window = config.get('prediction_window', 24)  # hours
        self.alert_thresholds = config.get('alert_thresholds', {
            'accuracy': 0.95,
            'latency_ms': 100,
            'error_rate': 0.01
        })
        
        # Initialize components
        self.root_cause_analyzer = RootCauseAnalyzer()
        self.metric_history = {}
        
    def process_metrics(self, current_metrics: Dict[str, float]) -> List[PredictiveAlert]:
        """
        Process current metrics and generate predictive alerts
        
        Args:
            current_metrics: Dictionary of current metric values
            
        Returns:
            List[PredictiveAlert]: List of predicted alerts
        """
        try:
            # Update metric history
            timestamp = datetime.utcnow().isoformat()
            for metric, value in current_metrics.items():
                if metric not in self.metric_history:
                    self.metric_history[metric] = []
                self.metric_history[metric].append((timestamp, value))
                
            # Generate predictions
            predictions = self._generate_predictions()
            
            # Generate alerts
            alerts = self._generate_alerts(predictions)
            
            # Perform root cause analysis for alerts
            for alert in alerts:
                if alert.probability > 0.8:  # High probability alerts
                    alert.root_cause = self.root_cause_analyzer.analyze(
                        self.metric_history,
                        alert.metric_name,
                        -1  # Latest time index
                    )
                    
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error processing metrics: {str(e)}")
            return []
            
    def _generate_predictions(self) -> Dict[str, Tuple[float, float]]:
        """Generate predictions for each metric"""
        predictions = {}
        
        for metric, history in self.metric_history.items():
            if len(history) < 24:  # Need minimum history
                continue
                
            # Extract values
            values = np.array([v for _, v in history])
            
            try:
                # Fit exponential smoothing model
                model = ExponentialSmoothing(
                    values,
                    seasonal_periods=24,  # Daily seasonality
                    trend='add',
                    seasonal='add'
                ).fit()
                
                # Generate prediction
                forecast = model.forecast(1)[0]
                
                # Calculate prediction interval
                residuals = model.resid
                error_std = np.std(residuals)
                prediction_interval = 1.96 * error_std  # 95% confidence
                
                predictions[metric] = (forecast, prediction_interval)
                
            except Exception as e:
                self.logger.warning(f"Error predicting {metric}: {str(e)}")
                continue
                
        return predictions
        
    def _generate_alerts(self, predictions: Dict[str, Tuple[float, float]]) -> List[PredictiveAlert]:
        """Generate alerts based on predictions"""
        alerts = []
        
        for metric, (predicted_value, interval) in predictions.items():
            if metric not in self.alert_thresholds:
                continue
                
            threshold = self.alert_thresholds[metric]
            current_value = self.metric_history[metric][-1][1]
            
            # Calculate probability of threshold violation
            if threshold > predicted_value:
                # Upper threshold
                probability = 1 - stats.norm.cdf(
                    threshold,
                    predicted_value,
                    interval/1.96
                )
            else:
                # Lower threshold
                probability = stats.norm.cdf(
                    threshold,
                    predicted_value,
                    interval/1.96
                )
                
            if probability > 0.3:  # Alert threshold
                severity = 'high' if probability > 0.7 else 'medium' if probability > 0.5 else 'low'
                
                alerts.append(PredictiveAlert(
                    metric_name=metric,
                    current_value=current_value,
                    predicted_value=predicted_value,
                    threshold=threshold,
                    probability=probability,
                    severity=severity,
                    timestamp=datetime.utcnow().isoformat()
                ))
                
        return alerts
