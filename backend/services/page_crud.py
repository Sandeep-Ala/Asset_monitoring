# services/page_crud.py - Enhanced with Widget Support

from sqlalchemy.orm import Session
from models.meta_models import Page
from datetime import datetime
import json
from typing import Dict, Optional

def create_page(db: Session, data: dict):
    """Create a new page"""
    new_page = Page(**data)
    db.add(new_page)
    db.commit()
    db.refresh(new_page)
    return new_page

def get_pages(db: Session):
    """Get all pages"""
    return db.query(Page).all()

def get_page_by_id(db: Session, page_id: str):
    """Get page by ID"""
    return db.query(Page).filter(Page.page_id == page_id).first()

def get_page_by_route(db: Session, page_route: str):
    """Get page by route"""
    return db.query(Page).filter(Page.page_route == page_route).first()

def update_page(db: Session, page_id: str, updates: dict):
    """Update page with provided fields"""
    page = db.query(Page).filter(Page.page_id == page_id).first()
    if page:
        for key, value in updates.items():
            if key == 'layout_data' and isinstance(value, (dict, list)):
                # Convert layout data to JSON string
                value = json.dumps(value)
            setattr(page, key, value)
        page.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(page)
    return page

def delete_page(db: Session, page_id: str):
    """Delete page and all associated widgets/time settings"""
    page = db.query(Page).filter(Page.page_id == page_id).first()
    if page:
        # Note: Widgets and time settings will be automatically deleted
        # due to cascade="all, delete-orphan" in the relationships
        db.delete(page)
        db.commit()
    return page

# ---------- Enhanced Layout Operations ----------

def save_page_layout(db: Session, page_id: str, layout_data: Dict) -> bool:
    """Save complete page layout data"""
    page = get_page_by_id(db, page_id)
    if page:
        page.layout_data = json.dumps(layout_data)
        page.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False

def get_page_layout(db: Session, page_id: str) -> Optional[Dict]:
    """Get page layout data as dictionary"""
    page = get_page_by_id(db, page_id)
    if page and page.layout_data:
        try:
            return json.loads(page.layout_data)
        except json.JSONDecodeError:
            return None
    return None

def update_layout_data(db: Session, page_id: str, layout_data: Dict) -> bool:
    """Update only the layout_data field"""
    return save_page_layout(db, page_id, layout_data)

# ---------- Page Data Helpers ----------

def page_to_dict(page: Page) -> Dict:
    """Convert page model to dictionary"""
    if not page:
        return None
    
    layout_data = None
    if page.layout_data:
        try:
            layout_data = json.loads(page.layout_data)
        except json.JSONDecodeError:
            layout_data = None
    
    return {
        "page_id": page.page_id,
        "page_name": page.page_name,
        "user_name": page.user_name,
        "page_route": page.page_route,
        "layout_data": layout_data,
        "created_at": page.created_at,
        "updated_at": page.updated_at
    }

# ---------- Page Validation ----------

def validate_page_route(db: Session, page_route: str, exclude_page_id: str = None) -> bool:
    """Check if page route is unique"""
    query = db.query(Page).filter(Page.page_route == page_route)
    if exclude_page_id:
        query = query.filter(Page.page_id != exclude_page_id)
    return query.first() is None

def validate_page_name(db: Session, page_name: str, exclude_page_id: str = None) -> bool:
    """Check if page name is unique"""
    query = db.query(Page).filter(Page.page_name == page_name)
    if exclude_page_id:
        query = query.filter(Page.page_id != exclude_page_id)
    return query.first() is None