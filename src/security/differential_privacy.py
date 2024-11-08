import numpy as np
from typing import Dict, List, Union, Optional
from dataclasses import dataclass
import logging
from scipy import stats
from abc import ABC, abstractmethod

@dataclass
class PrivacyBudget:
    epsilon: float  # Privacy loss parameter
    delta: float   # Probability of privacy loss exceeding epsilon
    remaining: float  # Remaining privacy budget

class DifferentialPrivacyMechanism(ABC):
    @abstractmethod
    def add_noise(self, data: np.ndarray) -> np.ndarray:
        pass
    
    @abstractmethod
    def get_privacy_cost(self) -> float:
        pass

class LaplaceMechanism(DifferentialPrivacyMechanism):
    def __init__(self, sensitivity: float, epsilon: float):
        """
        Initialize Laplace Mechanism
        
        Args:
            sensitivity: L1 sensitivity of the query
            epsilon: Privacy parameter
        """
        self.sensitivity = sensitivity
        self.epsilon = epsilon
        
    def add_noise(self, data: np.ndarray) -> np.ndarray:
        """Add Laplace noise to the data"""
        scale = self.sensitivity / self.epsilon
        noise = np.random.laplace(0, scale, data.shape)
        return data + noise
        
    def get_privacy_cost(self) -> float:
        """Get privacy cost of the mechanism"""
        return self.epsilon

class GaussianMechanism(DifferentialPrivacyMechanism):
    def __init__(self, sensitivity: float, epsilon: float, delta: float):
        """
        Initialize Gaussian Mechanism
        
        Args:
            sensitivity: L2 sensitivity of the query
            epsilon: Privacy parameter
            delta: Probability of privacy loss exceeding epsilon
        """
        self.sensitivity = sensitivity
        self.epsilon = epsilon
        self.delta = delta
        self.sigma = self._calculate_sigma()
        
    def _calculate_sigma(self) -> float:
        """Calculate standard deviation for Gaussian noise"""
        return self.sensitivity * np.sqrt(2 * np.log(1.25 / self.delta)) / self.epsilon
        
    def add_noise(self, data: np.ndarray) -> np.ndarray:
        """Add Gaussian noise to the data"""
        noise = np.random.normal(0, self.sigma, data.shape)
        return data + noise
        
    def get_privacy_cost(self) -> float:
        """Get privacy cost of the mechanism"""
        return self.epsilon

class ExponentialMechanism(DifferentialPrivacyMechanism):
    def __init__(self, utility_function: callable, sensitivity: float, epsilon: float):
        """
        Initialize Exponential Mechanism
        
        Args:
            utility_function: Function that assigns utility scores to outcomes
            sensitivity: Sensitivity of the utility function
            epsilon: Privacy parameter
        """
        self.utility_function = utility_function
        self.sensitivity = sensitivity
        self.epsilon = epsilon
        
    def add_noise(self, data: np.ndarray) -> np.ndarray:
        """Apply exponential mechanism to select outcomes"""
        utilities = np.array([self.utility_function(x) for x in data])
        probabilities = np.exp(self.epsilon * utilities / (2 * self.sensitivity))
        probabilities = probabilities / np.sum(probabilities)
        
        # Sample from the probability distribution
        indices = np.random.choice(len(data), size=len(data), p=probabilities)
        return data[indices]
        
    def get_privacy_cost(self) -> float:
        """Get privacy cost of the mechanism"""
        return self.epsilon

