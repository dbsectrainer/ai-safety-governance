"""
AI Bill of Materials (AIBOM) Tracking System (2025)

Implements comprehensive tracking of AI system components, dependencies,
and supply chain for security, compliance, and transparency.

Aligned with supply chain security best practices and emerging AIBOM standards.
"""

import typing
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import hashlib
import logging


class ComponentType(Enum):
    """Types of AI system components"""
    MODEL = "model"
    DATASET = "dataset"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    TOOL = "tool"
    API = "api"
    HARDWARE = "hardware"
    PLUGIN = "plugin"


class LicenseType(Enum):
    """Common license types"""
    MIT = "MIT"
    APACHE_2 = "Apache-2.0"
    GPL_3 = "GPL-3.0"
    BSD_3 = "BSD-3-Clause"
    PROPRIETARY = "Proprietary"
    CUSTOM = "Custom"
    UNKNOWN = "Unknown"


@dataclass
class Vulnerability:
    """Known vulnerability in a component"""
    cve_id: typing.Optional[str]
    severity: str  # critical, high, medium, low
    description: str
    affected_versions: typing.List[str]
    patched_version: typing.Optional[str]
    disclosure_date: str


@dataclass
class Component:
    """Individual component in AI system"""
    component_id: str
    name: str
    version: str
    component_type: ComponentType
    supplier: str
    license: LicenseType
    source_url: typing.Optional[str] = None
    hash_sha256: typing.Optional[str] = None
    description: typing.Optional[str] = None
    dependencies: typing.List[str] = field(default_factory=list)
    vulnerabilities: typing.List[Vulnerability] = field(default_factory=list)
    metadata: typing.Dict[str, typing.Any] = field(default_factory=dict)
    added_date: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TrainingDataset:
    """Training dataset component with provenance"""
    dataset_id: str
    name: str
    version: str
    source: str
    size_gb: float
    num_samples: int
    data_types: typing.List[str]
    collection_date: str
    geographic_origin: typing.List[str]
    sensitive_data: bool
    privacy_compliance: typing.List[str]  # GDPR, CCPA, etc.
    copyright_status: str
    license: LicenseType
    preprocessing: typing.List[str]
    quality_metrics: typing.Dict[str, float]
    metadata: typing.Dict[str, typing.Any] = field(default_factory=dict)


@dataclass
class ModelProvenance:
    """Model development provenance"""
    base_model: typing.Optional[str]
    training_framework: str
    training_start_date: str
    training_end_date: str
    training_duration_hours: float
    compute_platform: str
    total_flops: typing.Optional[float]
    energy_kwh: typing.Optional[float]
    carbon_kg_co2: typing.Optional[float]
    training_datasets: typing.List[str]  # Dataset IDs
    developers: typing.List[str]
    organization: str


@dataclass
class AIBOM:
    """
    AI Bill of Materials

    Complete inventory of components, dependencies, and provenance
    for an AI system
    """
    bom_id: str
    system_name: str
    system_version: str
    creation_date: str
    last_updated: str
    organization: str

    # Core components
    model_component: typing.Optional[Component] = None
    model_provenance: typing.Optional[ModelProvenance] = None

    # Dependencies
    frameworks: typing.List[Component] = field(default_factory=list)
    libraries: typing.List[Component] = field(default_factory=list)
    datasets: typing.List[TrainingDataset] = field(default_factory=list)
    tools: typing.List[Component] = field(default_factory=list)
    apis: typing.List[Component] = field(default_factory=list)
    hardware: typing.List[Component] = field(default_factory=list)

    # Security
    total_vulnerabilities: int = 0
    critical_vulnerabilities: int = 0
    high_vulnerabilities: int = 0

    # Compliance
    licenses: typing.List[str] = field(default_factory=list)
    compliance_tags: typing.List[str] = field(default_factory=list)

    # Metadata
    metadata: typing.Dict[str, typing.Any] = field(default_factory=dict)


