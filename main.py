from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func
# Asegúrate de importar tus modelos y la configuración de sesión
from database import SessionLocal  # Ejemplo de configuración
from models import Venta, Cliente, Tanque, Empresa

app = FastAPI()

# Dependencia para obtener la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/registrar-venta/")
def registrar_venta(placa: str, cantidad: float, tanque_id: int, db: Session = Depends(get_db)):
    # 1. Buscar al cliente por placa
    cliente = db.query(Cliente).filter(Cliente.placa == placa).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # 2. Calcular promedio de compras de los últimos 28 días
    fecha_limite = datetime.utcnow() - timedelta(days=28)
    promedio_compras = db.query(func.avg(Venta.cantidad)).filter(
        Venta.cliente_id == cliente.id,
        Venta.fecha >= fecha_limite
    ).scalar()

    # Si es nuevo (promedio es None), usamos un cupo base (ejemplo: 50.0)
    cupo_permitido = (promedio_compras if promedio_compras else 50.0)
    
    # 3. Obtener factor de holgura de la empresa (asumiendo que hay una empresa)
    empresa = db.query(Empresa).first()
    factor = empresa.factor_holgura if empresa else 0.10
    
    # 4. Validar límite: cupo + 10% (holgura)
    if cantidad > (cupo_permitido * (1 + factor)):
        raise HTTPException(status_code=400, detail="La venta supera el cupo permitido con holgura")

    # 5. Validar stock del tanque
    tanque = db.query(Tanque).filter(Tanque.id == tanque_id).first()
    if not tanque or tanque.stock_actual < cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente en el tanque")

    # 6. Registrar Venta y restar stock
    nueva_venta = Venta(
        cantidad=cantidad,
        cliente_id=cliente.id,
        tanque_id=tanque.id,
        empresa_nit=empresa.nit if empresa else None
    )
    
    tanque.stock_actual -= cantidad
    
    db.add(nueva_venta)
    db.commit()
    db.refresh(nueva_venta)
    
    return {"mensaje": "Venta registrada con éxito", "venta_id": nueva_venta.id}