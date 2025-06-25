# services/datasource_crud.py

from sqlalchemy.orm import Session
from models.datasource_models import DataConnection, ConnectionConfig
from datetime import datetime
from typing import List, Dict, Optional

# ---------- DataConnection CRUD ----------

def create_data_connection(db: Session, name: str, db_type: str, description: str = None):
    """Create a new data connection"""
    connection = DataConnection(
        name=name,
        db_type=db_type,
        description=description,
        status="inactive"
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection

def get_all_data_connections(db: Session):
    """Get all data connections"""
    return db.query(DataConnection).all()

def get_data_connection_by_id(db: Session, connection_id: str):
    """Get data connection by ID"""
    return db.query(DataConnection).filter(DataConnection.id == connection_id).first()

def get_data_connection_by_name(db: Session, name: str):
    """Get data connection by name"""
    return db.query(DataConnection).filter(DataConnection.name == name).first()

def update_data_connection(db: Session, connection_id: str, name: str = None, 
                          db_type: str = None, description: str = None, status: str = None):
    """Update data connection"""
    connection = get_data_connection_by_id(db, connection_id)
    if connection:
        if name is not None:
            connection.name = name
        if db_type is not None:
            connection.db_type = db_type
        if description is not None:
            connection.description = description
        if status is not None:
            connection.status = status
        connection.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(connection)
    return connection

def delete_data_connection(db: Session, connection_id: str):
    """Delete data connection and its configs"""
    # First delete all connection configs
    db.query(ConnectionConfig).filter(ConnectionConfig.connection_id == connection_id).delete()
    
    # Then delete the connection
    connection = get_data_connection_by_id(db, connection_id)
    if connection:
        db.delete(connection)
        db.commit()
    return connection

# ---------- ConnectionConfig CRUD ----------

def create_connection_config(db: Session, connection_id: str, config_key: str, config_value: str):
    """Create a new connection config"""
    config = ConnectionConfig(
        connection_id=connection_id,
        config_key=config_key,
        config_value=config_value
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config

def get_connection_configs(db: Session, connection_id: str):
    """Get all configs for a connection"""
    return db.query(ConnectionConfig).filter(ConnectionConfig.connection_id == connection_id).all()

def get_connection_config_dict(db: Session, connection_id: str) -> Dict[str, str]:
    """Get connection configs as dictionary"""
    configs = get_connection_configs(db, connection_id)
    return {config.config_key: config.config_value for config in configs}

def update_connection_config(db: Session, connection_id: str, config_key: str, config_value: str):
    """Update or create connection config"""
    config = db.query(ConnectionConfig).filter(
        ConnectionConfig.connection_id == connection_id,
        ConnectionConfig.config_key == config_key
    ).first()
    
    if config:
        config.config_value = config_value
        config.updated_at = datetime.utcnow()
    else:
        config = ConnectionConfig(
            connection_id=connection_id,
            config_key=config_key,
            config_value=config_value
        )
        db.add(config)
    
    db.commit()
    db.refresh(config)
    return config

def delete_connection_configs(db: Session, connection_id: str):
    """Delete all configs for a connection"""
    configs = db.query(ConnectionConfig).filter(ConnectionConfig.connection_id == connection_id).all()
    for config in configs:
        db.delete(config)
    db.commit()
    return len(configs)

def save_connection_configs_batch(db: Session, connection_id: str, configs: Dict[str, str]):
    """Save multiple connection configs at once"""
    # Delete existing configs
    delete_connection_configs(db, connection_id)
    
    # Create new configs
    for key, value in configs.items():
        create_connection_config(db, connection_id, key, value)
    
    return True