from sqlalchemy.orm import Session
from models.meta_models import *

# ---------- MasterModel ----------
def create_master_model(db: Session, name: str, enable: int):
    model = MasterModel(name=name, enable=enable)
    db.add(model)
    db.commit()
    db.refresh(model)
    return model

def get_master_model_by_id(db: Session, model_id: int):
    return db.query(MasterModel).filter(MasterModel.model_id == model_id).first()

def get_all_master_models(db: Session):
    return db.query(MasterModel).all()

def update_master_model(db: Session, model_id: int, name: str, enable: int):
    model = db.query(MasterModel).filter(MasterModel.model_id == model_id).first()
    if model:
        model.name = name
        model.enable = enable
        db.commit()
    return model

def delete_master_model(db: Session, model_id: int):
    model = db.query(MasterModel).filter(MasterModel.model_id == model_id).first()
    if model:
        db.delete(model)
        db.commit()
    return model

# ---------- Equipment ----------
def create_equipment(db: Session, name: str, model_id: int, location: str, enable: int):
    eqp = Equipment(name=name, model_id=model_id, location=location, enable=enable)
    db.add(eqp)
    db.commit()
    db.refresh(eqp)
    return eqp

def get_all_equipments(db: Session):
    return db.query(Equipment).all()

def get_equipment_by_id(db: Session, eqp_id: int):
    return db.query(Equipment).filter(Equipment.id == eqp_id).first()

def update_equipment(db: Session, eqp_id: int, name: str, model_id: int, location: str, enable: int):
    eqp = db.query(Equipment).filter(Equipment.id == eqp_id).first()
    if eqp:
        eqp.name = name
        eqp.model_id = model_id
        eqp.location = location
        eqp.enable = enable
        db.commit()
    return eqp

def delete_equipment(db: Session, eqp_id: int):
    eqp = db.query(Equipment).filter(Equipment.id == eqp_id).first()
    if eqp:
        db.delete(eqp)
        db.commit()
    return eqp

# ---------- EquipmentSpec ----------
def create_equipment_spec(db: Session, eqp_id: int, key: str, value: str, desc: str, unit: str, enable: int):
    spec = EquipmentSpec(eqp_id=eqp_id, key=key, value=value, desc=desc, unit=unit, enable=enable)
    db.add(spec)
    db.commit()
    db.refresh(spec)
    return spec

def get_all_equipment_specs(db: Session):
    return db.query(EquipmentSpec).all()

def get_equipment_spec_by_id(db: Session, spec_id: int):
    return db.query(EquipmentSpec).filter(EquipmentSpec.id == spec_id).first()

def update_equipment_spec(db: Session, spec_id: int, key: str, value: str, desc: str, unit: str, enable: int):
    spec = db.query(EquipmentSpec).filter(EquipmentSpec.id == spec_id).first()
    if spec:
        spec.key = key
        spec.value = value
        spec.desc = desc
        spec.unit = unit
        spec.enable = enable
        db.commit()
    return spec

def delete_equipment_spec(db: Session, spec_id: int):
    spec = db.query(EquipmentSpec).filter(EquipmentSpec.id == spec_id).first()
    if spec:
        db.delete(spec)
        db.commit()
    return spec

# ---------- EquipmentSignal ----------
def create_equipment_signal(db: Session, eqp_id: int, key: str, value: str, unit: str, desc: str, enable: int):
    signal = EquipmentSignal(eqp_id=eqp_id, key=key, value=value, unit=unit, desc=desc, enable=enable)
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal

def get_all_equipment_signals(db: Session):
    return db.query(EquipmentSignal).all()

def get_equipment_signal_by_id(db: Session, signal_id: int):
    return db.query(EquipmentSignal).filter(EquipmentSignal.id == signal_id).first()

def update_equipment_signal(db: Session, signal_id: int, key: str, value: str, unit: str, desc: str, enable: int):
    signal = db.query(EquipmentSignal).filter(EquipmentSignal.id == signal_id).first()
    if signal:
        signal.key = key
        signal.value = value
        signal.unit = unit
        signal.desc = desc
        signal.enable = enable
        db.commit()
    return signal

def delete_equipment_signal(db: Session, signal_id: int):
    signal = db.query(EquipmentSignal).filter(EquipmentSignal.id == signal_id).first()
    if signal:
        db.delete(signal)
        db.commit()
    return signal

# ---------- EquipmentDoc ----------
def create_equipment_doc(db: Session, eqp_id: int, path: str, desc: str):
    doc = EquipmentDoc(eqp_id=eqp_id, path=path, desc=desc)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_all_equipment_docs(db: Session):
    return db.query(EquipmentDoc).all()

def update_equipment_doc(db: Session, doc_id: int, path: str, desc: str):
    doc = db.query(EquipmentDoc).filter(EquipmentDoc.id == doc_id).first()
    if doc:
        doc.path = path
        doc.desc = desc
        db.commit()
    return doc

def get_equipment_doc_by_id(db: Session, doc_id: int):
    return db.query(EquipmentDoc).filter(EquipmentDoc.id == doc_id).first()

def delete_equipment_doc(db: Session, doc_id: int):
    doc = db.query(EquipmentDoc).filter(EquipmentDoc.id == doc_id).first()
    if doc:
        db.delete(doc)
        db.commit()
    return doc

# ---------- EquipmentFilter ----------
def create_equipment_filter(db: Session, eqp_id: int, filter_key: str, filter_value: str):
    filter_row = EquipmentFilter(eqp_id=eqp_id, filter_key=filter_key, filter_value=filter_value)
    db.add(filter_row)
    db.commit()
    db.refresh(filter_row)
    return filter_row

def get_all_equipment_filters(db: Session):
    return db.query(EquipmentFilter).all()

def get_by_eq_id(db:Session,eq_id:int):
    return db.query(EquipmentFilter).filter(EquipmentFilter.eqp_id == eq_id).all()

def get_equipment_filter_by_id(db: Session, filter_id: int):
    return db.query(EquipmentFilter).filter(EquipmentFilter.id == filter_id).first()
    
def update_equipment_filter(db: Session, filter_id: int, filter_key: str, filter_value: str):
    filter_row = db.query(EquipmentFilter).filter(EquipmentFilter.id == filter_id).first()
    if filter_row:
        filter_row.filter_key = filter_key
        filter_row.filter_value = filter_value
        db.commit()
    return filter_row

def delete_equipment_filter(db: Session, filter_id: int):
    filter_row = db.query(EquipmentFilter).filter(EquipmentFilter.id == filter_id).first()
    if filter_row:
        db.delete(filter_row)
        db.commit()
    return filter_row
