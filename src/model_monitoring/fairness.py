import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from sklearn.metrics import confusion_matrix

@dataclass
class FairnessMetrics:
    demographic_parity_diff: float
    equal_opportunity_diff: float
    disparate_impact_ratio: float
    group_fairness_score: float
    individual_fairness_score: float

class FairnessMonitor:
    def __init__(self, protected_attributes: List[str]):
        """
        Initialize FairnessMonitor
        
        Args:
            protected_attributes: List of protected attribute names to monitor
        """
        self.protected_attributes = protected_attributes
        
    def calculate_metrics(self, 
                         predictions: np.ndarray,
                         actual: np.ndarray,
                         protected_features: Dict[str, np.ndarray]) -> FairnessMetrics:
        """
        Calculate comprehensive fairness metrics
        
        Args:
            predictions: Model predictions
            actual: Actual labels
            protected_features: Dict mapping protected attribute names to their values
            
        Returns:
            FairnessMetrics: Calculated fairness metrics
        """
        metrics = FairnessMetrics(
            demographic_parity_diff=self._demographic_parity(predictions, protected_features),
            equal_opportunity_diff=self._equal_opportunity(predictions, actual, protected_features),
            disparate_impact_ratio=self._disparate_impact(predictions, protected_features),
            group_fairness_score=self._group_fairness(predictions, actual, protected_features),
            individual_fairness_score=self._individual_fairness(predictions, protected_features)
        )
        return metrics
    
    def _demographic_parity(self, predictions: np.ndarray, 
                          protected_features: Dict[str, np.ndarray]) -> float:
        """Calculate demographic parity difference"""
        max_diff = 0
        for attr, values in protected_features.items():
            unique_values = np.unique(values)
            if len(unique_values) < 2:
                continue
                
            group_predictions = [predictions[values == val] for val in unique_values]
            group_rates = [np.mean(preds) for preds in group_predictions]
            diff = max(group_rates) - min(group_rates)
            max_diff = max(max_diff, diff)
            
        return max_diff
    
    def _equal_opportunity(self, predictions: np.ndarray, actual: np.ndarray,
                         protected_features: Dict[str, np.ndarray]) -> float:
        """Calculate equal opportunity difference"""
        max_diff = 0
        for attr, values in protected_features.items():
            unique_values = np.unique(values)
            if len(unique_values) < 2:
                continue
                
            tpr_values = []
            for val in unique_values:
                mask = values == val
                tn, fp, fn, tp = confusion_matrix(actual[mask], predictions[mask]).ravel()
                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
                tpr_values.append(tpr)
                
            diff = max(tpr_values) - min(tpr_values)
            max_diff = max(max_diff, diff)
            
        return max_diff
    
    def _disparate_impact(self, predictions: np.ndarray,
                         protected_features: Dict[str, np.ndarray]) -> float:
        """Calculate disparate impact ratio"""
        min_ratio = 1.0
        for attr, values in protected_features.items():
            unique_values = np.unique(values)
            if len(unique_values) < 2:
                continue
                
            group_predictions = [predictions[values == val] for val in unique_values]
            group_rates = [np.mean(preds) for preds in group_predictions]
            ratio = min(group_rates) / max(group_rates) if max(group_rates) > 0 else 1.0
            min_ratio = min(min_ratio, ratio)
            
        return min_ratio
    
    def _group_fairness(self, predictions: np.ndarray, actual: np.ndarray,
                       protected_features: Dict[str, np.ndarray]) -> float:
        """Calculate overall group fairness score"""
        demographic_parity = self._demographic_parity(predictions, protected_features)
        equal_opportunity = self._equal_opportunity(predictions, actual, protected_features)
        disparate_impact = self._disparate_impact(predictions, protected_features)
        
        # Combine metrics into overall score (0-1, higher is better)
        score = 1.0 - (demographic_parity + (1.0 - disparate_impact) + equal_opportunity) / 3.0
        return max(0.0, min(1.0, score))
    
    def _individual_fairness(self, predictions: np.ndarray,
                           protected_features: Dict[str, np.ndarray]) -> float:
        """Calculate individual fairness score using consistency measure"""
        from sklearn.neighbors import NearestNeighbors
        
        # Convert protected features to matrix
        feature_matrix = np.column_stack([values for values in protected_features.values()])
        
        # Find k nearest neighbors for each instance
        k = min(5, len(predictions) - 1)
        nbrs = NearestNeighbors(n_neighbors=k+1).fit(feature_matrix)
        distances, indices = nbrs.kneighbors(feature_matrix)
        
        # Calculate consistency score
        consistency_scores = []
        for i in range(len(predictions)):
            neighbors = indices[i][1:]  # Exclude self
            neighbor_preds = predictions[neighbors]
            consistency = np.mean(neighbor_preds == predictions[i])
            consistency_scores.append(consistency)
            
        return np.mean(consistency_scores)
