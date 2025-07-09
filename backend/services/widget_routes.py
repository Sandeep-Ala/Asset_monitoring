# services/widget_routes.py - Widget Management and Time Settings APIs

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

import services.widget_crud as widget_crud
import services.meta_crud as meta_crud
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from config import get_db

widget_router = InferringRouter()

# ---------- Pydantic Schemas ----------

class WidgetCreate(BaseModel):
    page_id: str
    widget_type: str  # 'line_chart', 'bar_chart', 'pie_chart', 'table'
    widget_label: str
    equipment_ids: List[int] = []
    signal_ids: List[int] = []
    filter_selections: Dict[str, Any] = {}  # {"equipment_1": {"dcu": "1", "n_rack": "2"}}
    position_data: Dict[str, Any] = {}      # {"x": 0, "y": 0, "w": 4, "h": 2}
    styling_config: Dict[str, Any] = {}     # {"colors": ["#ff0000"], "lineStyles": ["solid"]}

class WidgetUpdate(BaseModel):
    widget_label: Optional[str] = None
    equipment_ids: Optional[List[int]] = None
    signal_ids: Optional[List[int]] = None
    filter_selections: Optional[Dict[str, Any]] = None
    position_data: Optional[Dict[str, Any]] = None
    styling_config: Optional[Dict[str, Any]] = None

class WidgetOut(BaseModel):
    widget_id: str
    page_id: str
    widget_type: str
    widget_label: str
    equipment_ids: List[int]
    signal_ids: List[int]
    filter_selections: Dict[str, Any]
    position_data: Dict[str, Any]
    styling_config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class PageTimeSettingsCreate(BaseModel):
    page_id: str
    default_time_range: Dict[str, Any] = {}
    default_refresh_rate: str = "manual"
    last_time_start: Optional[str] = None
    last_time_end: Optional[str] = None
    last_range_type: Optional[str] = None

class PageTimeSettingsOut(BaseModel):
    page_id: str
    default_time_range: Dict[str, Any]
    default_refresh_rate: str
    last_time_start: Optional[str]
    last_time_end: Optional[str]
    last_range_type: Optional[str]
    created_at: datetime
    updated_at: datetime

class PageLayoutData(BaseModel):
    layout_data: Dict[str, Any]
    widgets_data: Optional[List[Dict[str, Any]]] = []
    time_settings_data: Optional[Dict[str, Any]] = None

class WidgetDataRequest(BaseModel):
    time_start: str  # ISO datetime
    time_end: str    # ISO datetime
    time_range_type: Optional[str] = "custom"

class MetadataDropdownResponse(BaseModel):
    equipments: List[Dict[str, Any]]
    total_count: int

class EquipmentSignalsResponse(BaseModel):
    signals: List[Dict[str, Any]]
    filters: List[Dict[str, Any]]
    equipment_info: Dict[str, Any]

# ---------- Widget Management Routes ----------

