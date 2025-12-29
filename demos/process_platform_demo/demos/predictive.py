"""
Predictive Analytics Demo
Using scikit-learn and XGBoost for process prediction
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import classification_report, accuracy_score, mean_absolute_error
import warnings
import logging

warnings.filterwarnings('ignore')

# Setup logging
logger = logging.getLogger(__name__)


class ProcessPredictor:
    """
    Demonstrates predictive process monitoring capabilities.
    
    Capabilities:
    1. Outcome Prediction - Will the case complete successfully?
    2. Next Activity Prediction - What activity comes next?
    3. Remaining Time Prediction - How long until completion?
    """
    
    def __init__(self):
        self.outcome_model = None
        self.next_activity_model = None
        self.time_model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.activity_encoder = LabelEncoder()
    
    def prepare_features(self, event_log: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from event log for ML training.
        Creates prefix-based features (what has happened so far in the case).
        """
        features_list = []
        
        for case_id, case_events in event_log.groupby('case_id'):
            case_events = case_events.sort_values('timestamp')
            activities = case_events['activity'].tolist()
            
            # Get case-level attributes
            first_event = case_events.iloc[0]
            order_value = first_event.get('order_value', 0)
            priority = first_event.get('priority', 'Medium')
            region = first_event.get('region', 'Unknown')
            
            # Calculate case duration
            start_time = case_events['timestamp'].min()
            end_time = case_events['timestamp'].max()
            total_duration = (end_time - start_time).total_seconds() / 3600  # hours
            
            # Determine outcome (completed if Payment Received exists)
            completed = 'Payment Received' in activities
            
            # Create prefix features for each step
            for i in range(1, len(activities)):
                prefix = activities[:i]
                next_activity = activities[i]
                
                # Calculate remaining time from this point
                remaining_time = (end_time - case_events.iloc[i-1]['timestamp']).total_seconds() / 3600
                
                features_list.append({
                    'case_id': case_id,
                    'prefix_length': len(prefix),
                    'current_activity': prefix[-1],
                    'order_value': order_value,
                    'priority': priority,
                    'region': region,
                    'num_unique_activities': len(set(prefix)),
                    'has_deviation': any(a in prefix for a in ['Manual Review', 'Backorder', 'Credit Rejected']),
                    'next_activity': next_activity,
                    'remaining_time': remaining_time,
                    'completed': completed
                })
        
        return pd.DataFrame(features_list)
    
    def encode_features(self, df: pd.DataFrame, fit: bool = True) -> np.ndarray:
        """Encode categorical features for ML."""
        df_encoded = df.copy()
        
        categorical_cols = ['current_activity', 'priority', 'region']
        
        for col in categorical_cols:
            if fit:
                self.label_encoders[col] = LabelEncoder()
                df_encoded[col] = self.label_encoders[col].fit_transform(df_encoded[col].astype(str))
            else:
                df_encoded[col] = self.label_encoders[col].transform(df_encoded[col].astype(str))
        
        df_encoded['has_deviation'] = df_encoded['has_deviation'].astype(int)
        
        feature_cols = ['prefix_length', 'current_activity', 'order_value', 
                       'priority', 'region', 'num_unique_activities', 'has_deviation']
        
        X = df_encoded[feature_cols].values
        
        if fit:
            X = self.scaler.fit_transform(X)
        else:
            X = self.scaler.transform(X)
        
        return X
    
    def train_outcome_model(self, event_log: pd.DataFrame) -> dict:
        """
        Train model to predict if case will complete successfully.
        """
        features_df = self.prepare_features(event_log)
        
        X = self.encode_features(features_df, fit=True)
        y = features_df['completed'].astype(int).values
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.outcome_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.outcome_model.fit(X_train, y_train)
        
        y_pred = self.outcome_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        return {
            'accuracy': accuracy,
            'report': classification_report(y_test, y_pred, output_dict=True)
        }
    
    def train_next_activity_model(self, event_log: pd.DataFrame) -> dict:
        """
        Train model to predict next activity in the process.
        """
        features_df = self.prepare_features(event_log)
        
        X = self.encode_features(features_df, fit=False)  # Use existing encoders
        y = self.activity_encoder.fit_transform(features_df['next_activity'])
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.next_activity_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.next_activity_model.fit(X_train, y_train)
        
        y_pred = self.next_activity_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        return {
            'accuracy': accuracy,
            'classes': list(self.activity_encoder.classes_)
        }
    
    def train_time_model(self, event_log: pd.DataFrame) -> dict:
        """
        Train model to predict remaining process time.
        """
        features_df = self.prepare_features(event_log)
        
        X = self.encode_features(features_df, fit=False)
        y = features_df['remaining_time'].values
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.time_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.time_model.fit(X_train, y_train)
        
        y_pred = self.time_model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        
        return {
            'mae_hours': mae,
            'mae_days': mae / 24
        }
    
    def predict_case(self, case_prefix: dict) -> dict:
        """
        Make predictions for a running case.
        """
        # Create feature vector from prefix
        df = pd.DataFrame([case_prefix])
        X = self.encode_features(df, fit=False)
        
        predictions = {}
        
        if self.outcome_model:
            prob = self.outcome_model.predict_proba(X)[0]
            predictions['completion_probability'] = prob[1] if len(prob) > 1 else prob[0]
        
        if self.next_activity_model:
            next_act_idx = self.next_activity_model.predict(X)[0]
            predictions['next_activity'] = self.activity_encoder.inverse_transform([next_act_idx])[0]
            
            probs = self.next_activity_model.predict_proba(X)[0]
            top_3_idx = np.argsort(probs)[-3:][::-1]
            predictions['next_activity_probabilities'] = {
                self.activity_encoder.inverse_transform([i])[0]: probs[i] 
                for i in top_3_idx
            }
        
        if self.time_model:
            predictions['remaining_time_hours'] = self.time_model.predict(X)[0]
            predictions['remaining_time_days'] = predictions['remaining_time_hours'] / 24
        
        return predictions


def run_demo(event_log: pd.DataFrame) -> dict:
    """Run the full predictive analytics demo."""
    predictor = ProcessPredictor()
    
    # Train all models
    outcome_results = predictor.train_outcome_model(event_log)
    next_act_results = predictor.train_next_activity_model(event_log)
    time_results = predictor.train_time_model(event_log)
    
    # Make a sample prediction
    sample_case = {
        'prefix_length': 3,
        'current_activity': 'Stock Check',
        'order_value': 5000,
        'priority': 'High',
        'region': 'North',
        'num_unique_activities': 3,
        'has_deviation': False
    }
    
    prediction = predictor.predict_case(sample_case)
    
    return {
        'outcome_model': outcome_results,
        'next_activity_model': next_act_results,
        'time_model': time_results,
        'sample_prediction': prediction
    }
