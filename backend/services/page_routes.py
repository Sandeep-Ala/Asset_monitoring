from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

import services.page_crud as crud
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from config import get_db
from models.meta_models import Page  # import for ORM model type hinting

page_router = InferringRouter()


# Pydantic Schemas
class PageBase(BaseModel):
    page_name: str
    user_name: str
    page_route: str

class PageCreate(PageBase):
    pass

class PageUpdate(BaseModel):
    page_name: Optional[str] = None  # Allow partial updates

class PageOut(BaseModel):
    page_id: str
    page_name: str
    user_name: str
    page_route: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Route class
@cbv(page_router)
class PageModelRoutes:
    db: Session = Depends(get_db)
    page_router.tags = ["Pages"]
    page_router.prefix = "/pages"

    @page_router.post("/", response_model=PageOut)
    def create_page_route(self, page: PageCreate):
        return crud.create_page(self.db, page.dict())

    @page_router.get("/", response_model=List[PageOut])
    def get_all_pages(self):
        return crud.get_pages(self.db)

    @page_router.get("/{page_id}", response_model=PageOut)
    def get_single_page(self, page_id: str):
        page = crud.get_page_by_id(self.db, page_id)
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        return page

    @page_router.put("/{page_id}", response_model=PageOut)
    def update_page_route(self, page_id: str, update_data: PageUpdate):
        updated = crud.update_page(self.db, page_id, update_data.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Page not found")
        return updated

    @page_router.delete("/{page_id}")
    def delete_page_route(self, page_id: str):
        deleted = crud.delete_page(self.db, page_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Page not found")
        return {"message": "Page deleted successfully"}


# Router export
router = page_router


# from fastapi import Depends,HTTPException
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# from typing import List
# import services.page_crud as crud
# from fastapi_utils.cbv import cbv
# from fastapi_utils.inferring_router import InferringRouter
# from config import get_db



# page_router = InferringRouter()


# class PageCreate(BaseModel):
#     page_name: str
#     user_name: str
#     page_route: str

# class PageUpdate(BaseModel):
#     page_name: str
    
# @cbv(page_router)
# class PageModelRoutes:
#     db:Session = Depends(get_db)
#     page_router.tags =["Pages"]
        
#     @page_router.post("/")
#     def create_page_route(page: PageCreate, db: Session = Depends(get_db)):
#         return crud.create_page(db, page.dict())

#     @page_router.get("/")
#     def get_all_pages(db: Session = Depends(get_db)):
#         return crud.get_pages(db)

#     @page_router.get("/{page_id}")
#     def get_single_page(page_id: str, db: Session = Depends(get_db)):
#         page = crud.get_page_by_id(db, page_id)
#         if not page:
#             raise HTTPException(status_code=404, detail="Page not found")
#         return page

#     @page_router.put("/{page_id}")
#     def update_page_route(page_id: str, update_data: PageUpdate, db: Session = Depends(get_db)):
#         updated = crud.update_page(db, page_id, update_data.dict())
#         if not updated:
#             raise HTTPException(status_code=404, detail="Page not found")
#         return updated

#     @page_router.delete("/{page_id}")
#     def delete_page_route(page_id: str, db: Session = Depends(get_db)):
#         deleted = crud.delete_page(db, page_id)
#         if not deleted:
#             raise HTTPException(status_code=404, detail="Page not found")
#         return {"message": "Page deleted successfully"}
# router = page_router