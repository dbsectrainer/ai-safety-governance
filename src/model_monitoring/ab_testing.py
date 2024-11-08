import numpy as np
from typing import Dict, List, Optional, Union, Callable
from datetime import datetime
import logging
from dataclasses import dataclass
import scipy.stats as stats
from abc import ABC, abstractmethod

@dataclass
class ExperimentResult:
    experiment_id: str
    variant_a: str
    variant_b: str
    metric_name: str
    a_metrics: Dict[str, float]
    b_metrics: Dict[str, float]
    p_value: float
    confidence_level: float
    is_significant: bool
    sample_size: int
    duration_days: int
    recommendation: str

class StatisticalTest(ABC):
    @abstractmethod
    def run_test(self, a_data: np.ndarray, b_data: np.ndarray) -> tuple:
        pass

class TTest(StatisticalTest):
    def run_test(self, a_data: np.ndarray, b_data: np.ndarray) -> tuple:
        """Run Student's t-test"""
        t_stat, p_value = stats.ttest_ind(a_data, b_data)
        return t_stat, p_value

class MannWhitneyTest(StatisticalTest):
    def run_test(self, a_data: np.ndarray, b_data: np.ndarray) -> tuple:
        """Run Mann-Whitney U test"""
        stat, p_value = stats.mannwhitneyu(a_data, b_data)
        return stat, p_value

class ChiSquareTest(StatisticalTest):
    def run_test(self, a_data: np.ndarray, b_data: np.ndarray) -> tuple:
        """Run Chi-square test"""
        contingency = np.array([a_data, b_data])
        chi2, p_value = stats.chi2_contingency(contingency)[:2]
        return chi2, p_value