class AIBOMManager:
    """
    AI Bill of Materials Management System

    Manages creation, tracking, and analysis of AI system BOMs
    """

    def __init__(self, output_dir: str = 'aibom_reports'):
        """
        Initialize AIBOM Manager

        :param output_dir: Directory for AIBOM reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger('aibom_manager')
        self.logger.setLevel(logging.INFO)

        self.boms: typing.Dict[str, AIBOM] = {}

    def create_bom(self, system_name: str, system_version: str,
                   organization: str) -> AIBOM:
        """
        Create new AI Bill of Materials

        :param system_name: Name of AI system
        :param system_version: Version of AI system
        :param organization: Organization name
        :return: New AIBOM
        """
        bom_id = self._generate_bom_id(system_name, system_version)
        timestamp = datetime.now().isoformat()

        bom = AIBOM(
            bom_id=bom_id,
            system_name=system_name,
            system_version=system_version,
            creation_date=timestamp,
            last_updated=timestamp,
            organization=organization
        )

        self.boms[bom_id] = bom
        self.logger.info(f"Created AIBOM {bom_id} for {system_name} v{system_version}")

        return bom

    def _generate_bom_id(self, system_name: str, system_version: str) -> str:
        """Generate unique BOM ID"""
        content = f"{system_name}_{system_version}_{datetime.now().isoformat()}"
        return f"AIBOM-{hashlib.md5(content.encode()).hexdigest()[:16]}"

    def add_model_component(self, bom_id: str, model_info: dict):
        """Add model component to BOM"""
        if bom_id not in self.boms:
            raise ValueError(f"BOM {bom_id} not found")

        component = Component(
            component_id=model_info.get('component_id', self._generate_component_id()),
            name=model_info['name'],
            version=model_info['version'],
            component_type=ComponentType.MODEL,
            supplier=model_info.get('supplier', 'Internal'),
            license=LicenseType[model_info.get('license', 'UNKNOWN')],
            source_url=model_info.get('source_url'),
            hash_sha256=model_info.get('hash'),
            description=model_info.get('description'),
            metadata=model_info.get('metadata', {})
        )

        self.boms[bom_id].model_component = component
        self.boms[bom_id].last_updated = datetime.now().isoformat()

        self.logger.info(f"Added model component to BOM {bom_id}")

    def add_model_provenance(self, bom_id: str, provenance_info: dict):
        """Add model provenance information"""
        if bom_id not in self.boms:
            raise ValueError(f"BOM {bom_id} not found")

        provenance = ModelProvenance(
            base_model=provenance_info.get('base_model'),
            training_framework=provenance_info['training_framework'],
            training_start_date=provenance_info['training_start_date'],
            training_end_date=provenance_info['training_end_date'],
            training_duration_hours=provenance_info['training_duration_hours'],
            compute_platform=provenance_info['compute_platform'],
            total_flops=provenance_info.get('total_flops'),
            energy_kwh=provenance_info.get('energy_kwh'),
            carbon_kg_co2=provenance_info.get('carbon_kg_co2'),
            training_datasets=provenance_info.get('training_datasets', []),
            developers=provenance_info.get('developers', []),
            organization=provenance_info['organization']
        )

        self.boms[bom_id].model_provenance = provenance
        self.boms[bom_id].last_updated = datetime.now().isoformat()

    def add_framework(self, bom_id: str, framework_info: dict):
        """Add framework dependency"""
        self._add_component(bom_id, framework_info, ComponentType.FRAMEWORK, 'frameworks')

    def add_library(self, bom_id: str, library_info: dict):
        """Add library dependency"""
        self._add_component(bom_id, library_info, ComponentType.LIBRARY, 'libraries')

    def add_dataset(self, bom_id: str, dataset_info: dict):
        """Add training dataset"""
        if bom_id not in self.boms:
            raise ValueError(f"BOM {bom_id} not found")

        dataset = TrainingDataset(
            dataset_id=dataset_info.get('dataset_id', self._generate_component_id()),
            name=dataset_info['name'],
            version=dataset_info['version'],
            source=dataset_info['source'],
            size_gb=dataset_info['size_gb'],
            num_samples=dataset_info['num_samples'],
            data_types=dataset_info.get('data_types', []),
            collection_date=dataset_info['collection_date'],
            geographic_origin=dataset_info.get('geographic_origin', []),
            sensitive_data=dataset_info.get('sensitive_data', False),
            privacy_compliance=dataset_info.get('privacy_compliance', []),
            copyright_status=dataset_info.get('copyright_status', 'Unknown'),
            license=LicenseType[dataset_info.get('license', 'UNKNOWN')],
            preprocessing=dataset_info.get('preprocessing', []),
            quality_metrics=dataset_info.get('quality_metrics', {}),
            metadata=dataset_info.get('metadata', {})
        )

        self.boms[bom_id].datasets.append(dataset)
        self.boms[bom_id].last_updated = datetime.now().isoformat()

    def add_tool(self, bom_id: str, tool_info: dict):
        """Add tool dependency"""
        self._add_component(bom_id, tool_info, ComponentType.TOOL, 'tools')

    def add_api(self, bom_id: str, api_info: dict):
        """Add API dependency"""
        self._add_component(bom_id, api_info, ComponentType.API, 'apis')

    def _add_component(self, bom_id: str, component_info: dict,
                      component_type: ComponentType, collection_name: str):
        """Generic method to add component"""
        if bom_id not in self.boms:
            raise ValueError(f"BOM {bom_id} not found")

        component = Component(
            component_id=component_info.get('component_id', self._generate_component_id()),
            name=component_info['name'],
            version=component_info['version'],
            component_type=component_type,
            supplier=component_info.get('supplier', 'Unknown'),
            license=LicenseType[component_info.get('license', 'UNKNOWN')],
            source_url=component_info.get('source_url'),
            hash_sha256=component_info.get('hash'),
            description=component_info.get('description'),
            dependencies=component_info.get('dependencies', []),
            metadata=component_info.get('metadata', {})
        )

        collection = getattr(self.boms[bom_id], collection_name)
        collection.append(component)
        self.boms[bom_id].last_updated = datetime.now().isoformat()

    def _generate_component_id(self) -> str:
        """Generate unique component ID"""
        return f"COMP-{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12]}"

    def scan_vulnerabilities(self, bom_id: str) -> dict:
        """
        Scan BOM for known vulnerabilities

        :param bom_id: BOM identifier
        :return: Vulnerability scan results
        """
        if bom_id not in self.boms:
            raise ValueError(f"BOM {bom_id} not found")

        bom = self.boms[bom_id]
        results = {
            'bom_id': bom_id,
            'scan_date': datetime.now().isoformat(),
            'total_components': 0,
            'vulnerable_components': 0,
            'vulnerabilities_by_severity': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'vulnerabilities': []
        }

        # Scan all component types
        all_components = (
            ([bom.model_component] if bom.model_component else []) +
            bom.frameworks + bom.libraries + bom.tools + bom.apis
        )

        results['total_components'] = len(all_components)

        for component in all_components:
            if component.vulnerabilities:
                results['vulnerable_components'] += 1

                for vuln in component.vulnerabilities:
                    results['vulnerabilities_by_severity'][vuln.severity] += 1
                    results['vulnerabilities'].append({
                        'component': component.name,
                        'version': component.version,
                        'vulnerability': asdict(vuln)
                    })

        # Update BOM statistics
        bom.total_vulnerabilities = len(results['vulnerabilities'])
        bom.critical_vulnerabilities = results['vulnerabilities_by_severity']['critical']
        bom.high_vulnerabilities = results['vulnerabilities_by_severity']['high']

        self.logger.info(
            f"Vulnerability scan complete for {bom_id}: "
            f"{results['total_vulnerabilities']} vulnerabilities found"
        )

        return results

    def analyze_licenses(self, bom_id: str) -> dict:
        """
        Analyze license compliance

        :param bom_id: BOM identifier
        :return: License analysis results
        """
        if bom_id not in self.boms:
            raise ValueError(f"BOM {bom_id} not found")

        bom = self.boms[bom_id]
        all_components = (
            ([bom.model_component] if bom.model_component else []) +
            bom.frameworks + bom.libraries + bom.tools + bom.apis
        )

        license_counts = {}
        for component in all_components:
            license_name = component.license.value
            license_counts[license_name] = license_counts.get(license_name, 0) + 1

        # Add dataset licenses
        for dataset in bom.datasets:
            license_name = dataset.license.value
            license_counts[license_name] = license_counts.get(license_name, 0) + 1

        # Update BOM licenses
        bom.licenses = list(license_counts.keys())

        results = {
            'bom_id': bom_id,
            'analysis_date': datetime.now().isoformat(),
            'total_components': len(all_components) + len(bom.datasets),
            'license_distribution': license_counts,
            'compliance_concerns': self._identify_license_conflicts(license_counts)
        }

        return results

    def _identify_license_conflicts(self, license_counts: dict) -> typing.List[str]:
        """Identify potential license conflicts"""
        concerns = []

        # Check for GPL conflicts with proprietary
        if 'GPL-3.0' in license_counts and 'Proprietary' in license_counts:
            concerns.append(
                "GPL and proprietary licenses detected - potential compatibility issue"
            )

        # Check for unknown licenses
        if license_counts.get('Unknown', 0) > 0:
            concerns.append(
                f"{license_counts['Unknown']} components with unknown licenses"
            )

        return concerns

    def export_bom(self, bom_id: str, format: str = 'json') -> Path:
        """
        Export BOM to file

        :param bom_id: BOM identifier
        :param format: Export format (json, cyclonedx, spdx)
        :return: Path to exported file
        """
        if bom_id not in self.boms:
            raise ValueError(f"BOM {bom_id} not found")

        bom = self.boms[bom_id]

        if format == 'json':
            return self._export_json(bom)
        elif format == 'cyclonedx':
            return self._export_cyclonedx(bom)
        elif format == 'spdx':
            return self._export_spdx(bom)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_json(self, bom: AIBOM) -> Path:
        """Export BOM as JSON"""
        filename = f"{bom.bom_id}_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = self.output_dir / filename

        # Convert to dict
        bom_dict = asdict(bom)

        # Convert enums to strings
        def enum_to_str(obj):
            if isinstance(obj, dict):
                return {k: enum_to_str(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [enum_to_str(item) for item in obj]
            elif isinstance(obj, Enum):
                return obj.value
            return obj

        bom_dict = enum_to_str(bom_dict)

        with open(filepath, 'w') as f:
            json.dump(bom_dict, f, indent=2)

        self.logger.info(f"Exported BOM to {filepath}")
        return filepath

    def _export_cyclonedx(self, bom: AIBOM) -> Path:
        """Export BOM in CycloneDX format"""
        # Simplified CycloneDX export
        # In production, use the official cyclonedx-python-lib
        filename = f"{bom.bom_id}_cyclonedx_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = self.output_dir / filename

        cyclonedx_bom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "component": {
                    "type": "machine-learning-model",
                    "name": bom.system_name,
                    "version": bom.system_version
                }
            },
            "components": []
        }

        # Add all components
        all_components = (
            ([bom.model_component] if bom.model_component else []) +
            bom.frameworks + bom.libraries + bom.tools + bom.apis
        )

        for comp in all_components:
            cyclonedx_bom["components"].append({
                "type": "library",
                "name": comp.name,
                "version": comp.version,
                "licenses": [{"license": {"id": comp.license.value}}]
            })

        with open(filepath, 'w') as f:
            json.dump(cyclonedx_bom, f, indent=2)

        self.logger.info(f"Exported CycloneDX BOM to {filepath}")
        return filepath

    def _export_spdx(self, bom: AIBOM) -> Path:
        """Export BOM in SPDX format"""
        # Simplified SPDX export
        filename = f"{bom.bom_id}_spdx_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = self.output_dir / filename

        spdx_doc = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": f"{bom.system_name}-{bom.system_version}",
            "documentNamespace": f"https://example.com/aibom/{bom.bom_id}",
            "creationInfo": {
                "created": bom.creation_date,
                "creators": [f"Organization: {bom.organization}"]
            },
            "packages": []
        }

        # Add packages
        all_components = (
            ([bom.model_component] if bom.model_component else []) +
            bom.frameworks + bom.libraries + bom.tools + bom.apis
        )

        for idx, comp in enumerate(all_components):
            spdx_doc["packages"].append({
                "SPDXID": f"SPDXRef-Package-{idx}",
                "name": comp.name,
                "versionInfo": comp.version,
                "licenseConcluded": comp.license.value,
                "downloadLocation": comp.source_url or "NOASSERTION"
            })

        with open(filepath, 'w') as f:
            json.dump(spdx_doc, f, indent=2)

        self.logger.info(f"Exported SPDX BOM to {filepath}")
        return filepath


def main():
    """Example usage"""
    manager = AIBOMManager()

    # Create BOM
    bom = manager.create_bom(
        system_name="GPT-Style Model",
        system_version="1.0.0",
        organization="Example AI Labs"
    )

    # Add model component
    manager.add_model_component(bom.bom_id, {
        'name': 'gpt-style-model',
        'version': '1.0.0',
        'license': 'MIT',
        'description': 'Transformer-based language model'
    })

    # Add framework
    manager.add_framework(bom.bom_id, {
        'name': 'PyTorch',
        'version': '2.1.0',
        'supplier': 'Meta',
        'license': 'BSD_3'
    })

    # Add library
    manager.add_library(bom.bom_id, {
        'name': 'transformers',
        'version': '4.35.0',
        'supplier': 'Hugging Face',
        'license': 'APACHE_2'
    })

    # Add dataset
    manager.add_dataset(bom.bom_id, {
        'name': 'WebText',
        'version': '1.0',
        'source': 'Internet',
        'size_gb': 40.0,
        'num_samples': 8000000,
        'collection_date': '2024-01-01',
        'sensitive_data': False,
        'privacy_compliance': ['GDPR', 'CCPA'],
        'copyright_status': 'Mixed',
        'license': 'CUSTOM'
    })

    # Scan vulnerabilities
    vuln_results = manager.scan_vulnerabilities(bom.bom_id)
    print(f"Vulnerabilities found: {vuln_results['total_vulnerabilities']}")

    # Analyze licenses
    license_results = manager.analyze_licenses(bom.bom_id)
    print(f"License distribution: {license_results['license_distribution']}")

    # Export BOM
    exported_path = manager.export_bom(bom.bom_id, format='json')
    print(f"BOM exported to: {exported_path}")


if __name__ == '__main__':
    main()
