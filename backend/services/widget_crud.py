# services/widget_crud.py - Widget and Time Settings CRUD Operations

from sqlalchemy.orm import Session
from models.widget_models import Widget, PageTimeSettings
from datetime import datetime
from typing import List, Dict, Optional
import json

# ---------- Widget CRUD Operations ----------

def create_widget(db: Session, page_id: str, widget_type: str, widget_label: str,
                 equipment_ids: List[int] = None, signal_ids: List[int] = None,
                 filter_selections: Dict = None, position_data: Dict = None,
                 styling_config: Dict = None):
    """Create a new widget with metadata"""
    widget = Widget(
        page_id=page_id,
        widget_type=widget_type,
        widget_label=widget_label,
        equipment_ids=json.dumps(equipment_ids or []),
        signal_ids=json.dumps(signal_ids or []),
        filter_selections=json.dumps(filter_selections or {}),
        position_data=json.dumps(position_data or {}),
        styling_config=json.dumps(styling_config or {})
    )
    db.add(widget)
    db.commit()
    db.refresh(widget)
    return widget

def get_widgets_by_page(db: Session, page_id: str) -> List[Widget]:
    """Get all widgets for a specific page"""
    return db.query(Widget).filter(Widget.page_id == page_id).all()

def get_widget_by_id(db: Session, widget_id: str) -> Widget:
    """Get widget by ID"""
    return db.query(Widget).filter(Widget.widget_id == widget_id).first()

def update_widget(db: Session, widget_id: str, **updates) -> Widget:
    """Update widget with provided fields"""
    widget = get_widget_by_id(db, widget_id)
    if widget:
        for key, value in updates.items():
            if key in ['equipment_ids', 'signal_ids', 'filter_selections', 'position_data', 'styling_config']:
                # JSON fields - convert to string
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
            setattr(widget, key, value)
        
        widget.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(widget)
    return widget

def delete_widget(db: Session, widget_id: str) -> Widget:
    """Delete widget by ID"""
    widget = get_widget_by_id(db, widget_id)
    if widget:
        db.delete(widget)
        db.commit()
    return widget

def delete_widgets_by_page(db: Session, page_id: str) -> int:
    """Delete all widgets for a page"""
    widgets = get_widgets_by_page(db, page_id)
    count = len(widgets)
    for widget in widgets:
        db.delete(widget)
    db.commit()
    return count

# ---------- Widget Data Conversion Helpers ----------

def widget_to_dict(widget: Widget) -> Dict:
    """Convert widget model to dictionary with JSON parsing"""
    if not widget:
        return None
    
    return {
        "widget_id": widget.widget_id,
        "page_id": widget.page_id,
        "widget_type": widget.widget_type,
        "widget_label": widget.widget_label,
        "equipment_ids": json.loads(widget.equipment_ids) if widget.equipment_ids else [],
        "signal_ids": json.loads(widget.signal_ids) if widget.signal_ids else [],
        "filter_selections": json.loads(widget.filter_selections) if widget.filter_selections else {},
        "position_data": json.loads(widget.position_data) if widget.position_data else {},
        "styling_config": json.loads(widget.styling_config) if widget.styling_config else {},
        "created_at": widget.created_at,
        "updated_at": widget.updated_at
    }

def widgets_to_dict_list(widgets: List[Widget]) -> List[Dict]:
    """Convert list of widgets to list of dictionaries"""
    return [widget_to_dict(widget) for widget in widgets]

# ---------- Page Time Settings CRUD Operations ----------

def create_or_update_page_time_settings(db: Session, page_id: str,
                                       default_time_range: Dict = None,
                                       default_refresh_rate: str = "manual",
                                       default_window_period: str = "auto",  # NEW
                                       last_time_start: str = None,
                                       last_time_end: str = None,
                                       last_range_type: str = None,
                                       last_window_period: str = None):  # NEW
    """Create or update page time settings with window period support"""
    settings = get_page_time_settings(db, page_id)
    
    if settings:
        # Update existing settings
        if default_time_range is not None:
            settings.default_time_range = json.dumps(default_time_range)
        if default_refresh_rate is not None:
            settings.default_refresh_rate = default_refresh_rate
        if default_window_period is not None:  # NEW
            settings.default_window_period = default_window_period
        if last_time_start is not None:
            settings.last_time_start = last_time_start
        if last_time_end is not None:
            settings.last_time_end = last_time_end
        if last_range_type is not None:
            settings.last_range_type = last_range_type
        if last_window_period is not None:  # NEW
            settings.last_window_period = last_window_period
        
        settings.updated_at = datetime.utcnow()
    else:
        # Create new settings
        settings = PageTimeSettings(
            page_id=page_id,
            default_time_range=json.dumps(default_time_range or {}),
            default_refresh_rate=default_refresh_rate,
            default_window_period=default_window_period,  # NEW
            last_time_start=last_time_start,
            last_time_end=last_time_end,
            last_range_type=last_range_type,
            last_window_period=last_window_period  # NEW
        )
        db.add(settings)
    
    db.commit()
    db.refresh(settings)
    return settings

