"""
Carvix API Server — REST API для синхронизации PyQt6 приложения и Next.js сайта
Запуск: python api_server.py  (или uvicorn api_server:app --reload --port 8000)
"""

import sqlite3
import hashlib
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Any, Dict

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from jose import JWTError, jwt
from passlib.context import CryptContext

# =============================================================================
# КОНФИГУРАЦИЯ
# =============================================================================

DB_NAME = "carvix_database.db"
SECRET_KEY = "carvix-secret-key-2024-fleet-manager"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 часа

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("carvix-api")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

# =============================================================================
# ПРИЛОЖЕНИЕ FastAPI
# =============================================================================

app = FastAPI(
    title="Carvix API",
    description="REST API для управления автопарком — синхронизация десктоп и веб",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# БАЗА ДАННЫХ
# =============================================================================

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
    finally:
        conn.close()


def db_fetchall(db: sqlite3.Connection, sql: str, params=()) -> List[Dict]:
    cursor = db.execute(sql, params)
    rows = cursor.fetchall()
    return [dict(r) for r in rows]


def db_fetchone(db: sqlite3.Connection, sql: str, params=()) -> Optional[Dict]:
    cursor = db.execute(sql, params)
    row = cursor.fetchone()
    return dict(row) if row else None

# =============================================================================
# PYDANTIC МОДЕЛИ
# =============================================================================

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role_name: str = "Пользователь"
    department: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None

class VehicleCreate(BaseModel):
    vehicle_number: str
    brand: str
    model: str
    year: int
    vin: Optional[str] = None
    fuel_type: Optional[str] = None
    category: Optional[str] = None
    mileage: int = 0
    status: str = "Активен"
    department: Optional[str] = None
    next_maintenance: Optional[str] = None
    notes: Optional[str] = None

class VehicleUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    mileage: Optional[int] = None
    status: Optional[str] = None
    department: Optional[str] = None
    next_maintenance: Optional[str] = None
    notes: Optional[str] = None

class RepairRequestCreate(BaseModel):
    vehicle_id: int
    description: str
    priority: str = "Средний"
    repair_type_id: Optional[int] = None
    defect_category_id: Optional[int] = None

class RepairRequestUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    notes: Optional[str] = None

class MaintenanceCreate(BaseModel):
    vehicle_id: int
    maintenance_type_id: Optional[int] = None
    scheduled_date: str
    estimated_cost: Optional[float] = None
    notes: Optional[str] = None

class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    type: str = "info"

class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    email_notifications: Optional[bool] = None
    auto_refresh: Optional[bool] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# =============================================================================
# JWT АВТОРИЗАЦИЯ
# =============================================================================

def verify_password_hash(plain: str, hashed: str) -> bool:
    """Проверка пароля — поддерживает SHA-256 (PyQt6), MD5 (legacy) и bcrypt"""
    # SHA-256 (используется в PyQt6 приложении)
    sha256_hash = hashlib.sha256(plain.encode()).hexdigest()
    if sha256_hash == hashed:
        return True
    # MD5 (legacy)
    md5_hash = hashlib.md5(plain.encode()).hexdigest()
    if md5_hash == hashed:
        return True
    # bcrypt (для будущих пользователей созданных через API)
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: sqlite3.Connection = Depends(get_db),
) -> Dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Не авторизован")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=401, detail="Недействительный токен")
        user_id: int = int(sub)
        if user_id is None:
            raise HTTPException(status_code=401, detail="Недействительный токен")
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    user = db_fetchone(db, """
        SELECT u.id, u.username, u.full_name, u.email, u.phone,
               u.department, u.is_active, r.name as role_name, r.name as role_display
        FROM users u LEFT JOIN roles r ON u.role_id = r.id
        WHERE u.id = ?
    """, (user_id,))
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user

# =============================================================================
# AUTH ENDPOINTS
# =============================================================================

