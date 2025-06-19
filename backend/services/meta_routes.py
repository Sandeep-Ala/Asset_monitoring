
#meta_routes.py
from fastapi import Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import services.meta_crud as crud
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from config import get_db


meta_router = InferringRouter()

# ---------- Pydantic Schemas ----------
class MasterModelSchema(BaseModel):
    name: str
    enable: int
class MasterModelOut(MasterModelSchema):
    model_id: int
    class Config: orm_mode = True

class EquipmentSchema(BaseModel):
    name: str
    model_id: int
    location: str
    enable: int
class EquipmentOut(EquipmentSchema):
    id: int
    class Config: orm_mode = True

class EquipmentSpecSchema(BaseModel):
    eqp_id: int
    key: str
    value: str
    desc: str
    unit: str
    enable: int
class EquipmentSpecOut(EquipmentSpecSchema):
    id: int
    class Config: orm_mode = True

class EquipmentSignalSchema(BaseModel):
    eqp_id: int
    key: str
    value: str
    unit: str
    desc: str
    enable: int
class EquipmentSignalOut(EquipmentSignalSchema):
    id: int
    class Config: orm_mode = True

class EquipmentDocSchema(BaseModel):
    eqp_id: int
    path: str
    desc: str
class EquipmentDocOut(EquipmentDocSchema):
    id: int
    class Config: orm_mode = True

class EquipmentFilterSchema(BaseModel):
    eqp_id: int
    filter_key: str
    filter_value: str
class EquipmentFilterOut(EquipmentFilterSchema):
    id: int
    class Config: orm_mode = True

# ---------- CRUD Routes ----------

@cbv(meta_router)
class MasterModelRoutes:
    db: Session = Depends(get_db)
    meta_router.tags =["Master-Models"]
    @meta_router.post("/models", response_model=MasterModelOut)
    def create_model(self, item: MasterModelSchema):
        return crud.create_master_model(self.db, item.name, item.enable)

    @meta_router.get("/models", response_model=List[MasterModelOut])
    def get_models(self):
        return crud.get_all_master_models(self.db)

    @meta_router.get("/models/{model_id}", response_model=MasterModelOut)
    def get_model_by_id(self, model_id: int):
        return crud.get_master_model_by_id(self.db, model_id)

    @meta_router.put("/models/{model_id}", response_model=MasterModelOut)
    def update_model(self, model_id: int, item: MasterModelSchema):
        return crud.update_master_model(self.db, model_id, item.name, item.enable)

    @meta_router.delete("/models/{model_id}")
    def delete_model(self, model_id: int):
        return crud.delete_master_model(self.db, model_id)

@cbv(meta_router)
class EquipmentRoutes:
    db: Session = Depends(get_db)
    meta_router.tags =["Equipments"]

    @meta_router.post("/equipments", response_model=EquipmentOut)
    def create_equipment(self, item: EquipmentSchema):
        return crud.create_equipment(self.db, **item.dict())

    @meta_router.get("/equipments", response_model=List[EquipmentOut])
    def get_equipments(self):
        return crud.get_all_equipments(self.db)

    @meta_router.get("/equipments/{eqp_id}", response_model=EquipmentOut)
    def get_equipment_by_id(self, eqp_id: int):
        return crud.get_equipment_by_id(self.db, eqp_id)

    @meta_router.put("/equipments/{eqp_id}", response_model=EquipmentOut)
    def update_equipment(self, eqp_id: int, item: EquipmentSchema):
        return crud.update_equipment(self.db, eqp_id, **item.dict())

    @meta_router.delete("/equipments/{eqp_id}")
    def delete_equipment(self, eqp_id: int):
        return crud.delete_equipment(self.db, eqp_id)

