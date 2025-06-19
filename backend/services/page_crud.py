from sqlalchemy.orm import Session
from models.meta_models import Page
from datetime import datetime

def create_page(db: Session, data: dict):
    new_page = Page(**data)
    db.add(new_page)
    db.commit()
    db.refresh(new_page)
    return new_page

def get_pages(db: Session):
    return db.query(Page).all()

def get_page_by_id(db: Session, page_id: str):
    return db.query(Page).filter(Page.page_id == page_id).first()

def update_page(db: Session, page_id: str, updates: dict):
    page = db.query(Page).filter(Page.page_id == page_id).first()
    if page:
        for key, value in updates.items():
            setattr(page, key, value)
        page.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(page)
    return page

def delete_page(db: Session, page_id: str):
    page = db.query(Page).filter(Page.page_id == page_id).first()
    if page:
        db.delete(page)
        db.commit()
    return page