@app.post("/api/auth/login", response_model=TokenResponse, tags=["auth"])
def login(data: LoginRequest, db: sqlite3.Connection = Depends(get_db)):
    user = db_fetchone(db, """
        SELECT u.id, u.username, u.password_hash, u.full_name, u.email, u.phone,
               u.department, u.is_active, r.name as role_name, r.name as role_display
        FROM users u LEFT JOIN roles r ON u.role_id = r.id
        WHERE u.username = ? AND u.is_active = 1
    """, (data.username,))

    if not user or not verify_password_hash(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token = create_access_token({"sub": str(user["id"])})
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    return {"access_token": token, "token_type": "bearer", "user": user_data}


@app.get("/api/auth/me", tags=["auth"])
def get_me(current_user: Dict = Depends(get_current_user)):
    return current_user


@app.post("/api/auth/change-password", tags=["auth"])
def change_password(
    data: PasswordChange,
    current_user: Dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    user = db_fetchone(db, "SELECT password_hash FROM users WHERE id = ?", (current_user["id"],))
    if not verify_password_hash(data.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Неверный текущий пароль")

    new_hash = hashlib.sha256(data.new_password.encode()).hexdigest()
    db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, current_user["id"]))
    db.commit()
    return {"success": True}

# =============================================================================
# USERS ENDPOINTS
# =============================================================================

@app.get("/api/users", tags=["users"])
def get_users(
    skip: int = 0, limit: int = 100,
    role: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_db),
    _: Dict = Depends(get_current_user),
):
    sql = """
        SELECT u.id, u.username, u.full_name, u.email, u.phone,
               u.department, u.is_active, u.created_at,
               r.name as role_name, r.description as role_display
        FROM users u LEFT JOIN roles r ON u.role_id = r.id
    """
    params = []
    if role:
        sql += " WHERE r.name = ?"
        params.append(role)
    sql += f" ORDER BY u.full_name LIMIT {limit} OFFSET {skip}"
    return db_fetchall(db, sql, params)


@app.get("/api/users/{user_id}", tags=["users"])
def get_user(user_id: int, db: sqlite3.Connection = Depends(get_db), _: Dict = Depends(get_current_user)):
    user = db_fetchone(db, """
        SELECT u.id, u.username, u.full_name, u.email, u.phone,
               u.department, u.is_active, u.created_at,
               r.name as role_name, r.description as role_display
        FROM users u LEFT JOIN roles r ON u.role_id = r.id WHERE u.id = ?
    """, (user_id,))
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@app.put("/api/users/{user_id}", tags=["users"])
def update_user(
    user_id: int, data: UserUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    admin_roles = {"admin", "Администратор", "Директор", "director"}
    if current_user["id"] != user_id and current_user.get("role_name") not in admin_roles:
        raise HTTPException(status_code=403, detail="Нет прав")
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="Нет данных для обновления")
    sets = ", ".join(f"{k} = ?" for k in fields)
    db.execute(f"UPDATE users SET {sets} WHERE id = ?", (*fields.values(), user_id))
    db.commit()
    return get_user(user_id, db, current_user)

# =============================================================================
# VEHICLES ENDPOINTS
# =============================================================================

@app.get("/api/vehicles", tags=["vehicles"])
def get_vehicles(
    skip: int = 0, limit: int = 100,
    status: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_db),
    _: Dict = Depends(get_current_user),
):
    sql = "SELECT * FROM vehicles WHERE 1=1"
    params = []
    if status:
        sql += " AND status = ?"
        params.append(status)
    sql += f" ORDER BY vehicle_number LIMIT {limit} OFFSET {skip}"
    return db_fetchall(db, sql, params)


