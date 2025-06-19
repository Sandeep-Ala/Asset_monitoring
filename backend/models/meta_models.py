#meta_models.py
from sqlalchemy import Column, Integer, String, ForeignKey,DateTime
from sqlalchemy.orm import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class Page(Base):
    __tablename__ = 'pages'

    page_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    page_name = Column(String(64), nullable=False)
    user_name = Column(String(64), nullable=False)
    page_route = Column(String(128), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class MasterModel(Base):
    __tablename__ = "master_model"
    model_id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    enable = Column(Integer, nullable=False)

class Equipment(Base):
    __tablename__ = "equipments"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    model_id = Column(Integer, ForeignKey("master_model.model_id"))
    location = Column(String(64))
    enable = Column(Integer, nullable=False)

class EquipmentSpec(Base):
    __tablename__ = "equipment_specs"
    id = Column(Integer, primary_key=True)
    eqp_id = Column(Integer, ForeignKey("equipments.id"))
    key = Column(String(64), nullable=False)
    value = Column(String(64), nullable=False)
    desc = Column(String(64))
    unit = Column(String(64))
    enable = Column(Integer, nullable=False)

class EquipmentSignal(Base):
    __tablename__ = "equipment_signals"
    id = Column(Integer, primary_key=True)
    eqp_id = Column(Integer, ForeignKey("equipments.id"))
    key = Column(String(64), nullable=False)
    value = Column(String(64))
    unit = Column(String(64))
    desc = Column(String(64))
    enable = Column(Integer, nullable=False)

class EquipmentDoc(Base):
    __tablename__ = "equipment_doc"
    id = Column(Integer, primary_key=True)
    eqp_id = Column(Integer, ForeignKey("equipments.id"))
    path = Column(String(128))
    desc = Column(String(64))

class EquipmentFilter(Base):
    __tablename__ = "equipment_filters"
    id = Column(Integer, primary_key=True)
    eqp_id = Column(Integer, ForeignKey("equipments.id"))
    filter_key = Column(String(64), nullable=False)
    filter_value = Column(String(64), nullable=False)