@cbv(meta_router)
class EquipmentSpecRoutes:
    db: Session = Depends(get_db)
    meta_router.tags =["Specifications"]

    @meta_router.post("/specs", response_model=EquipmentSpecOut)
    def create_spec(self, item: EquipmentSpecSchema):
        return crud.create_equipment_spec(self.db, **item.dict())

    @meta_router.get("/specs", response_model=List[EquipmentSpecOut])
    def get_specs(self):
        return crud.get_all_equipment_specs(self.db)

    @meta_router.get("/specs/{spec_id}", response_model=EquipmentSpecOut)
    def get_spec_by_id(self, spec_id: int):
        return crud.get_equipment_spec_by_id(self.db, spec_id)

    @meta_router.put("/specs/{spec_id}", response_model=EquipmentSpecOut)
    def update_spec(self, spec_id: int, item: EquipmentSpecSchema):
        return crud.update_equipment_spec(self.db, spec_id, **item.dict())

    @meta_router.delete("/specs/{spec_id}")
    def delete_spec(self, spec_id: int):
        return crud.delete_equipment_spec(self.db, spec_id)

@cbv(meta_router)
class EquipmentSignalRoutes:
    db: Session = Depends(get_db)
    meta_router.tags =["Signals"]

    @meta_router.post("/signals", response_model=EquipmentSignalOut)
    def create_signal(self, item: EquipmentSignalSchema):
        return crud.create_equipment_signal(self.db, **item.dict())

    @meta_router.get("/signals", response_model=List[EquipmentSignalOut])
    def get_signals(self):
        return crud.get_all_equipment_signals(self.db)

    @meta_router.get("/signals/{signal_id}", response_model=EquipmentSignalOut)
    def get_signal_by_id(self, signal_id: int):
        return crud.get_equipment_signal_by_id(self.db, signal_id)

    @meta_router.put("/signals/{signal_id}", response_model=EquipmentSignalOut)
    def update_signal(self, signal_id: int, item: EquipmentSignalSchema):
        return crud.update_equipment_signal(self.db, signal_id, **item.dict())

    @meta_router.delete("/signals/{signal_id}")
    def delete_signal(self, signal_id: int):
        return crud.delete_equipment_signal(self.db, signal_id)

@cbv(meta_router)
class EquipmentDocRoutes:
    db: Session = Depends(get_db)
    meta_router.tags =["Documents"]

    @meta_router.post("/docs", response_model=EquipmentDocOut)
    def create_doc(self, item: EquipmentDocSchema):
        return crud.create_equipment_doc(self.db, **item.dict())

    @meta_router.get("/docs", response_model=List[EquipmentDocOut])
    def get_docs(self):
        return crud.get_all_equipment_docs(self.db)

    @meta_router.get("/docs/{doc_id}", response_model=EquipmentDocOut)
    def get_doc_by_id(self, doc_id: int):
        return crud.get_equipment_doc_by_id(self.db, doc_id)

    @meta_router.put("/docs/{doc_id}", response_model=EquipmentDocOut)
    def update_doc(self, doc_id: int, item: EquipmentDocSchema):
        return crud.update_equipment_doc(self.db, doc_id, item.path, item.desc)

    @meta_router.delete("/docs/{doc_id}")
    def delete_doc(self, doc_id: int):
        return crud.delete_equipment_doc(self.db, doc_id)

@cbv(meta_router)
class EquipmentFilterRoutes:
    db: Session = Depends(get_db)
    meta_router.tags =["Filters"]

    @meta_router.post("/filters", response_model=EquipmentFilterOut)
    def create_filter(self, item: EquipmentFilterSchema):
        return crud.create_equipment_filter(self.db, **item.dict())

    @meta_router.get("/filters", response_model=List[EquipmentFilterOut])
    def get_filters(self):
        return crud.get_all_equipment_filters(self.db)

    @meta_router.get("/filters/{filter_id}", response_model=EquipmentFilterOut)
    def get_filter_by_id(self, filter_id: int):
        return crud.get_equipment_filter_by_id(self.db, filter_id)

    @meta_router.put("/filters/{filter_id}", response_model=EquipmentFilterOut)
    def update_filter(self, filter_id: int, item: EquipmentFilterSchema):
        return crud.update_equipment_filter(self.db, filter_id, item.filter_key, item.filter_value)

    @meta_router.delete("/filters/{filter_id}")
    def delete_filter(self, filter_id: int):
        return crud.delete_equipment_filter(self.db, filter_id)

    @meta_router.get("/filters/{eq_id}",response_model=List[EquipmentFilterOut])
    def get_filters_by_eq_id(self, eq_id:int):
        return crud.get_by_eq_id(self.db,eq_id)

router = meta_router