class DifferentialPrivacy:
    def __init__(self, config: Dict):
        """
        Initialize DifferentialPrivacy with configuration
        
        Args:
            config: Configuration dictionary containing privacy settings
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Initialize privacy budget
        self.privacy_budget = PrivacyBudget(
            epsilon=config.get('epsilon', 1.0),
            delta=config.get('delta', 1e-5),
            remaining=config.get('epsilon', 1.0)
        )
        
        # Initialize mechanisms
        self.mechanisms = {
            'laplace': lambda s, e: LaplaceMechanism(s, e),
            'gaussian': lambda s, e: GaussianMechanism(s, e, self.privacy_budget.delta),
            'exponential': lambda s, e, u: ExponentialMechanism(u, s, e)
        }
        
    def privatize_data(self, data: np.ndarray, mechanism: str,
                      sensitivity: float, utility_function: callable = None) -> np.ndarray:
        """
        Apply differential privacy mechanism to data
        
        Args:
            data: Input data to privatize
            mechanism: Type of mechanism to use ('laplace', 'gaussian', 'exponential')
            sensitivity: Sensitivity of the query
            utility_function: Required for exponential mechanism
            
        Returns:
            np.ndarray: Privatized data
        """
        try:
            # Check privacy budget
            if self.privacy_budget.remaining <= 0:
                raise ValueError("Privacy budget exhausted")
                
            # Create mechanism
            if mechanism == 'exponential' and utility_function is None:
                raise ValueError("Utility function required for exponential mechanism")
                
            dp_mechanism = self._create_mechanism(
                mechanism, sensitivity, self.privacy_budget.remaining, utility_function
            )
            
            # Apply mechanism
            private_data = dp_mechanism.add_noise(data)
            
            # Update privacy budget
            privacy_cost = dp_mechanism.get_privacy_cost()
            self.privacy_budget.remaining -= privacy_cost
            
            self.logger.info(
                f"Applied {mechanism} mechanism. "
                f"Remaining privacy budget: {self.privacy_budget.remaining:.4f}"
            )
            
            return private_data
            
        except Exception as e:
            self.logger.error(f"Error applying differential privacy: {str(e)}")
            raise
            
    def _create_mechanism(self, mechanism: str, sensitivity: float,
                         epsilon: float, utility_function: callable = None) -> DifferentialPrivacyMechanism:
        """Create differential privacy mechanism"""
        if mechanism not in self.mechanisms:
            raise ValueError(f"Unknown mechanism: {mechanism}")
            
        if mechanism == 'exponential':
            return self.mechanisms[mechanism](sensitivity, epsilon, utility_function)
        else:
            return self.mechanisms[mechanism](sensitivity, epsilon)
            
    def compose_mechanisms(self, mechanisms: List[Dict]) -> float:
        """
        Calculate total privacy cost for composed mechanisms
        
        Args:
            mechanisms: List of mechanism configurations
            
        Returns:
            float: Total privacy cost
        """
        total_cost = 0
        for mech in mechanisms:
            dp_mechanism = self._create_mechanism(
                mech['type'],
                mech['sensitivity'],
                mech.get('epsilon', self.privacy_budget.epsilon),
                mech.get('utility_function')
            )
            total_cost += dp_mechanism.get_privacy_cost()
            
        return total_cost
        
    def check_privacy_guarantee(self, epsilon: float, delta: float,
                              num_queries: int) -> bool:
        """
        Check if privacy guarantees hold for multiple queries
        
        Args:
            epsilon: Privacy parameter
            delta: Probability parameter
            num_queries: Number of queries
            
        Returns:
            bool: True if privacy guarantees hold
        """
        # Advanced composition theorem
        composed_epsilon = np.sqrt(2 * num_queries * np.log(1/delta)) * epsilon + \
                         num_queries * epsilon * (np.exp(epsilon) - 1)
        composed_delta = num_queries * delta
        
        return composed_epsilon <= self.privacy_budget.epsilon and \
               composed_delta <= self.privacy_budget.delta
               
    def estimate_sensitivity(self, data: np.ndarray, query_function: callable,
                           num_samples: int = 1000) -> float:
        """
        Estimate sensitivity of a query function
        
        Args:
            data: Input data
            query_function: Function to compute query result
            num_samples: Number of sample pairs to use
            
        Returns:
            float: Estimated sensitivity
        """
        sensitivities = []
        for _ in range(num_samples):
            # Sample two adjacent datasets
            idx = np.random.randint(len(data))
            adjacent_data = data.copy()
            adjacent_data[idx] = np.random.normal(0, 1)  # Modify one record
            
            # Compute query results
            result1 = query_function(data)
            result2 = query_function(adjacent_data)
            
            # Compute sensitivity
            sensitivity = np.abs(result1 - result2)
            sensitivities.append(sensitivity)
            
        return np.max(sensitivities)
