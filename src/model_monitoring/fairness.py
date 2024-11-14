import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

@dataclass
class FairnessMetrics:
    demographic_parity_diff: float
    equal_opportunity_diff: float
    disparate_impact_ratio: float
    group_fairness_score: float
    individual_fairness_score: float
    intersectional_fairness_score: float
    bias_amplification_score: float
    
    def to_dict(self):
        """Convert dataclass to dictionary"""
        return asdict(self)

class IntersectionalFairnessMonitor:
    def __init__(self, protected_attributes: List[str], bias_mitigation_strategy: str = 'reweighting'):
        """
        Initialize IntersectionalFairnessMonitor
        
        Args:
            protected_attributes: List of protected attribute names to monitor
            bias_mitigation_strategy: Strategy for mitigating bias ('reweighting', 'resampling', 'adversarial')
        """
        self.protected_attributes = protected_attributes
        self.bias_mitigation_strategy = bias_mitigation_strategy
        
    def calculate_metrics(self, 
                         predictions: np.ndarray,
                         actual: np.ndarray,
                         features: pd.DataFrame) -> FairnessMetrics:
        """
        Calculate comprehensive intersectional fairness metrics
        
        Args:
            predictions: Model predictions
            actual: Actual labels
            features: DataFrame with protected and other features
            
        Returns:
            FairnessMetrics: Calculated fairness metrics
        """
        # Convert features to dictionary of protected attributes
        protected_features = {attr: features[attr].values for attr in self.protected_attributes}
        
        metrics = FairnessMetrics(
            demographic_parity_diff=self._demographic_parity(predictions, protected_features),
            equal_opportunity_diff=self._equal_opportunity(predictions, actual, protected_features),
            disparate_impact_ratio=self._disparate_impact(predictions, protected_features),
            group_fairness_score=self._group_fairness(predictions, actual, protected_features),
            individual_fairness_score=self._individual_fairness(predictions, protected_features),
            intersectional_fairness_score=self._intersectional_fairness(predictions, actual, features),
            bias_amplification_score=self._bias_amplification(predictions, actual, features)
        )
        return metrics
    
    def _demographic_parity(self, predictions: np.ndarray, 
                          protected_features: Dict[str, np.ndarray]) -> float:
        """Calculate demographic parity difference with intersectional analysis"""
        max_diff = 0
        
        # Single attribute analysis
        for attr, values in protected_features.items():
            unique_values = np.unique(values)
            group_predictions = [predictions[values == val] for val in unique_values]
            group_rates = [np.mean(preds) for preds in group_predictions]
            diff = max(group_rates) - min(group_rates)
            max_diff = max(max_diff, diff)
        
        # Intersectional analysis
        if len(self.protected_attributes) > 1:
            intersectional_groups = self._create_intersectional_groups(protected_features)
            intersectional_rates = [np.mean(predictions[group]) for group in intersectional_groups.values()]
            intersectional_diff = max(intersectional_rates) - min(intersectional_rates)
            max_diff = max(max_diff, intersectional_diff)
        
        return max_diff
    
    def _equal_opportunity(self, predictions: np.ndarray, actual: np.ndarray,
                         protected_features: Dict[str, np.ndarray]) -> float:
        """Calculate equal opportunity difference with intersectional analysis"""
        max_diff = 0
        
        # Single attribute analysis
        for attr, values in protected_features.items():
            unique_values = np.unique(values)
            tpr_values = []
            for val in unique_values:
                mask = values == val
                tn, fp, fn, tp = confusion_matrix(actual[mask], predictions[mask]).ravel()
                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
                tpr_values.append(tpr)
            
            diff = max(tpr_values) - min(tpr_values)
            max_diff = max(max_diff, diff)
        
        # Intersectional analysis
        if len(self.protected_attributes) > 1:
            intersectional_groups = self._create_intersectional_groups(protected_features)
            intersectional_tprs = []
            for group_mask in intersectional_groups.values():
                tn, fp, fn, tp = confusion_matrix(actual[group_mask], predictions[group_mask]).ravel()
                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
                intersectional_tprs.append(tpr)
            
            intersectional_diff = max(intersectional_tprs) - min(intersectional_tprs)
            max_diff = max(max_diff, intersectional_diff)
        
        return max_diff
    
    def _disparate_impact(self, predictions: np.ndarray,
                         protected_features: Dict[str, np.ndarray]) -> float:
        """Calculate disparate impact ratio with intersectional analysis"""
        min_ratio = 1.0
        
        # Single attribute analysis
        for attr, values in protected_features.items():
            unique_values = np.unique(values)
            group_predictions = [predictions[values == val] for val in unique_values]
            group_rates = [np.mean(preds) for preds in group_predictions]
            ratio = min(group_rates) / max(group_rates) if max(group_rates) > 0 else 1.0
            min_ratio = min(min_ratio, ratio)
        
        # Intersectional analysis
        if len(self.protected_attributes) > 1:
            intersectional_groups = self._create_intersectional_groups(protected_features)
            intersectional_rates = [np.mean(predictions[group]) for group in intersectional_groups.values()]
            intersectional_ratio = min(intersectional_rates) / max(intersectional_rates) if max(intersectional_rates) > 0 else 1.0
            min_ratio = min(min_ratio, intersectional_ratio)
        
        return min_ratio
    
    def _create_intersectional_groups(self, protected_features: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Create intersectional groups by combining protected attributes"""
        from itertools import product
        
        intersectional_groups = {}
        attribute_values = [np.unique(values) for values in protected_features.values()]
        
        for combination in product(*attribute_values):
            group_mask = np.ones(len(list(protected_features.values())[0]), dtype=bool)
            for i, val in enumerate(combination):
                group_mask &= (list(protected_features.values())[i] == val)
            
            group_name = '_'.join(map(str, combination))
            intersectional_groups[group_name] = group_mask
        
        return intersectional_groups
    
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
    
    def _intersectional_fairness(self, predictions: np.ndarray, actual: np.ndarray, 
                                features: pd.DataFrame) -> float:
        """Calculate intersectional fairness score"""
        intersectional_groups = self._create_intersectional_groups(
            {attr: features[attr].values for attr in self.protected_attributes}
        )
        
        group_performance = {}
        for group_name, group_mask in intersectional_groups.items():
            group_preds = predictions[group_mask]
            group_actual = actual[group_mask]
            
            # Calculate performance metrics for each group
            group_performance[group_name] = {
                'accuracy': np.mean(group_preds == group_actual),
                'precision': classification_report(group_actual, group_preds, output_dict=True)['weighted avg']['precision'],
                'recall': classification_report(group_actual, group_preds, output_dict=True)['weighted avg']['recall']
            }
        
        # Calculate variance in performance across groups
        performance_metrics = ['accuracy', 'precision', 'recall']
        performance_variances = [
            np.var([group_performance[group][metric] for group in group_performance])
            for metric in performance_metrics
        ]
        
        # Intersectional fairness score: lower variance means more fairness
        return 1.0 - np.mean(performance_variances)
    
    def _bias_amplification(self, predictions: np.ndarray, actual: np.ndarray, 
                           features: pd.DataFrame) -> float:
        """Detect bias amplification across intersectional groups"""
        # Logistic regression to detect bias
        X = features[self.protected_attributes]
        y = (predictions != actual).astype(int)  # Binary: correct or incorrect prediction
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        lr = LogisticRegression(penalty='l2', solver='lbfgs')
        lr.fit(X_scaled, y)
        
        # Coefficient magnitude indicates bias amplification
        bias_amplification_score = np.mean(np.abs(lr.coef_[0]))
        
        return bias_amplification_score
    
    def generate_fairness_report(self, metrics: FairnessMetrics, output_path: Optional[str] = None) -> Dict:
        """
        Generate comprehensive fairness report with visualization
        
        Args:
            metrics: Fairness metrics to report
            output_path: Optional path to save visualization
            
        Returns:
            Dict containing report details
        """
        report = {
            'summary': {
                'demographic_parity_diff': metrics.demographic_parity_diff,
                'equal_opportunity_diff': metrics.equal_opportunity_diff,
                'disparate_impact_ratio': metrics.disparate_impact_ratio,
                'group_fairness_score': metrics.group_fairness_score,
                'individual_fairness_score': metrics.individual_fairness_score,
                'intersectional_fairness_score': metrics.intersectional_fairness_score,
                'bias_amplification_score': metrics.bias_amplification_score
            },
            'recommendations': self._generate_bias_mitigation_recommendations(metrics)
        }
        
        # Visualization
        if output_path:
            plt.figure(figsize=(10, 6))
            metrics_dict = metrics.to_dict()
            sns.barplot(x=list(metrics_dict.keys()), y=list(metrics_dict.values()))
            plt.title('Fairness Metrics Overview')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            report['visualization_path'] = output_path
        
        return report
    
    def _generate_bias_mitigation_recommendations(self, metrics: FairnessMetrics) -> List[str]:
        """Generate recommendations for bias mitigation"""
        recommendations = []
        
        if metrics.demographic_parity_diff > 0.2:
            recommendations.append("High demographic parity difference detected. Consider resampling or reweighting training data.")
        
        if metrics.equal_opportunity_diff > 0.2:
            recommendations.append("Significant equal opportunity disparity. Evaluate model's performance across different groups.")
        
        if metrics.disparate_impact_ratio < 0.8:
            recommendations.append("Disparate impact ratio is low. Implement fairness constraints in model training.")
        
        if metrics.bias_amplification_score > 0.5:
            recommendations.append("High bias amplification detected. Consider adversarial debiasing techniques.")
        
        if metrics.intersectional_fairness_score < 0.7:
            recommendations.append("Low intersectional fairness score. Perform detailed analysis of performance across intersectional groups.")
        
        return recommendations
    
    def apply_bias_mitigation(self, predictions: np.ndarray, features: pd.DataFrame) -> np.ndarray:
        """
        Apply bias mitigation strategy based on selected method
        
        Args:
            predictions: Original model predictions
            features: Features used for bias mitigation
            
        Returns:
            Debiased predictions
        """
        if self.bias_mitigation_strategy == 'reweighting':
            return self._reweighting_mitigation(predictions, features)
        elif self.bias_mitigation_strategy == 'resampling':
            return self._resampling_mitigation(predictions, features)
        elif self.bias_mitigation_strategy == 'adversarial':
            return self._adversarial_mitigation(predictions, features)
        else:
            return predictions
    
    def _reweighting_mitigation(self, predictions: np.ndarray, features: pd.DataFrame) -> np.ndarray:
        """Reweighting-based bias mitigation"""
        # Implement reweighting logic
        # This is a placeholder and should be customized based on specific use case
        return predictions
    
    def _resampling_mitigation(self, predictions: np.ndarray, features: pd.DataFrame) -> np.ndarray:
        """Resampling-based bias mitigation"""
        # Implement resampling logic
        # This is a placeholder and should be customized based on specific use case
        return predictions
    
    def _adversarial_mitigation(self, predictions: np.ndarray, features: pd.DataFrame) -> np.ndarray:
        """Adversarial debiasing"""
        # Implement adversarial debiasing logic
        # This is a placeholder and should be customized based on specific use case
        return predictions
