import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
import scipy.stats as stats
import networkx as nx

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
    causal_explanation: Optional[Dict] = None

class AdvancedRootCauseAnalyzer:
    def __init__(self, correlation_threshold: float = 0.7):
        """
        Initialize advanced root cause analyzer with causal inference capabilities
        
        Args:
            correlation_threshold: Minimum correlation to consider metrics related
        """
        self.logger = logging.getLogger(__name__)
        self.correlation_threshold = correlation_threshold
        
    def analyze(self, metrics: Dict[str, np.ndarray], 
                alert_metric: str, 
                alert_time_idx: int) -> Dict:
        """
        Perform advanced root cause analysis with causal inference
        
        Args:
            metrics: Dictionary of metric name to time series data
            alert_metric: Name of the metric that triggered the alert
            alert_time_idx: Time index when alert occurred
            
        Returns:
            dict: Comprehensive root cause analysis results
        """
        try:
            # Convert metrics to DataFrame
            df = pd.DataFrame(metrics)
            
            # Correlation and Dependency Analysis
            correlation_analysis = self._correlation_analysis(df, alert_metric)
            
            # Causal Graph Construction
            causal_graph = self._construct_causal_graph(df, correlation_analysis)
            
            # Advanced Anomaly Detection
            anomaly_analysis = self._advanced_anomaly_detection(df, alert_metric, alert_time_idx)
            
            # Machine Learning Causal Inference
            ml_causal_inference = self._ml_causal_inference(df, alert_metric, alert_time_idx)
            
            root_causes = {
                'correlation_analysis': correlation_analysis,
                'causal_graph': nx.to_dict_of_dicts(causal_graph),
                'anomaly_analysis': anomaly_analysis,
                'ml_causal_inference': ml_causal_inference
            }
            
            return root_causes
        
        except Exception as e:
            self.logger.error(f"Advanced root cause analysis error: {str(e)}")
            return {}
    
    def _correlation_analysis(self, df: pd.DataFrame, alert_metric: str) -> Dict:
        """Perform advanced correlation analysis"""
        correlations = df.corr()[alert_metric].abs()
        related_metrics = correlations[correlations > self.correlation_threshold].index.tolist()
        
        return {
            'related_metrics': related_metrics,
            'correlation_matrix': correlations.to_dict()
        }
    
    def _construct_causal_graph(self, df: pd.DataFrame, correlation_analysis: Dict) -> nx.DiGraph:
        """Construct a causal graph based on correlations"""
        G = nx.DiGraph()
        
        for metric in correlation_analysis['related_metrics']:
            G.add_node(metric)
        
        for source in correlation_analysis['related_metrics']:
            for target in correlation_analysis['related_metrics']:
                if source != target:
                    correlation = abs(df[source].corr(df[target]))
                    if correlation > 0.5:
                        G.add_edge(source, target, weight=correlation)
        
        return G
    
    def _advanced_anomaly_detection(self, df: pd.DataFrame, alert_metric: str, alert_time_idx: int) -> Dict:
        """Perform advanced anomaly detection with multiple techniques"""
        anomalies = {}
        
        # Isolation Forest
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        scaled_data = StandardScaler().fit_transform(df)
        iso_forest.fit(scaled_data)
        
        # Z-Score Method
        z_scores = np.abs((df[alert_metric] - df[alert_metric].mean()) / df[alert_metric].std())
        
        # Robust Scaling Anomaly Detection
        robust_scaler = RobustScaler()
        robust_scaled_data = robust_scaler.fit_transform(df[[alert_metric]])
        
        anomalies = {
            'isolation_forest_anomaly': iso_forest.predict(scaled_data[alert_time_idx:alert_time_idx+1])[0] == -1,
            'z_score_anomaly': z_scores[alert_time_idx] > 3,
            'robust_scaled_anomaly': np.abs(robust_scaled_data[alert_time_idx]) > 2.5
        }
        
        return anomalies
    
    def _ml_causal_inference(self, df: pd.DataFrame, alert_metric: str, alert_time_idx: int) -> Dict:
        """Perform machine learning-based causal inference"""
        causal_inference = {}
        
        # Prepare data
        X = df.drop(columns=[alert_metric])
        y = df[alert_metric]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Random Forest for feature importance
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        
        # Predict and evaluate
        y_pred = rf_model.predict(X_test)
        
        causal_inference = {
            'feature_importances': dict(zip(X.columns, rf_model.feature_importances_)),
            'model_performance': {
                'mae': mean_absolute_error(y_test, y_pred),
                'mse': mean_squared_error(y_test, y_pred)
            },
            'most_important_features': sorted(
                zip(X.columns, rf_model.feature_importances_), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
        }
        
        return causal_inference

class PredictiveMonitor:
    def __init__(self, config: Dict):
        """
        Initialize PredictiveMonitor with enhanced configuration
        
        Args:
            config: Configuration dictionary containing monitoring settings
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Enhanced settings
        self.prediction_window = config.get('prediction_window', 24)  # hours
        self.alert_thresholds = config.get('alert_thresholds', {
            'accuracy': 0.95,
            'latency_ms': 100,
            'error_rate': 0.01
        })
        
        # Initialize advanced components
        self.root_cause_analyzer = AdvancedRootCauseAnalyzer()
        self.metric_history = {}
        self.forecasting_models = {
            'exponential_smoothing': self._exponential_smoothing_forecast,
            'seasonal_decomposition': self._seasonal_decomposition_forecast
        }
        
    def process_metrics(self, current_metrics: Dict[str, float]) -> List[PredictiveAlert]:
        """
        Process current metrics with enhanced predictive capabilities
        
        Args:
            current_metrics: Dictionary of current metric values
            
        Returns:
            List[PredictiveAlert]: List of predicted alerts with advanced insights
        """
        try:
            # Update metric history
            timestamp = datetime.utcnow().isoformat()
            for metric, value in current_metrics.items():
                if metric not in self.metric_history:
                    self.metric_history[metric] = []
                self.metric_history[metric].append((timestamp, value))
                
            # Generate multi-model predictions
            predictions = self._generate_multi_model_predictions()
            
            # Generate alerts
            alerts = self._generate_alerts(predictions)
            
            # Perform advanced root cause analysis for high-probability alerts
            for alert in alerts:
                if alert.probability > 0.8:  # High probability alerts
                    alert.root_cause = self.root_cause_analyzer.analyze(
                        {k: np.array([v for _, v in h]) for k, h in self.metric_history.items()},
                        alert.metric_name,
                        -1  # Latest time index
                    )
                    
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error processing metrics: {str(e)}")
            return []
            
    def _generate_multi_model_predictions(self) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """Generate predictions using multiple forecasting models"""
        predictions = {}
        
        for metric, history in self.metric_history.items():
            if len(history) < 24:  # Need minimum history
                continue
                
            # Extract values
            values = np.array([v for _, v in history])
            
            metric_predictions = {}
            for model_name, forecast_func in self.forecasting_models.items():
                try:
                    prediction, interval = forecast_func(values)
                    metric_predictions[model_name] = (prediction, interval)
                except Exception as e:
                    self.logger.warning(f"Error in {model_name} for {metric}: {str(e)}")
            
            predictions[metric] = metric_predictions
                
        return predictions
        
    def _exponential_smoothing_forecast(self, values: np.ndarray) -> Tuple[float, float]:
        """Exponential smoothing forecast method"""
        model = ExponentialSmoothing(
            values,
            seasonal_periods=24,  # Daily seasonality
            trend='add',
            seasonal='add'
        ).fit()
        
        forecast = model.forecast(1)[0]
        residuals = model.resid
        error_std = np.std(residuals)
        prediction_interval = 1.96 * error_std  # 95% confidence
        
        return forecast, prediction_interval
    
    def _seasonal_decomposition_forecast(self, values: np.ndarray) -> Tuple[float, float]:
        """Seasonal decomposition forecast method"""
        decomposition = seasonal_decompose(values, period=24)
        
        # Simple forecast based on trend and seasonal components
        trend_forecast = np.polyval(np.polyfit(range(len(decomposition.trend)), decomposition.trend, 1), len(decomposition.trend))
        seasonal_forecast = decomposition.seasonal[-24:].mean()
        
        forecast = trend_forecast + seasonal_forecast
        
        # Estimate prediction interval
        residuals = values - (decomposition.trend + decomposition.seasonal + decomposition.resid)
        prediction_interval = 1.96 * np.std(residuals)
        
        return forecast, prediction_interval
        
    def _generate_alerts(self, predictions: Dict[str, Dict[str, Tuple[float, float]]]) -> List[PredictiveAlert]:
        """Generate alerts based on multi-model predictions"""
        alerts = []
        
        for metric, model_predictions in predictions.items():
            if metric not in self.alert_thresholds:
                continue
                
            threshold = self.alert_thresholds[metric]
            current_value = self.metric_history[metric][-1][1]
            
            # Consensus prediction
            predicted_values = [pred for model_pred in model_predictions.values() for pred in model_pred]
            consensus_prediction = np.mean(predicted_values)
            consensus_interval = np.std(predicted_values)
            
            # Calculate probability of threshold violation
            if threshold > consensus_prediction:
                # Upper threshold
                probability = 1 - stats.norm.cdf(
                    threshold,
                    consensus_prediction,
                    consensus_interval
                )
            else:
                # Lower threshold
                probability = stats.norm.cdf(
                    threshold,
                    consensus_prediction,
                    consensus_interval
                )
                
            if probability > 0.3:  # Alert threshold
                severity = 'high' if probability > 0.7 else 'medium' if probability > 0.5 else 'low'
                
                alerts.append(PredictiveAlert(
                    metric_name=metric,
                    current_value=current_value,
                    predicted_value=consensus_prediction,
                    threshold=threshold,
                    probability=probability,
                    severity=severity,
                    timestamp=datetime.utcnow().isoformat()
                ))
                
        return alerts
