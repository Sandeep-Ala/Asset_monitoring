# config.py - Updated with Widget Models

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.meta_models import Base

# Import all models to ensure they're registered with SQLAlchemy
from models.meta_models import Page, MasterModel, Equipment, EquipmentSpec, EquipmentSignal, EquipmentDoc, EquipmentFilter
from models.datasource_models import DataConnection, ConnectionConfig
from models.widget_models import Widget, PageTimeSettings  # New widget models

BASE_PARQUET_PATH = "D:\Asset Monitoring System\Data-Backup\site=UK_Tollgate"
#D:\Asset Monitoring System\GITHUB\Asset_M_combined\MetaDB.sqlite3
SQLITE_URL = "sqlite:///D:/Asset Monitoring System/GITHUB/Asset_M_combined/MetaDB.sqlite3"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# Create all tables (including new widget tables)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Window Period Configuration
import os
from typing import Dict, List

# Configurable points per widget (for testing different values)
MAX_POINTS_PER_WIDGET = int(os.getenv('MAX_POINTS_PER_WIDGET', '99'))
DEFAULT_WINDOW_PERIOD = os.getenv('DEFAULT_WINDOW_PERIOD', 'auto')

# Window period options and their seconds
WINDOW_PERIOD_OPTIONS = {
    '1sec': 1,
    '5sec': 5,
    '30sec': 30,
    '1m': 60,
    '5m': 300,
    '15m': 900,
    '30m': 1800,
    '1h': 3600,
    '6h': 21600,
    '12h': 43200,
    '24h': 86400,
    'auto': 0  # Special case - calculated automatically
}

def calculate_optimal_window_period(time_start: str, time_end: str, max_points: int = None) -> tuple:
    """
    Calculate optimal window period to stay within point limits
    
    Returns: (window_period_str, window_seconds, total_points)
    """
    from datetime import datetime
    
    if max_points is None:
        max_points = MAX_POINTS_PER_WIDGET
    
    try:
        # Parse time range
        start_dt = datetime.fromisoformat(time_start.replace('Z', '+00:00').replace('+00:00', ''))
        end_dt = datetime.fromisoformat(time_end.replace('Z', '+00:00').replace('+00:00', ''))
        
        # Calculate total seconds
        total_seconds = (end_dt - start_dt).total_seconds()
        
        # Calculate optimal window to get max_points
        optimal_window_seconds = total_seconds / max_points
        
        # Find the best matching predefined window period
        best_window = '1h'
        best_seconds = 3600
        min_diff = float('inf')
        
        for window_str, window_secs in WINDOW_PERIOD_OPTIONS.items():
            if window_str == 'auto':
                continue
                
            # Check how many points this window would generate
            points_count = total_seconds / window_secs if window_secs > 0 else max_points
            
            # Prefer windows that give us close to max_points but not over
            if points_count <= max_points:
                diff = abs(points_count - max_points)
                if diff < min_diff:
                    min_diff = diff
                    best_window = window_str
                    best_seconds = window_secs
        
        # If no predefined window works well, use custom window
        if min_diff > max_points * 0.3:  # If difference is > 30%
            if optimal_window_seconds < 60:
                custom_window = f"{int(optimal_window_seconds)}sec"
            elif optimal_window_seconds < 3600:
                custom_window = f"{int(optimal_window_seconds/60)}m"
            else:
                custom_window = f"{optimal_window_seconds/3600:.1f}h"
            
            return custom_window, optimal_window_seconds, max_points
        
        actual_points = int(total_seconds / best_seconds)
        return best_window, best_seconds, actual_points
        
    except Exception as e:
        print(f"Error calculating window period: {e}")
        return '1h', 3600, max_points

# Database initialization status
print("✅ Database initialized with all tables:")
print("   - Pages (enhanced with layout_data)")
print("   - Master Models, Equipment, Specs, Signals, Docs, Filters")
print("   - Data Connections and Configs")
print("   - Widgets and Page Time Settings (NEW)")
print("📍 Database location:", SQLITE_URL)
print("⚙️  Widget Configuration:")
print(f"   - Max points per widget: {MAX_POINTS_PER_WIDGET}")
print(f"   - Default window period: {DEFAULT_WINDOW_PERIOD}")
print(f"   - Available window periods: {list(WINDOW_PERIOD_OPTIONS.keys())}")