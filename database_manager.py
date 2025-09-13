"""
Database Manager for Accruals Forecasting System
Handles storage of forecasts, actuals, versions, and accuracy tracking
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path

class DatabaseManager:
    """Manages SQLite database for forecast storage and accuracy tracking"""
    
    def __init__(self, db_path: str = "accruals_forecasts.db"):
        """Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Forecast Versions table - tracks different forecast runs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forecast_versions (
                    version_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_name TEXT NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    target_month INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    data_file_path TEXT,
                    weekly_adjustment BOOLEAN DEFAULT FALSE,
                    auto_fit BOOLEAN DEFAULT FALSE,
                    parameters TEXT,  -- JSON of parameters used
                    notes TEXT,
                    UNIQUE(version_name, target_month, target_year)
                )
            """)
            
            # Forecasts table - stores individual category forecasts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forecasts (
                    forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    simple_average REAL,
                    weighted_average REAL,
                    trending_average REAL,
                    seasonal_forecast REAL,
                    recommended_accrual REAL,
                    confidence REAL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (version_id) REFERENCES forecast_versions (version_id)
                )
            """)
            
            # Actuals table - stores actual invoice data when loaded
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS actuals (
                    actual_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    actual_amount REAL NOT NULL,
                    invoice_month INTEGER NOT NULL,
                    invoice_year INTEGER NOT NULL,
                    loaded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_source TEXT,  -- Source file/path
                    UNIQUE(category, invoice_month, invoice_year)
                )
            """)
            
            # Accuracy Metrics table - tracks forecast vs actual performance
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accuracy_metrics (
                    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    actual_amount REAL NOT NULL,
                    simple_avg_error REAL,
                    weighted_avg_error REAL,
                    trending_avg_error REAL,
                    seasonal_forecast_error REAL,
                    recommended_error REAL,
                    simple_avg_accuracy REAL,
                    weighted_avg_accuracy REAL,
                    trending_avg_accuracy REAL,
                    seasonal_forecast_accuracy REAL,
                    recommended_accuracy REAL,
                    calculated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (version_id) REFERENCES forecast_versions (version_id)
                )
            """)
            
            # Method Performance table - tracks overall method performance over time
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS method_performance (
                    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    method_name TEXT NOT NULL,
                    category TEXT,
                    avg_accuracy REAL,
                    std_accuracy REAL,
                    total_forecasts INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(method_name, category)
                )
            """)
            
            # Learning Weights table - stores adaptive weights for methods
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_weights (
                    weight_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    simple_avg_weight REAL DEFAULT 0.25,
                    weighted_avg_weight REAL DEFAULT 0.25,
                    trending_avg_weight REAL DEFAULT 0.25,
                    seasonal_forecast_weight REAL DEFAULT 0.25,
                    confidence_score REAL DEFAULT 0.5,
                    sample_size INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(category)
                )
            """)
            
            conn.commit()
    
    def create_forecast_version(self, 
                              version_name: str,
                              target_month: int,
                              target_year: int,
                              data_file_path: str = None,
                              weekly_adjustment: bool = False,
                              auto_fit: bool = False,
                              parameters: Dict = None,
                              notes: str = None) -> int:
        """Create a new forecast version
        
        Returns:
            version_id: ID of created version
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            parameters_json = json.dumps(parameters) if parameters else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO forecast_versions 
                (version_name, target_month, target_year, data_file_path, 
                 weekly_adjustment, auto_fit, parameters, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (version_name, target_month, target_year, data_file_path,
                  weekly_adjustment, auto_fit, parameters_json, notes))
            
            return cursor.lastrowid
    
    def store_forecasts(self, version_id: int, forecasts_df: pd.DataFrame):
        """Store forecast results for a version
        
        Args:
            version_id: Version ID from forecast_versions table
            forecasts_df: DataFrame with forecast results
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for _, row in forecasts_df.iterrows():
                cursor.execute("""
                    INSERT INTO forecasts 
                    (version_id, category, simple_average, weighted_average, 
                     trending_average, seasonal_forecast, recommended_accrual, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    version_id,
                    row['Category'],
                    row.get('Simple_Average', 0),
                    row.get('Weighted_Average', 0),
                    row.get('Trending_Average', 0),
                    row.get('Seasonal_Forecast', 0),
                    row.get('Recommended_Accrual', 0),
                    row.get('Confidence', 0.5)
                ))
            
            conn.commit()
    
    def store_actuals(self, actuals_df: pd.DataFrame, 
                     invoice_month: int, 
                     invoice_year: int,
                     data_source: str = None):
        """Store actual invoice data
        
        Args:
            actuals_df: DataFrame with actual amounts by category
            invoice_month: Month of the invoices
            invoice_year: Year of the invoices
            data_source: Source file/path
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for category, amount in actuals_df.items():
                if pd.notna(amount) and amount != 0:
                    cursor.execute("""
                        INSERT OR REPLACE INTO actuals 
                        (category, actual_amount, invoice_month, invoice_year, data_source)
                        VALUES (?, ?, ?, ?, ?)
                    """, (category, float(amount), invoice_month, invoice_year, data_source))
            
            conn.commit()
    
    def calculate_accuracy_metrics(self, version_id: int, actual_month: int, actual_year: int):
        """Calculate and store accuracy metrics for a forecast version
        
        Args:
            version_id: Forecast version to evaluate
            actual_month: Month of actual data
            actual_year: Year of actual data
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get forecasts for this version
            forecasts_df = pd.read_sql_query("""
                SELECT * FROM forecasts WHERE version_id = ?
            """, conn, params=(version_id,))
            
            # Get actuals for the target month/year
            actuals_df = pd.read_sql_query("""
                SELECT category, actual_amount FROM actuals 
                WHERE invoice_month = ? AND invoice_year = ?
            """, conn, params=(actual_month, actual_year))
            
            if len(actuals_df) == 0:
                print(f"No actual data found for {actual_month}/{actual_year}")
                return
            
            cursor = conn.cursor()
            
            # Calculate metrics for each category
            for _, actual_row in actuals_df.iterrows():
                category = actual_row['category']
                actual_amount = actual_row['actual_amount']
                
                # Find corresponding forecast
                forecast_row = forecasts_df[forecasts_df['category'] == category]
                
                if len(forecast_row) == 0:
                    continue
                
                forecast_row = forecast_row.iloc[0]
                
                # Calculate errors and accuracy for each method
                methods = {
                    'simple_avg': forecast_row['simple_average'],
                    'weighted_avg': forecast_row['weighted_average'],
                    'trending_avg': forecast_row['trending_average'],
                    'seasonal_forecast': forecast_row['seasonal_forecast'],
                    'recommended': forecast_row['recommended_accrual']
                }
                
                errors = {}
                accuracies = {}
                
                for method, forecast_value in methods.items():
                    if pd.notna(forecast_value) and forecast_value != 0:
                        error = abs(actual_amount - forecast_value)
                        accuracy = 1 - (error / max(actual_amount, forecast_value))
                        errors[f"{method}_error"] = error
                        accuracies[f"{method}_accuracy"] = max(0, accuracy)
                    else:
                        errors[f"{method}_error"] = None
                        accuracies[f"{method}_accuracy"] = None
                
                # Store metrics
                cursor.execute("""
                    INSERT OR REPLACE INTO accuracy_metrics 
                    (version_id, category, actual_amount,
                     simple_avg_error, weighted_avg_error, trending_avg_error, 
                     seasonal_forecast_error, recommended_error,
                     simple_avg_accuracy, weighted_avg_accuracy, trending_avg_accuracy,
                     seasonal_forecast_accuracy, recommended_accuracy)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    version_id, category, actual_amount,
                    errors['simple_avg_error'], errors['weighted_avg_error'], 
                    errors['trending_avg_error'], errors['seasonal_forecast_error'], 
                    errors['recommended_error'],
                    accuracies['simple_avg_accuracy'], accuracies['weighted_avg_accuracy'],
                    accuracies['trending_avg_accuracy'], accuracies['seasonal_forecast_accuracy'],
                    accuracies['recommended_accuracy']
                ))
            
            conn.commit()
            
            # Update method performance
            self._update_method_performance()
    
    def _update_method_performance(self):
        """Update overall method performance statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            methods = ['simple_avg', 'weighted_avg', 'trending_avg', 'seasonal_forecast', 'recommended']
            
            for method in methods:
                # Overall performance - calculate standard deviation manually
                cursor.execute(f"""
                    SELECT {method}_accuracy
                    FROM accuracy_metrics 
                    WHERE {method}_accuracy IS NOT NULL
                """)
                
                accuracies = [row[0] for row in cursor.fetchall()]
                
                if accuracies:
                    avg_acc = np.mean(accuracies)
                    std_acc = np.std(accuracies) if len(accuracies) > 1 else 0
                    count = len(accuracies)
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO method_performance 
                        (method_name, category, avg_accuracy, std_accuracy, total_forecasts)
                        VALUES (?, NULL, ?, ?, ?)
                    """, (method, avg_acc, std_acc, count))
                
                # Per-category performance
                cursor.execute(f"""
                    SELECT category, {method}_accuracy
                    FROM accuracy_metrics 
                    WHERE {method}_accuracy IS NOT NULL
                """)
                
                # Group by category
                category_data = {}
                for row in cursor.fetchall():
                    category, accuracy = row
                    if category not in category_data:
                        category_data[category] = []
                    category_data[category].append(accuracy)
                
                # Calculate stats for each category
                for category, accuracies in category_data.items():
                    avg_acc = np.mean(accuracies)
                    std_acc = np.std(accuracies) if len(accuracies) > 1 else 0
                    count = len(accuracies)
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO method_performance 
                        (method_name, category, avg_accuracy, std_accuracy, total_forecasts)
                        VALUES (?, ?, ?, ?, ?)
                    """, (method, category, avg_acc, std_acc, count))
            
            conn.commit()
    
    def get_adaptive_weights(self, category: str) -> Dict[str, float]:
        """Get adaptive weights for a category based on historical performance
        
        Returns:
            Dictionary with weights for each method
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current weights
            cursor.execute("""
                SELECT simple_avg_weight, weighted_avg_weight, trending_avg_weight, 
                       seasonal_forecast_weight, confidence_score
                FROM learning_weights WHERE category = ?
            """, (category,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'simple_avg': result[0],
                    'weighted_avg': result[1],
                    'trending_avg': result[2],
                    'seasonal_forecast': result[3],
                    'confidence': result[4]
                }
            else:
                # Return default weights
                return {
                    'simple_avg': 0.25,
                    'weighted_avg': 0.25,
                    'trending_avg': 0.25,
                    'seasonal_forecast': 0.25,
                    'confidence': 0.5
                }
    
    def update_adaptive_weights(self):
        """Update adaptive weights based on historical accuracy"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get categories with accuracy data
            cursor.execute("""
                SELECT DISTINCT category FROM accuracy_metrics
                WHERE simple_avg_accuracy IS NOT NULL
            """)
            
            categories = [row[0] for row in cursor.fetchall()]
            
            for category in categories:
                # Get average accuracy for each method for this category
                cursor.execute("""
                    SELECT 
                        AVG(simple_avg_accuracy) as simple_avg,
                        AVG(weighted_avg_accuracy) as weighted_avg,
                        AVG(trending_avg_accuracy) as trending_avg,
                        AVG(seasonal_forecast_accuracy) as seasonal_forecast,
                        COUNT(*) as sample_size
                    FROM accuracy_metrics 
                    WHERE category = ? 
                    AND simple_avg_accuracy IS NOT NULL
                """, (category,))
                
                result = cursor.fetchone()
                
                if result and result[0] is not None:
                    accuracies = {
                        'simple_avg': result[0] or 0,
                        'weighted_avg': result[1] or 0,
                        'trending_avg': result[2] or 0,
                        'seasonal_forecast': result[3] or 0
                    }
                    sample_size = result[4]
                    
                    # Calculate weights based on relative accuracy
                    total_accuracy = sum(accuracies.values())
                    
                    if total_accuracy > 0:
                        weights = {k: v / total_accuracy for k, v in accuracies.items()}
                        confidence = min(0.9, sample_size / 10)  # More samples = higher confidence
                        
                        cursor.execute("""
                            INSERT OR REPLACE INTO learning_weights 
                            (category, simple_avg_weight, weighted_avg_weight, 
                             trending_avg_weight, seasonal_forecast_weight, 
                             confidence_score, sample_size)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            category,
                            weights['simple_avg'],
                            weights['weighted_avg'],
                            weights['trending_avg'],
                            weights['seasonal_forecast'],
                            confidence,
                            sample_size
                        ))
            
            conn.commit()
    
    def get_forecast_versions(self, target_month: int = None, target_year: int = None) -> pd.DataFrame:
        """Get forecast versions with optional filtering"""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM forecast_versions"
            params = []
            
            if target_month and target_year:
                query += " WHERE target_month = ? AND target_year = ?"
                params = [target_month, target_year]
            
            query += " ORDER BY created_date DESC"
            
            return pd.read_sql_query(query, conn, params=params)
    
    def get_forecasts_by_version(self, version_id: int) -> pd.DataFrame:
        """Get all forecasts for a specific version"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query("""
                SELECT * FROM forecasts WHERE version_id = ? ORDER BY category
            """, conn, params=(version_id,))
    
    def get_accuracy_summary(self, category: str = None) -> pd.DataFrame:
        """Get accuracy summary statistics"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT 
                    category,
                    COUNT(*) as total_forecasts,
                    AVG(simple_avg_accuracy) as simple_avg_accuracy,
                    AVG(weighted_avg_accuracy) as weighted_avg_accuracy,
                    AVG(trending_avg_accuracy) as trending_avg_accuracy,
                    AVG(seasonal_forecast_accuracy) as seasonal_forecast_accuracy,
                    AVG(recommended_accuracy) as recommended_accuracy
                FROM accuracy_metrics
                WHERE simple_avg_accuracy IS NOT NULL
            """
            
            if category:
                query += " AND category = ?"
                params = [category]
            else:
                params = []
            
            query += " GROUP BY category ORDER BY category"
            
            return pd.read_sql_query(query, conn, params=params)

    def close(self):
        """Close database connection"""
        pass  # Using context managers, no explicit close needed