class ABTestingFramework:
    def __init__(self, config: Dict):
        """
        Initialize AB Testing Framework
        
        Args:
            config: Configuration dictionary containing testing settings
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Initialize settings
        self.min_sample_size = config.get('min_sample_size', 1000)
        self.confidence_level = config.get('confidence_level', 0.95)
        self.max_experiment_days = config.get('max_experiment_days', 30)
        
        # Initialize statistical tests
        self.statistical_tests = {
            'continuous': TTest(),
            'ordinal': MannWhitneyTest(),
            'categorical': ChiSquareTest()
        }
        
        # Track experiments
        self.active_experiments = {}
        self.completed_experiments = {}
        
    def start_experiment(self, experiment_id: str, metric_name: str,
                        metric_type: str = 'continuous') -> Dict:
        """
        Start a new A/B test experiment
        
        Args:
            experiment_id: Unique identifier for the experiment
            metric_name: Name of the metric to test
            metric_type: Type of metric ('continuous', 'ordinal', 'categorical')
            
        Returns:
            dict: Experiment configuration
        """
        if experiment_id in self.active_experiments:
            raise ValueError(f"Experiment {experiment_id} already exists")
            
        experiment = {
            'id': experiment_id,
            'metric_name': metric_name,
            'metric_type': metric_type,
            'start_time': datetime.utcnow(),
            'variant_a': {
                'data': [],
                'metrics': {}
            },
            'variant_b': {
                'data': [],
                'metrics': {}
            },
            'status': 'running'
        }
        
        self.active_experiments[experiment_id] = experiment
        self.logger.info(f"Started experiment: {experiment_id}")
        
        return experiment
        
    def record_observation(self, experiment_id: str, variant: str,
                          value: Union[float, int, str]) -> None:
        """Record an observation for an experiment variant"""
        if experiment_id not in self.active_experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
            
        experiment = self.active_experiments[experiment_id]
        variant_data = experiment[f'variant_{variant.lower()}']['data']
        variant_data.append(value)
        
        # Update metrics
        self._update_metrics(experiment, variant)
        
        # Check if experiment can be concluded
        self._check_experiment_conclusion(experiment_id)
        
    def _update_metrics(self, experiment: Dict, variant: str) -> None:
        """Update metrics for a variant"""
        data = np.array(experiment[f'variant_{variant}']['data'])
        metrics = {
            'count': len(data),
            'mean': np.mean(data) if len(data) > 0 else 0,
            'std': np.std(data) if len(data) > 0 else 0,
            'min': np.min(data) if len(data) > 0 else 0,
            'max': np.max(data) if len(data) > 0 else 0
        }
        experiment[f'variant_{variant}']['metrics'] = metrics
        
    def _check_experiment_conclusion(self, experiment_id: str) -> None:
        """Check if experiment can be concluded"""
        experiment = self.active_experiments[experiment_id]
        
        # Check duration
        duration = (datetime.utcnow() - experiment['start_time']).days
        if duration >= self.max_experiment_days:
            self._conclude_experiment(experiment_id, "Maximum duration reached")
            return
            
        # Check sample size
        a_count = len(experiment['variant_a']['data'])
        b_count = len(experiment['variant_b']['data'])
        if min(a_count, b_count) >= self.min_sample_size:
            self._conclude_experiment(experiment_id, "Minimum sample size reached")
            return
            
    def _conclude_experiment(self, experiment_id: str, reason: str) -> ExperimentResult:
        """Conclude an experiment and compute results"""
        experiment = self.active_experiments[experiment_id]
        
        # Get data
        a_data = np.array(experiment['variant_a']['data'])
        b_data = np.array(experiment['variant_b']['data'])
        
        # Run statistical test
        test = self.statistical_tests[experiment['metric_type']]
        _, p_value = test.run_test(a_data, b_data)
        
        # Calculate results
        is_significant = p_value < (1 - self.confidence_level)
        duration = (datetime.utcnow() - experiment['start_time']).days
        
        # Generate recommendation
        if not is_significant:
            recommendation = "No significant difference. Continue with current version."
        else:
            a_mean = np.mean(a_data)
            b_mean = np.mean(b_data)
            better_variant = 'B' if b_mean > a_mean else 'A'
            recommendation = f"Variant {better_variant} shows significant improvement. Consider implementing this version."
        
        # Create result
        result = ExperimentResult(
            experiment_id=experiment_id,
            variant_a='A',
            variant_b='B',
            metric_name=experiment['metric_name'],
            a_metrics=experiment['variant_a']['metrics'],
            b_metrics=experiment['variant_b']['metrics'],
            p_value=p_value,
            confidence_level=self.confidence_level,
            is_significant=is_significant,
            sample_size=min(len(a_data), len(b_data)),
            duration_days=duration,
            recommendation=recommendation
        )
        
        # Move to completed experiments
        self.completed_experiments[experiment_id] = {
            'experiment': experiment,
            'result': result,
            'conclusion_reason': reason
        }
        del self.active_experiments[experiment_id]
        
        self.logger.info(f"Concluded experiment {experiment_id}: {recommendation}")
        return result
        
    def get_experiment_status(self, experiment_id: str) -> Dict:
        """Get current status of an experiment"""
        if experiment_id in self.active_experiments:
            experiment = self.active_experiments[experiment_id]
            duration = (datetime.utcnow() - experiment['start_time']).days
            
            return {
                'status': 'running',
                'duration_days': duration,
                'variant_a_metrics': experiment['variant_a']['metrics'],
                'variant_b_metrics': experiment['variant_b']['metrics'],
                'sample_sizes': {
                    'a': len(experiment['variant_a']['data']),
                    'b': len(experiment['variant_b']['data'])
                }
            }
        elif experiment_id in self.completed_experiments:
            completed = self.completed_experiments[experiment_id]
            return {
                'status': 'completed',
                'result': vars(completed['result']),
                'conclusion_reason': completed['conclusion_reason']
            }
        else:
            raise ValueError(f"Experiment {experiment_id} not found")
            
    def list_experiments(self) -> Dict[str, List[str]]:
        """List all experiments"""
        return {
            'active': list(self.active_experiments.keys()),
            'completed': list(self.completed_experiments.keys())
        }