@cbv(widget_router)
class WidgetRoutes:
    db: Session = Depends(get_db)
    widget_router.tags = ["Widgets"]
    widget_router.prefix = "/widgets"

    @widget_router.post("/", response_model=WidgetOut)
    def create_widget(self, widget: WidgetCreate):
        """Create a new widget with metadata"""
        # Validate page exists
        from services.page_crud import get_page_by_id
        page = get_page_by_id(self.db, widget.page_id)
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        
        # Validate equipment IDs exist
        for equipment_id in widget.equipment_ids:
            equipment = meta_crud.get_equipment_by_id(self.db, equipment_id)
            if not equipment:
                raise HTTPException(status_code=400, detail=f"Equipment ID {equipment_id} not found")
        
        # Validate signal IDs exist
        for signal_id in widget.signal_ids:
            signal = meta_crud.get_equipment_signal_by_id(self.db, signal_id)
            if not signal:
                raise HTTPException(status_code=400, detail=f"Signal ID {signal_id} not found")
        
        # Create widget
        db_widget = widget_crud.create_widget(
            db=self.db,
            page_id=widget.page_id,
            widget_type=widget.widget_type,
            widget_label=widget.widget_label,
            equipment_ids=widget.equipment_ids,
            signal_ids=widget.signal_ids,
            filter_selections=widget.filter_selections,
            position_data=widget.position_data,
            styling_config=widget.styling_config
        )
        
        return widget_crud.widget_to_dict(db_widget)

    @widget_router.get("/page/{page_id}", response_model=List[WidgetOut])
    def get_widgets_by_page(self, page_id: str):
        """Get all widgets for a specific page"""
        widgets = widget_crud.get_widgets_by_page(self.db, page_id)
        return widget_crud.widgets_to_dict_list(widgets)

    @widget_router.get("/{widget_id}", response_model=WidgetOut)
    def get_widget(self, widget_id: str):
        """Get widget by ID"""
        widget = widget_crud.get_widget_by_id(self.db, widget_id)
        if not widget:
            raise HTTPException(status_code=404, detail="Widget not found")
        return widget_crud.widget_to_dict(widget)

    @widget_router.put("/{widget_id}", response_model=WidgetOut)
    def update_widget(self, widget_id: str, updates: WidgetUpdate):
        """Update widget"""
        # Check widget exists
        widget = widget_crud.get_widget_by_id(self.db, widget_id)
        if not widget:
            raise HTTPException(status_code=404, detail="Widget not found")
        
        # Prepare updates
        update_data = updates.dict(exclude_unset=True)
        
        # Validate equipment IDs if provided
        if 'equipment_ids' in update_data:
            for equipment_id in update_data['equipment_ids']:
                equipment = meta_crud.get_equipment_by_id(self.db, equipment_id)
                if not equipment:
                    raise HTTPException(status_code=400, detail=f"Equipment ID {equipment_id} not found")
        
        # Validate signal IDs if provided
        if 'signal_ids' in update_data:
            for signal_id in update_data['signal_ids']:
                signal = meta_crud.get_equipment_signal_by_id(self.db, signal_id)
                if not signal:
                    raise HTTPException(status_code=400, detail=f"Signal ID {signal_id} not found")
        
        # Update widget
        updated_widget = widget_crud.update_widget(self.db, widget_id, **update_data)
        return widget_crud.widget_to_dict(updated_widget)

    @widget_router.delete("/{widget_id}")
    def delete_widget(self, widget_id: str):
        """Delete widget"""
        widget = widget_crud.delete_widget(self.db, widget_id)
        if not widget:
            raise HTTPException(status_code=404, detail="Widget not found")
        return {"message": "Widget deleted successfully"}

# ---------- Page Time Settings Routes ----------

@cbv(widget_router)
class PageTimeRoutes:
    db: Session = Depends(get_db)
    widget_router.tags = ["Page Time Settings"]

    @widget_router.post("/pages/{page_id}/time-settings", response_model=PageTimeSettingsOut)
    def create_or_update_time_settings(self, page_id: str, settings: PageTimeSettingsCreate):
        """Create or update page time settings"""
        # Validate page exists
        from services.page_crud import get_page_by_id
        page = get_page_by_id(self.db, page_id)
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        
        db_settings = widget_crud.create_or_update_page_time_settings(
            db=self.db,
            page_id=page_id,
            default_time_range=settings.default_time_range,
            default_refresh_rate=settings.default_refresh_rate,
            default_window_period=settings.default_window_period,  # NEW
            last_time_start=settings.last_time_start,
            last_time_end=settings.last_time_end,
            last_range_type=settings.last_range_type,
            last_window_period=settings.last_window_period  # NEW
        )
        
        return widget_crud.time_settings_to_dict(db_settings)

    @widget_router.get("/pages/{page_id}/time-settings", response_model=Optional[PageTimeSettingsOut])
    def get_time_settings(self, page_id: str):
        """Get page time settings"""
        settings = widget_crud.get_page_time_settings(self.db, page_id)
        if settings:
            return widget_crud.time_settings_to_dict(settings)
        return None

# ---------- Enhanced Layout Management Routes ----------

@cbv(widget_router)
class LayoutRoutes:
    db: Session = Depends(get_db)
    widget_router.tags = ["Page Layout"]

    @widget_router.put("/pages/{page_id}/layout")
    def save_complete_layout(self, page_id: str, layout_data: PageLayoutData):
        """Save complete page layout with widgets and time settings"""
        # Validate page exists
        from services.page_crud import get_page_by_id
        page = get_page_by_id(self.db, page_id)
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        
        success = widget_crud.save_complete_page_data(
            db=self.db,
            page_id=page_id,
            widgets_data=layout_data.widgets_data or [],
            time_settings_data=layout_data.time_settings_data,
            layout_data=layout_data.layout_data
        )
        
        if success:
            return {"message": "Layout saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save layout")

    @widget_router.get("/pages/{page_id}/layout")
    def get_complete_layout(self, page_id: str):
        """Get complete page layout with widgets and time settings - FIXED"""
        try:
            # Validate page exists first
            from services.page_crud import get_page_by_id
            page = get_page_by_id(self.db, page_id)
            if not page:
                raise HTTPException(status_code=404, detail="Page not found")
            
            # Get complete page data with error handling
            layout_data = widget_crud.get_complete_page_data(self.db, page_id)
            
            if layout_data is None:
                # If no data, return empty structure
                return {
                    "page": {
                        "page_id": page.page_id,
                        "page_name": page.page_name,
                        "user_name": page.user_name,
                        "page_route": page.page_route,
                        "created_at": page.created_at.isoformat() if page.created_at else None,
                        "updated_at": page.updated_at.isoformat() if page.updated_at else None
                    },
                    "widgets": [],
                    "time_settings": None,
                    "layout_data": {}
                }
            
            return layout_data
            
        except Exception as e:
            # Log the error for debugging
            print(f"❌ Error in get_complete_layout: {str(e)}")
            print(f"❌ Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            
            # Return 500 with detailed error
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to load layout: {str(e)}"
            )