def get_page_time_settings(db: Session, page_id: str) -> PageTimeSettings:
    """Get time settings for a page"""
    return db.query(PageTimeSettings).filter(PageTimeSettings.page_id == page_id).first()

def delete_page_time_settings(db: Session, page_id: str) -> PageTimeSettings:
    """Delete time settings for a page"""
    settings = get_page_time_settings(db, page_id)
    if settings:
        db.delete(settings)
        db.commit()
    return settings

def time_settings_to_dict(settings: PageTimeSettings) -> Dict:
    """Convert time settings model to dictionary with window period support"""
    if not settings:
        return None
    
    return {
        "page_id": settings.page_id,
        "default_time_range": json.loads(settings.default_time_range) if settings.default_time_range else {},
        "default_refresh_rate": settings.default_refresh_rate,
        "default_window_period": getattr(settings, 'default_window_period', 'auto'),  # NEW with fallback
        "last_time_start": settings.last_time_start,
        "last_time_end": settings.last_time_end,
        "last_range_type": settings.last_range_type,
        "last_window_period": getattr(settings, 'last_window_period', 'auto'),  # NEW with fallback
        "created_at": settings.created_at,
        "updated_at": settings.updated_at
    }

# ---------- Enhanced Page Layout Operations ----------

def update_page_layout_data(db: Session, page_id: str, layout_data: Dict) -> bool:
    """Update page layout data with complete GridStack layout"""
    from services.page_crud import get_page_by_id
    
    page = get_page_by_id(db, page_id)
    if page:
        page.layout_data = json.dumps(layout_data)
        page.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False

def get_page_layout_data(db: Session, page_id: str) -> Dict:
    """Get page layout data"""
    from services.page_crud import get_page_by_id
    
    page = get_page_by_id(db, page_id)
    if page and page.layout_data:
        try:
            return json.loads(page.layout_data)
        except json.JSONDecodeError:
            return {}
    return {}

# ---------- Bulk Operations ----------