@app.get("/api/vehicles/{vehicle_id}", tags=["vehicles"])
def get_vehicle(vehicle_id: int, db: sqlite3.Connection = Depends(get_db), _: Dict = Depends(get_current_user)):
    v = db_fetchone(db, "SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
    if not v:
        raise HTTPException(status_code=404, detail="Автомобиль не найден")
    return v


@app.post("/api/vehicles", tags=["vehicles"], status_code=201)
def create_vehicle(
    data: VehicleCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    cursor = db.execute("""
        INSERT INTO vehicles (vehicle_number, brand, model, year, vin, fuel_type,
            category, mileage, status, department, next_maintenance, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data.vehicle_number, data.brand, data.model, data.year, data.vin,
          data.fuel_type, data.category, data.mileage, data.status, data.department,
          data.next_maintenance, data.notes))
    db.commit()
    return get_vehicle(cursor.lastrowid, db, current_user)


@app.put("/api/vehicles/{vehicle_id}", tags=["vehicles"])
def update_vehicle(
    vehicle_id: int, data: VehicleUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="Нет данных")
    sets = ", ".join(f"{k} = ?" for k in fields)
    db.execute(f"UPDATE vehicles SET {sets} WHERE id = ?", (*fields.values(), vehicle_id))
    db.commit()
    return get_vehicle(vehicle_id, db, current_user)

# =============================================================================
# REPAIR REQUESTS ENDPOINTS
# =============================================================================

@app.get("/api/requests", tags=["requests"])
def get_requests(
    skip: int = 0, limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    vehicle_id: Optional[int] = None,
    created_by: Optional[int] = None,
    db: sqlite3.Connection = Depends(get_db),
    _: Dict = Depends(get_current_user),
):
    sql = """
        SELECT rr.id, rr.request_number, rr.vehicle_id, rr.description,
               rr.priority, rr.status, rr.estimated_cost, rr.actual_cost,
               rr.created_at, rr.notes, rr.created_by, rr.assigned_to,
               rr.repair_type_id, rr.defect_category_id,
               v.vehicle_number, v.brand, v.model,
               u_created.full_name as created_by_name,
               u_assigned.full_name as assigned_to_name,
               rt.name as repair_type_name,
               dc.name as defect_category_name
        FROM repair_requests rr
        LEFT JOIN vehicles v ON rr.vehicle_id = v.id
        LEFT JOIN users u_created ON rr.created_by = u_created.id
        LEFT JOIN users u_assigned ON rr.assigned_to = u_assigned.id
        LEFT JOIN repair_types rt ON rr.repair_type_id = rt.id
        LEFT JOIN defect_categories dc ON rr.defect_category_id = dc.id
        WHERE 1=1
    """
    params = []
    if status:
        sql += " AND rr.status = ?"
        params.append(status)
    if priority:
        sql += " AND rr.priority = ?"
        params.append(priority)
    if vehicle_id:
        sql += " AND rr.vehicle_id = ?"
        params.append(vehicle_id)
    if created_by:
        sql += " AND rr.created_by = ?"
        params.append(created_by)
    sql += f" ORDER BY rr.created_at DESC LIMIT {limit} OFFSET {skip}"
    return db_fetchall(db, sql, params)


@app.get("/api/requests/{request_id}", tags=["requests"])
def get_request(request_id: int, db: sqlite3.Connection = Depends(get_db), _: Dict = Depends(get_current_user)):
    r = db_fetchone(db, """
        SELECT rr.id, rr.request_number, rr.vehicle_id, rr.description,
               rr.priority, rr.status, rr.estimated_cost, rr.actual_cost,
               rr.created_at, rr.notes, rr.created_by, rr.assigned_to,
               v.vehicle_number, v.brand, v.model,
               u_created.full_name as created_by_name,
               u_assigned.full_name as assigned_to_name,
               rt.name as repair_type_name,
               dc.name as defect_category_name
        FROM repair_requests rr
        LEFT JOIN vehicles v ON rr.vehicle_id = v.id
        LEFT JOIN users u_created ON rr.created_by = u_created.id
        LEFT JOIN users u_assigned ON rr.assigned_to = u_assigned.id
        LEFT JOIN repair_types rt ON rr.repair_type_id = rt.id
        LEFT JOIN defect_categories dc ON rr.defect_category_id = dc.id
        WHERE rr.id = ?
    """, (request_id,))
    if not r:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return r


@app.post("/api/requests", tags=["requests"], status_code=201)
def create_request(
    data: RepairRequestCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    count = db_fetchone(db, "SELECT COUNT(*) as c FROM repair_requests")["c"]
    request_number = f"REQ-{datetime.now().year}-{count + 1:04d}"
    cursor = db.execute("""
        INSERT INTO repair_requests
            (request_number, vehicle_id, description, priority, status,
             created_by, repair_type_id, defect_category_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'Новая', ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (request_number, data.vehicle_id, data.description, data.priority,
          current_user["id"], data.repair_type_id, data.defect_category_id))
    db.commit()
    return get_request(cursor.lastrowid, db, current_user)


@app.put("/api/requests/{request_id}", tags=["requests"])
def update_request(
    request_id: int, data: RepairRequestUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="Нет данных")
    sets = ", ".join(f"{k} = ?" for k in fields)
    db.execute(f"UPDATE repair_requests SET {sets} WHERE id = ?", (*fields.values(), request_id))
    db.commit()
    return get_request(request_id, db, current_user)

# =============================================================================
# MAINTENANCE ENDPOINTS
# =============================================================================

@app.get("/api/maintenance", tags=["maintenance"])
def get_maintenance(
    skip: int = 0, limit: int = 100,
    status: Optional[str] = None,
    vehicle_id: Optional[int] = None,
    db: sqlite3.Connection = Depends(get_db),
    _: Dict = Depends(get_current_user),
):
    sql = """
        SELECT mr.id, mr.request_number, mr.vehicle_id, mr.description,
               mr.priority, mr.status, mr.estimated_cost, mr.actual_cost,
               mr.scheduled_date, mr.completed_at, mr.created_at, mr.notes,
               mr.assigned_to, mr.maintenance_type_id,
               v.vehicle_number, v.brand, v.model,
               mt.name as maintenance_type_name,
               u.full_name as assigned_to_name
        FROM maintenance_requests mr
        LEFT JOIN vehicles v ON mr.vehicle_id = v.id
        LEFT JOIN maintenance_types mt ON mr.maintenance_type_id = mt.id
        LEFT JOIN users u ON mr.assigned_to = u.id
        WHERE 1=1
    """
    params = []
    if status:
        sql += " AND mr.status = ?"
        params.append(status)
    if vehicle_id:
        sql += " AND mr.vehicle_id = ?"
        params.append(vehicle_id)
    sql += f" ORDER BY mr.scheduled_date DESC LIMIT {limit} OFFSET {skip}"
    return db_fetchall(db, sql, params)


@app.post("/api/maintenance", tags=["maintenance"], status_code=201)
def create_maintenance(
    data: MaintenanceCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    count = db_fetchone(db, "SELECT COUNT(*) as c FROM maintenance_requests")["c"]
    request_number = f"MNT-{datetime.now().year}-{count + 1:04d}"
    cursor = db.execute("""
        INSERT INTO maintenance_requests
            (request_number, vehicle_id, maintenance_type_id, scheduled_date,
             estimated_cost, notes, status, priority, created_by)
        VALUES (?, ?, ?, ?, ?, ?, 'Запланировано', 'Средний', ?)
    """, (request_number, data.vehicle_id, data.maintenance_type_id,
          data.scheduled_date, data.estimated_cost, data.notes, current_user["id"]))
    db.commit()
    r = db_fetchone(db, "SELECT * FROM maintenance_requests WHERE id = ?", (cursor.lastrowid,))
    return r


class MaintenanceUpdate(BaseModel):
    status: Optional[str] = None
    actual_cost: Optional[float] = None
    completed_at: Optional[str] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None

@app.put("/api/maintenance/{maintenance_id}", tags=["maintenance"])
def update_maintenance(
    maintenance_id: int, data: MaintenanceUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="Нет данных")
    sets = ", ".join(f"{k} = ?" for k in fields)
    db.execute(f"UPDATE maintenance_requests SET {sets} WHERE id = ?", (*fields.values(), maintenance_id))
    db.commit()
    return db_fetchone(db, "SELECT * FROM maintenance_requests WHERE id = ?", (maintenance_id,))

# =============================================================================
# PARTS ENDPOINTS
# =============================================================================

@app.get("/api/parts", tags=["parts"])
def get_parts(
    skip: int = 0, limit: int = 100,
    low_stock: bool = False,
    db: sqlite3.Connection = Depends(get_db),
    _: Dict = Depends(get_current_user),
):
    sql = """
        SELECT p.id, p.part_number, p.name, p.description, p.category,
               p.price, p.quantity, p.min_quantity, p.location, p.is_active,
               s.name as supplier_name
        FROM parts p LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE p.is_active = 1
    """
    if low_stock:
        sql += " AND p.quantity <= p.min_quantity"
    sql += f" ORDER BY p.name LIMIT {limit} OFFSET {skip}"
    return db_fetchall(db, sql, [])


@app.get("/api/parts/{part_id}", tags=["parts"])
def get_part(part_id: int, db: sqlite3.Connection = Depends(get_db), _: Dict = Depends(get_current_user)):
    p = db_fetchone(db, """
        SELECT p.id, p.part_number, p.name, p.description, p.category,
               p.price, p.quantity, p.min_quantity, p.location, p.is_active,
               s.name as supplier_name
        FROM parts p LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE p.id = ?
    """, (part_id,))
    if not p:
        raise HTTPException(status_code=404, detail="Запчасть не найдена")
    return p

# =============================================================================
# NOTIFICATIONS ENDPOINTS
# =============================================================================

@app.get("/api/notifications", tags=["notifications"])
def get_notifications(
    skip: int = 0, limit: int = 50,
    unread_only: bool = False,
    db: sqlite3.Connection = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    sql = "SELECT * FROM notifications WHERE user_id = ?"
    params = [current_user["id"]]
    if unread_only:
        sql += " AND is_read = 0"
    sql += f" ORDER BY created_at DESC LIMIT {limit} OFFSET {skip}"
    return db_fetchall(db, sql, params)


@app.post("/api/notifications/{notif_id}/read", tags=["notifications"])
def mark_notification_read(
    notif_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    db.execute(
        "UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?",
        (notif_id, current_user["id"])
    )
    db.commit()
    return {"success": True}


@app.post("/api/notifications/read-all", tags=["notifications"])
def mark_all_read(db: sqlite3.Connection = Depends(get_db), current_user: Dict = Depends(get_current_user)):
    db.execute(
        "UPDATE notifications SET is_read = 1 WHERE user_id = ?",
        (current_user["id"],)
    )
    db.commit()
    return {"success": True}

# =============================================================================
# SETTINGS ENDPOINTS
# =============================================================================

@app.get("/api/settings", tags=["settings"])
def get_settings(db: sqlite3.Connection = Depends(get_db), current_user: Dict = Depends(get_current_user)):
    s = db_fetchone(db, "SELECT * FROM user_settings WHERE user_id = ?", (current_user["id"],))
    if not s:
        db.execute(
            "INSERT INTO user_settings (user_id, theme) VALUES (?, 'dark')",
            (current_user["id"],)
        )
        db.commit()
        s = db_fetchone(db, "SELECT * FROM user_settings WHERE user_id = ?", (current_user["id"],))
    return s


@app.put("/api/settings", tags=["settings"])
def update_settings(
    data: SettingsUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    existing = db_fetchone(db, "SELECT id FROM user_settings WHERE user_id = ?", (current_user["id"],))
    fields = {k: v for k, v in data.model_dump().items() if v is not None}

    if existing:
        if fields:
            sets = ", ".join(f"{k} = ?" for k in fields)
            db.execute(
                f"UPDATE user_settings SET {sets}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (*fields.values(), current_user["id"])
            )
    else:
        db.execute(
            "INSERT INTO user_settings (user_id, theme) VALUES (?, ?)",
            (current_user["id"], fields.get("theme", "dark"))
        )
    db.commit()
    return get_settings(db, current_user)

# =============================================================================
# ANALYTICS ENDPOINTS
# =============================================================================

@app.get("/api/analytics/dashboard", tags=["analytics"])
def get_dashboard_analytics(
    db: sqlite3.Connection = Depends(get_db),
    _: Dict = Depends(get_current_user),
):
    total_vehicles = db_fetchone(db, "SELECT COUNT(*) as c FROM vehicles")["c"]
    active_vehicles = db_fetchone(db, "SELECT COUNT(*) as c FROM vehicles WHERE status = 'Активен'")["c"]
    in_repair = db_fetchone(db, "SELECT COUNT(*) as c FROM vehicles WHERE status = 'На ремонте'")["c"]

    total_requests = db_fetchone(db, "SELECT COUNT(*) as c FROM repair_requests")["c"]
    new_requests = db_fetchone(db, "SELECT COUNT(*) as c FROM repair_requests WHERE status = 'Новая'")["c"]
    in_progress = db_fetchone(db, "SELECT COUNT(*) as c FROM repair_requests WHERE status = 'В работе'")["c"]
    completed = db_fetchone(db, "SELECT COUNT(*) as c FROM repair_requests WHERE status = 'Выполнена'")["c"]

    total_maintenance = db_fetchone(db, "SELECT COUNT(*) as c FROM maintenance_requests")["c"]
    planned_maintenance = db_fetchone(db, "SELECT COUNT(*) as c FROM maintenance_requests WHERE status = 'Запланировано'")["c"]

    total_parts = db_fetchone(db, "SELECT COUNT(*) as c FROM parts WHERE is_active = 1")["c"]
    low_stock = db_fetchone(db, "SELECT COUNT(*) as c FROM parts WHERE quantity <= min_quantity AND is_active = 1")["c"]

    total_cost = db_fetchone(db, "SELECT COALESCE(SUM(actual_cost), 0) as s FROM repair_requests WHERE actual_cost IS NOT NULL")["s"]

    requests_by_status = db_fetchall(db, """
        SELECT status, COUNT(*) as count FROM repair_requests GROUP BY status
    """)
    vehicles_by_status = db_fetchall(db, """
        SELECT status, COUNT(*) as count FROM vehicles GROUP BY status
    """)
    requests_by_month = db_fetchall(db, """
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
        FROM repair_requests
        WHERE created_at >= date('now', '-6 months')
        GROUP BY month ORDER BY month
    """)

    return {
        "vehicles": {"total": total_vehicles, "active": active_vehicles, "in_repair": in_repair},
        "requests": {"total": total_requests, "new": new_requests, "in_progress": in_progress, "completed": completed},
        "maintenance": {"total": total_maintenance, "planned": planned_maintenance},
        "parts": {"total": total_parts, "low_stock": low_stock},
        "total_cost": total_cost,
        "charts": {
            "requests_by_status": requests_by_status,
            "vehicles_by_status": vehicles_by_status,
            "requests_by_month": requests_by_month,
        }
    }


@app.get("/api/analytics/costs", tags=["analytics"])
def get_cost_analytics(
    db: sqlite3.Connection = Depends(get_db),
    _: Dict = Depends(get_current_user),
):
    monthly_costs = db_fetchall(db, """
        SELECT strftime('%Y-%m', created_at) as month,
               SUM(actual_cost) as total_cost,
               COUNT(*) as request_count
        FROM repair_requests
        WHERE actual_cost IS NOT NULL
        GROUP BY month ORDER BY month DESC LIMIT 12
    """)
    top_vehicles = db_fetchall(db, """
        SELECT v.vehicle_number, v.brand, v.model,
               SUM(rr.actual_cost) as total_cost,
               COUNT(rr.id) as request_count
        FROM repair_requests rr
        JOIN vehicles v ON rr.vehicle_id = v.id
        WHERE rr.actual_cost IS NOT NULL
        GROUP BY v.id ORDER BY total_cost DESC LIMIT 10
    """)
    return {"monthly_costs": monthly_costs, "top_vehicles": top_vehicles}


# =============================================================================
# СПРАВОЧНИКИ ENDPOINTS
# =============================================================================

@app.get("/api/references/roles", tags=["references"])
def get_roles(db: sqlite3.Connection = Depends(get_db), _: Dict = Depends(get_current_user)):
    return db_fetchall(db, "SELECT * FROM roles ORDER BY name")


@app.get("/api/references/repair-types", tags=["references"])
def get_repair_types(db: sqlite3.Connection = Depends(get_db), _: Dict = Depends(get_current_user)):
    return db_fetchall(db, "SELECT * FROM repair_types WHERE is_active = 1 ORDER BY name")


@app.get("/api/references/maintenance-types", tags=["references"])
def get_maintenance_types(db: sqlite3.Connection = Depends(get_db), _: Dict = Depends(get_current_user)):
    return db_fetchall(db, "SELECT * FROM maintenance_types WHERE is_active = 1 ORDER BY name")


@app.get("/api/references/defect-categories", tags=["references"])
def get_defect_categories(db: sqlite3.Connection = Depends(get_db), _: Dict = Depends(get_current_user)):
    return db_fetchall(db, "SELECT * FROM defect_categories WHERE is_active = 1 ORDER BY name")


@app.get("/api/references/suppliers", tags=["references"])
def get_suppliers(db: sqlite3.Connection = Depends(get_db), _: Dict = Depends(get_current_user)):
    return db_fetchall(db, "SELECT * FROM suppliers WHERE is_active = 1 ORDER BY name")


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/api/health", tags=["system"])
def health_check(db: sqlite3.Connection = Depends(get_db)):
    try:
        db_fetchone(db, "SELECT 1")
        return {"status": "ok", "database": DB_NAME, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ЗАПУСК
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Запуск Carvix API сервера на http://localhost:8000")
    logger.info("📖 Документация: http://localhost:8000/docs")
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