# ---------- Metadata Support Routes (for Widget Wizard) ----------

@cbv(widget_router)
class MetadataRoutes:
    db: Session = Depends(get_db)
    widget_router.tags = ["Widget Metadata"]

    @widget_router.get("/metadata/equipments", response_model=MetadataDropdownResponse)
    def get_equipments_for_dropdown(self):
        """Get all equipment for dropdown selection in widget wizard"""
        equipments = meta_crud.get_all_equipments(self.db)
        
        equipment_list = []
        for equipment in equipments:
            equipment_list.append({
                "id": equipment.id,
                "name": equipment.name,
                "location": equipment.location,
                "model_id": equipment.model_id,
                "enable": equipment.enable
            })
        
        return {
            "equipments": equipment_list,
            "total_count": len(equipment_list)
        }

    @widget_router.get("/metadata/equipment/{equipment_id}/signals", response_model=EquipmentSignalsResponse)
    def get_equipment_signals_and_filters(self, equipment_id: int):
        """Get signals and filters for specific equipment"""
        # Get equipment info
        equipment = meta_crud.get_equipment_by_id(self.db, equipment_id)
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipment not found")
        
        # Get signals for this equipment
        signals = self.db.query(meta_crud.EquipmentSignal).filter(
            meta_crud.EquipmentSignal.eqp_id == equipment_id
        ).all()
        
        # Get filters for this equipment
        filters = meta_crud.get_by_eq_id(self.db, equipment_id)
        
        signal_list = []
        for signal in signals:
            signal_list.append({
                "id": signal.id,
                "key": signal.key,
                "value": signal.value,
                "unit": signal.unit,
                "desc": signal.desc,
                "enable": signal.enable
            })
        
        filter_list = []
        for filter_item in filters:
            filter_list.append({
                "id": filter_item.id,
                "filter_key": filter_item.filter_key,
                "filter_value": filter_item.filter_value
            })
        
        return {
            "signals": signal_list,
            "filters": filter_list,
            "equipment_info": {
                "id": equipment.id,
                "name": equipment.name,
                "location": equipment.location,
                "model_id": equipment.model_id
            }
        }

    @widget_router.get("/metadata/signals")
    def get_all_signals(self):
        """Get all signals across all equipment"""
        signals = meta_crud.get_all_equipment_signals(self.db)
        
        signal_list = []
        for signal in signals:
            # Get equipment info for this signal
            equipment = meta_crud.get_equipment_by_id(self.db, signal.eqp_id)
            
            signal_list.append({
                "id": signal.id,
                "key": signal.key,
                "value": signal.value,
                "unit": signal.unit,
                "desc": signal.desc,
                "enable": signal.enable,
                "equipment_id": signal.eqp_id,
                "equipment_name": equipment.name if equipment else "Unknown"
            })
        
        return {
            "signals": signal_list,
            "total_count": len(signal_list)
        }

# ---------- Widget Data Retrieval Routes ----------