def get_complete_page_data(db: Session, page_id: str) -> Dict:
    """Get complete page data including widgets and time settings - FIXED"""
    try:
        from services.page_crud import get_page_by_id
        
        # Get page
        page = get_page_by_id(db, page_id)
        if not page:
            print(f"❌ Page not found: {page_id}")
            return None
        
        print(f"✅ Page found: {page.page_id}")
        
        # Get widgets with error handling
        try:
            widgets = get_widgets_by_page(db, page_id)
            widgets_dict = widgets_to_dict_list(widgets)
            print(f"✅ Widgets loaded: {len(widgets_dict)} widgets")
        except Exception as e:
            print(f"❌ Error loading widgets: {str(e)}")
            widgets_dict = []
        
        # Get time settings with error handling
        try:
            time_settings_obj = get_page_time_settings(db, page_id)
            time_settings = time_settings_to_dict(time_settings_obj)
            print(f"✅ Time settings loaded: {time_settings is not None}")
        except Exception as e:
            print(f"❌ Error loading time settings: {str(e)}")
            time_settings = None
        
        # Get layout data with error handling
        try:
            layout_data = get_page_layout_data(db, page_id)
            print(f"✅ Layout data loaded: {layout_data is not None}")
        except Exception as e:
            print(f"❌ Error loading layout data: {str(e)}")
            layout_data = {}
        
        # Ensure datetime objects are serializable
        page_data = {
            "page_id": page.page_id,
            "page_name": page.page_name,
            "user_name": page.user_name,
            "page_route": page.page_route,
            "created_at": page.created_at.isoformat() if page.created_at else None,
            "updated_at": page.updated_at.isoformat() if page.updated_at else None
        }
        
        result = {
            "page": page_data,
            "widgets": widgets_dict,
            "time_settings": time_settings,
            "layout_data": layout_data
        }
        
        print(f"✅ Complete page data assembled successfully")
        return result
        
    except Exception as e:
        print(f"❌ Error in get_complete_page_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# ALSO ADD ERROR HANDLING TO HELPER FUNCTIONS

def get_page_layout_data(db: Session, page_id: str) -> Dict:
    """Get page layout data - ENHANCED WITH ERROR HANDLING"""
    try:
        from services.page_crud import get_page_by_id
        
        page = get_page_by_id(db, page_id)
        if not page:
            print(f"❌ Page not found for layout data: {page_id}")
            return {}
        
        if not page.layout_data:
            print(f"📝 No layout data found for page: {page_id}")
            return {}
        
        try:
            layout_data = json.loads(page.layout_data)
            print(f"✅ Layout data parsed successfully")
            return layout_data
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error in layout data: {str(e)}")
            return {}
            
    except Exception as e:
        print(f"❌ Error getting page layout data: {str(e)}")
        return {}


def widgets_to_dict_list(widgets: List[Widget]) -> List[Dict]:
    """Convert list of widgets to list of dictionaries - ENHANCED ERROR HANDLING"""
    try:
        result = []
        for widget in widgets:
            try:
                widget_dict = widget_to_dict(widget)
                if widget_dict:
                    result.append(widget_dict)
                    print(f"✅ Widget converted: {widget.widget_id}")
                else:
                    print(f"⚠️ Widget conversion returned None: {widget.widget_id}")
            except Exception as e:
                print(f"❌ Error converting widget {widget.widget_id}: {str(e)}")
                continue
        
        print(f"✅ Converted {len(result)} widgets to dict list")
        return result
        
    except Exception as e:
        print(f"❌ Error in widgets_to_dict_list: {str(e)}")
        return []


def widget_to_dict(widget: Widget) -> Dict:
    """Convert widget model to dictionary with JSON parsing - ENHANCED ERROR HANDLING"""
    try:
        if not widget:
            return None
        
        # Safely parse JSON fields
        def safe_json_parse(json_str, default=None):
            if not json_str:
                return default if default is not None else {}
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return default if default is not None else {}
        
        result = {
            "widget_id": widget.widget_id,
            "page_id": widget.page_id,
            "widget_type": widget.widget_type or "line_chart",
            "widget_label": widget.widget_label or "Untitled Widget",
            "equipment_ids": safe_json_parse(widget.equipment_ids, []),
            "signal_ids": safe_json_parse(widget.signal_ids, []),
            "filter_selections": safe_json_parse(widget.filter_selections, {}),
            "position_data": safe_json_parse(widget.position_data, {}),
            "styling_config": safe_json_parse(widget.styling_config, {}),
            "created_at": widget.created_at.isoformat() if widget.created_at else None,
            "updated_at": widget.updated_at.isoformat() if widget.updated_at else None
        }
        
        print(f"✅ Widget {widget.widget_id} converted to dict successfully")
        return result
        
    except Exception as e:
        print(f"❌ Error converting widget to dict: {str(e)}")
        # Return a basic structure to prevent complete failure
        return {
            "widget_id": getattr(widget, 'widget_id', 'unknown'),
            "page_id": getattr(widget, 'page_id', ''),
            "widget_type": "line_chart",
            "widget_label": "Error Loading Widget",
            "equipment_ids": [],
            "signal_ids": [],
            "filter_selections": {},
            "position_data": {},
            "styling_config": {},
            "created_at": None,
            "updated_at": None,
            "error": str(e)
        }
def save_complete_page_data(db: Session, page_id: str, widgets_data: List[Dict],
                          time_settings_data: Dict = None, layout_data: Dict = None) -> bool:
    """Save complete page data in single transaction"""
    try:
        # Update layout data
        if layout_data:
            update_page_layout_data(db, page_id, layout_data)
        
        # Update time settings
        if time_settings_data:
            create_or_update_page_time_settings(db, page_id, **time_settings_data)
        
        # Delete existing widgets and recreate (simpler than sync)
        delete_widgets_by_page(db, page_id)
        
        # Create new widgets
        for widget_data in widgets_data:
            create_widget(
                db=db,
                page_id=page_id,
                widget_type=widget_data.get('widget_type'),
                widget_label=widget_data.get('widget_label'),
                equipment_ids=widget_data.get('equipment_ids', []),
                signal_ids=widget_data.get('signal_ids', []),
                filter_selections=widget_data.get('filter_selections', {}),
                position_data=widget_data.get('position_data', {}),
                styling_config=widget_data.get('styling_config', {})
            )
        
        return True
    except Exception as e:
        db.rollback()
        print(f"Error saving page data: {str(e)}")
        return False