from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Empresa(Base):
    __tablename__ = 'empresas'
    
    # Suponiendo que el NIT es la clave primaria por ser único
    nit = Column(String(20), primary_key=True)
    nombre = Column(String(100), nullable=False)
    stock_min_alerta = Column(Float, default=0.0)
    factor_holgura = Column(Float, default=0.0)

    # Relaciones
    tanques = relationship("Tanque", back_populates="empresa")
    ventas = relationship("Venta", back_populates="empresa")
    ingresos = relationship("Ingreso", back_populates="empresa")

class Tanque(Base):
    __tablename__ = 'tanques'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    combustible = Column(String(50), nullable=False)
    capacidad_max = Column(Float, nullable=False)
    stock_actual = Column(Float, default=0.0)
    empresa_nit = Column(String(20), ForeignKey('empresas.nit'))

    empresa = relationship("Empresa", back_populates="tanques")

class Cliente(Base):
    __tablename__ = 'clientes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    documento = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    placa = Column(String(10), nullable=True)
    tipo = Column(String(50)) # Ej: Particular, Empresa, Público

    ventas = relationship("Venta", back_populates="cliente")

class Ingreso(Base):
    __tablename__ = 'ingresos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cantidad = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    empresa_nit = Column(String(20), ForeignKey('empresas.nit'))
    tanque_id = Column(Integer, ForeignKey('tanques.id'))

    empresa = relationship("Empresa", back_populates="ingresos")

class Venta(Base):
    __tablename__ = 'ventas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cantidad = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    empresa_nit = Column(String(20), ForeignKey('empresas.nit'))
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    tanque_id = Column(Integer, ForeignKey('tanques.id'))

    empresa = relationship("Empresa", back_populates="ventas")
    cliente = relationship("Cliente", back_populates="ventas")