@cbv(widget_router)
class WidgetDataRoutes:
    db: Session = Depends(get_db)
    widget_router.tags = ["Widget Data"]

    @widget_router.post("/{widget_id}/data")
    def get_widget_data(self, widget_id: str, time_request: WidgetDataRequest, connection_id: Optional[str] = None):
        """Get data for a specific widget with window period support"""
        from services.data_retrieval_service import DataRetrievalService
        from services.query_generation_service import QueryGenerationService
        
        # Validate time range
        time_range = {
            "start": "2025-03-07T04:52:00.000Z",
            "end": "2025-03-08T05:52:00.000Z",
            "range_type": time_request.time_range_type
        }
        
        is_valid, error = DataRetrievalService.validate_time_range(time_range)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid time range: {error}")
        
        # Get widget data with window period
        success, data, error_msg = DataRetrievalService.get_widget_data_with_window(
            self.db, widget_id, time_range, 'auto', connection_id
        )
        
        if success:
            return data
        else:
            raise HTTPException(status_code=500, detail=error_msg)

    @widget_router.post("/pages/{page_id}/widgets/data-bulk")
    def get_bulk_widget_data(self, page_id: str, time_request: WidgetDataRequest, connection_id: Optional[str] = None):
        """Get data for all widgets on a page with window period support"""
        from services.data_retrieval_service import DataRetrievalService
        
        # Validate time range
        time_range = {
            "start": time_request.time_start,
            "end": time_request.time_end,
            "range_type": time_request.time_range_type
        }
        
        is_valid, error = DataRetrievalService.validate_time_range(time_range)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid time range: {error}")
        
        # Get bulk data with window period
        bulk_data = DataRetrievalService.get_bulk_widget_data_with_window(
            self.db, page_id, time_range, time_request.window_period, connection_id
        )
        
        return bulk_data

    @widget_router.get("/data-sources/status")
    def get_data_source_status(self, connection_id: Optional[str] = None):
        """Get status of data source connections"""
        from services.data_retrieval_service import DataRetrievalService
        
        status = DataRetrievalService.get_data_source_status(self.db, connection_id)
        return status

# ---------- Time Range Helper Routes ----------

@cbv(widget_router)
class TimeRangeRoutes:
    db: Session = Depends(get_db)
    widget_router.tags = ["Time Management"]

    @widget_router.get("/time-ranges/presets")
    def get_time_range_presets(self):
        """Get predefined time range options and window periods for UI"""
        from services.query_generation_service import QueryGenerationService
        from config import WINDOW_PERIOD_OPTIONS, MAX_POINTS_PER_WIDGET
        
        presets = QueryGenerationService.generate_sample_time_ranges()
        
        # Format window period options for UI
        window_periods = []
        for period_str, period_seconds in WINDOW_PERIOD_OPTIONS.items():
            if period_str == 'auto':
                window_periods.append({
                    "label": "Auto (Smart calculation)",
                    "value": "auto",
                    "description": f"Automatically calculate optimal window to stay within {MAX_POINTS_PER_WIDGET} points"
                })
            else:
                # Convert to readable format
                if period_seconds < 60:
                    label = f"{period_seconds} second{'s' if period_seconds != 1 else ''}"
                elif period_seconds < 3600:
                    minutes = period_seconds // 60
                    label = f"{minutes} minute{'s' if minutes != 1 else ''}"
                else:
                    hours = period_seconds // 3600
                    label = f"{hours} hour{'s' if hours != 1 else ''}"
                
                window_periods.append({
                    "label": label,
                    "value": period_str,
                    "description": f"Fixed {label} intervals"
                })
        
        return {
            "presets": presets,
            "refresh_rates": [
                {"label": "Manual", "value": "manual", "description": "Refresh only when requested"},
                {"label": "Every 5 minutes", "value": "5m", "description": "Auto refresh every 5 minutes"},
                {"label": "Every 15 minutes", "value": "15m", "description": "Auto refresh every 15 minutes"},
                {"label": "Every 1 hour", "value": "1h", "description": "Auto refresh every hour"}
            ],
            "window_periods": window_periods,
            "config": {
                "max_points_per_widget": MAX_POINTS_PER_WIDGET,
                "default_window_period": "auto"
            }
        }

    @widget_router.post("/time-ranges/calculate")
    def calculate_time_range(self, range_type: str, custom_start: Optional[str] = None, custom_end: Optional[str] = None):
        """Calculate time range based on type"""
        from services.query_generation_service import QueryGenerationService
        
        time_range = QueryGenerationService.calculate_time_range(range_type, custom_start, custom_end)
        return time_range

    @widget_router.post("/window-period/calculate")
    def calculate_optimal_window_period(self, time_start: str, time_end: str, max_points: Optional[int] = None):
        """Calculate optimal window period for given time range"""
        from config import calculate_optimal_window_period, MAX_POINTS_PER_WIDGET
        
        if max_points is None:
            max_points = MAX_POINTS_PER_WIDGET
        
        try:
            window_str, window_seconds, total_points = calculate_optimal_window_period(
                time_start, time_end, max_points
            )
            
            return {
                "success": True,
                "window_period": window_str,
                "window_seconds": window_seconds,
                "estimated_points": total_points,
                "max_points_limit": max_points,
                "time_range": {
                    "start": time_start,
                    "end": time_end
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "window_period": "1h",
                "window_seconds": 3600,
                "estimated_points": 100
            }

# Router export
router = widget_router