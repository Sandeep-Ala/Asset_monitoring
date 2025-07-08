# models/widget_models.py - Widget and Time Management Database Models

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.meta_models import Base
from datetime import datetime
import uuid

class Widget(Base):
    """
    Widget configuration table for storing metadata-driven widgets
    Supports multiple equipment, signals, and user-selected filters
    """
    __tablename__ = "widgets"
    
    widget_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    page_id = Column(String, ForeignKey("pages.page_id"), nullable=False)
    widget_type = Column(String(32), nullable=False)  # 'line_chart', 'bar_chart', 'pie_chart', 'table'
    widget_label = Column(String(128), nullable=False)
    
    # Metadata Configuration (stored as JSON strings)
    equipment_ids = Column(Text)  # JSON array: ["1", "2", "3"] - Multiple equipment support
    signal_ids = Column(Text)     # JSON array: ["5", "6", "7"] - Multiple signals support
    filter_selections = Column(Text)  # JSON object: {"equipment_1": {"dcu": "1", "n_rack": "2"}}
    
    # Widget Position and Styling (GridStack integration)
    position_data = Column(Text)    # JSON: {"x": 0, "y": 0, "w": 4, "h": 2, "locked": false}
    styling_config = Column(Text)   # JSON: {"colors": ["#ff0000"], "lineStyles": ["solid"], "showLegend": true}
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to page
    page = relationship("Page", back_populates="widgets")

class PageTimeSettings(Base):
    """
    Page-level time management settings with window period support
    Global time picker configuration per page
    """
    __tablename__ = "page_time_settings"
    
    page_id = Column(String, ForeignKey("pages.page_id"), primary_key=True)
    
    # Time Range Configuration
    default_time_range = Column(Text)  # JSON: {"start": "2025-01-01T00:00:00", "end": "2025-01-01T23:59:59", "range_type": "last_1_hour"}
    default_refresh_rate = Column(String(16), default="manual")  # 'manual', '5m', '15m', '1h'
    default_window_period = Column(String(16), default="auto")   # NEW: '1sec', '5m', '1m', '1h', 'auto'
    
    # Last used settings for persistence
    last_time_start = Column(String(32))    # ISO datetime string
    last_time_end = Column(String(32))      # ISO datetime string
    last_range_type = Column(String(32))    # 'custom', 'last_15m', 'last_1h', 'last_6h', 'last_24h'
    last_window_period = Column(String(16)) # NEW: Last used window period
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to page
    page = relationship("Page", back_populates="time_settings")

# Add relationships to existing Page model
# Note: This will be added to meta_models.py in the next file