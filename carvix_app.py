"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        CARVIX - AUTOMANAGER v1.0                              ║
║          Информационная система управления ремонтом и ТО автопарка           ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Роли системы:
- Администратор: полный доступ, управление пользователями и справочниками
- Директор: аналитика и управленческие решения
- Главный механик: управление ремонтным процессом
- Механик: выполнение ремонтных работ
- Диспетчер: регистрация и сопровождение заявок
- Аналитик: анализ данных и отчеты
- Пользователь: создание заявок на ремонт
"""

import sys
import os
import sqlite3
import json
import subprocess
import hashlib
import logging
import traceback
from datetime import datetime, timedelta
from functools import partial
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import random
import string

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QStackedWidget, QLabel, QPushButton, QLineEdit,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QFormLayout, QTextEdit, QDateEdit,
    QTimeEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox,
    QSplitter, QFrame, QScrollArea, QTabWidget, QFileDialog,
    QProgressBar, QStatusBar, QToolBar, QMenu, QSystemTrayIcon,
    QGraphicsDropShadowEffect, QSizePolicy, QSpacerItem,
    QGraphicsOpacityEffect, QGraphicsColorizeEffect, QStyleFactory,
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QSize,
    QParallelAnimationGroup, QSequentialAnimationGroup, pyqtSignal,
    QThread, QDate, QTime, QDateTime, QRect, QMargins, QObject
)
from PyQt6.QtGui import (
    QFont, QIcon, QPixmap, QPainter, QColor, QLinearGradient,
    QBrush, QPen, QFontDatabase, QCursor, QKeySequence, QAction,
    QPalette, QImage, QTransform, QMovie
)

# Дополнительные библиотеки
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# =============================================================================
# КОНФИГУРАЦИЯ
# =============================================================================

class Config:
    APP_NAME = "Carvix - AutoManager"
    APP_VERSION = "1.0.0"
    DB_NAME = "carvix_database.db"

    # Design System: Linear / Vercel / Notion dark
    COLORS = {
        # Backgrounds
        'bg_primary':    '#09090F',
        'bg_secondary':  '#0F0F1A',
        'bg_card':       '#13131F',
        'bg_elevated':   '#1A1A2A',
        'bg_hover':      '#1E1E30',
        'bg_input':      '#0F0F1A',
        # Accent — Indigo
        'accent':        '#6366F1',
        'accent_light':  '#818CF8',
        'accent_dark':   '#4F46E5',
        'accent_glow':   '#6366F125',
        # Semantic
        'success':       '#10B981',
        'success_bg':    '#10B98115',
        'error':         '#EF4444',
        'error_bg':      '#EF444415',
        'warning':       '#F59E0B',
        'warning_bg':    '#F59E0B15',
        'info':          '#38BDF8',
        'info_bg':       '#38BDF815',
        # Text
        'text_primary':  '#F1F5F9',
        'text_secondary':'#8892A4',
        'text_muted':    '#4B5563',
        'text_disabled': '#2D3748',
        # Borders
        'border':        '#1E1E30',
        'divider':       '#141422',
        # Legacy aliases
        'accent_cyan':   '#6366F1',
        'accent_pink':   '#EC4899',
        'accent_purple': '#8B5CF6',
        'accent_green':  '#10B981',
        'accent_orange': '#F97316',
        'accent_yellow': '#F59E0B',
    }

    STATUS_NEW = 'Новая'
    STATUS_ACCEPTED = 'Принята'
    STATUS_IN_PROGRESS = 'В работе'
    STATUS_WAITING_PARTS = 'Ожидает запчасти'
    STATUS_COMPLETED = 'Выполнена'
    STATUS_CLOSED = 'Закрыта'

    STATUS_COLORS = {
        STATUS_NEW:           '#38BDF8',
        STATUS_ACCEPTED:      '#818CF8',
        STATUS_IN_PROGRESS:   '#F59E0B',
        STATUS_WAITING_PARTS: '#A78BFA',
        STATUS_COMPLETED:     '#10B981',
        STATUS_CLOSED:        '#4B5563',
    }

    PRIORITY_LOW = 'Низкий'
    PRIORITY_MEDIUM = 'Средний'
    PRIORITY_HIGH = 'Высокий'
    PRIORITY_CRITICAL = 'Критический'

    PRIORITY_COLORS = {
        PRIORITY_LOW:      '#4B5563',
        PRIORITY_MEDIUM:   '#38BDF8',
        PRIORITY_HIGH:     '#F59E0B',
        PRIORITY_CRITICAL: '#EF4444',
    }

    # Светлая тема
    COLORS_LIGHT = {
        'bg_primary':    '#FFFFFF',
        'bg_secondary':  '#F8FAFC',
        'bg_card':       '#FFFFFF',
        'bg_elevated':   '#FFFFFF',
        'bg_hover':      '#F1F5F9',
        'bg_input':      '#F8FAFC',
        'accent':        '#6366F1',
        'accent_light':  '#818CF8',
        'accent_dark':   '#4F46E5',
        'accent_glow':   '#6366F115',
        'success':       '#10B981',
        'success_bg':    '#10B98110',
        'error':         '#EF4444',
        'error_bg':      '#EF444410',
        'warning':       '#F59E0B',
        'warning_bg':    '#F59E0B10',
        'info':          '#0EA5E9',
        'info_bg':       '#0EA5E910',
        'text_primary':  '#0F172A',
        'text_secondary':'#475569',
        'text_muted':    '#94A3B8',
        'text_disabled': '#CBD5E1',
        'border':        '#E2E8F0',
        'divider':       '#F1F5F9',
        'accent_cyan':   '#6366F1',
        'accent_pink':   '#EC4899',
        'accent_purple': '#8B5CF6',
        'accent_green':  '#10B981',
        'accent_orange': '#F97316',
        'accent_yellow': '#F59E0B',
    }


class ThemeManager:
    """Менеджер тем приложения"""
    
    @staticmethod
    def get_colors(theme='dark'):
        """Получить цветовую схему для указанной темы"""
        if theme == 'light':
            return Config.COLORS_LIGHT
        return Config.COLORS
    
    @staticmethod
    def apply_theme(theme='dark'):
        """Применить тему к Config.COLORS"""
        if theme == 'light':
            Config.COLORS = Config.COLORS_LIGHT.copy()
        else:
            Config.COLORS = {
                'bg_primary':    '#09090F',
                'bg_secondary':  '#0F0F1A',
                'bg_card':       '#13131F',
                'bg_elevated':   '#1A1A2A',
                'bg_hover':      '#1E1E30',
                'bg_input':      '#0F0F1A',
                'accent':        '#6366F1',
                'accent_light':  '#818CF8',
                'accent_dark':   '#4F46E5',
                'accent_glow':   '#6366F125',
                'success':       '#10B981',
                'success_bg':    '#10B98115',
                'error':         '#EF4444',
                'error_bg':      '#EF444415',
                'warning':       '#F59E0B',
                'warning_bg':    '#F59E0B15',
                'info':          '#38BDF8',
                'info_bg':       '#38BDF815',
                'text_primary':  '#F1F5F9',
                'text_secondary':'#8892A4',
                'text_muted':    '#4B5563',
                'text_disabled': '#2D3748',
                'border':        '#1E1E30',
                'divider':       '#141422',
                'accent_cyan':   '#6366F1',
                'accent_pink':   '#EC4899',
                'accent_purple': '#8B5CF6',
                'accent_green':  '#10B981',
                'accent_orange': '#F97316',
                'accent_yellow': '#F59E0B',
            }

# =============================================================================
# FIREBASE AUTHENTICATION
# =============================================================================

try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

class FirebaseAuth:
    """Firebase Email/Password auth via Identity Toolkit REST API"""

    API_KEY = "AIzaSyB1Qcih38nxUyKZsbqgo4o22RmEBDwuINw"
    BASE = "https://identitytoolkit.googleapis.com/v1/accounts"

    _ERRORS = {
        'INVALID_LOGIN_CREDENTIALS':  'Неверный email или пароль',
        'EMAIL_NOT_FOUND':            'Пользователь с таким email не найден',
        'INVALID_PASSWORD':           'Неверный пароль',
        'USER_DISABLED':              'Аккаунт заблокирован администратором',
        'EMAIL_EXISTS':               'Этот email уже зарегистрирован',
        'WEAK_PASSWORD':              'Пароль слишком короткий (минимум 6 символов)',
        'INVALID_EMAIL':              'Неверный формат email',
        'TOO_MANY_ATTEMPTS_TRY_LATER':'Слишком много попыток. Попробуйте позже',
        'OPERATION_NOT_ALLOWED':      'Авторизация через email отключена в Firebase',
    }

    @classmethod
    def _translate(cls, msg: str) -> str:
        for key, text in cls._ERRORS.items():
            if key in msg:
                return text
        return f'Ошибка аутентификации: {msg}'

    @classmethod
    def sign_in(cls, email: str, password: str) -> tuple:
        """Вход. Возвращает (firebase_uid, id_token). При ошибке — Exception."""
        if not _REQUESTS_AVAILABLE:
            raise Exception("Библиотека requests не установлена.\nВыполните: pip install requests")
        resp = _requests.post(
            f"{cls.BASE}:signInWithPassword?key={cls.API_KEY}",
            json={"email": email, "password": password, "returnSecureToken": True},
            timeout=10
        )
        data = resp.json()
        if "error" in data:
            raise Exception(cls._translate(data["error"].get("message", "")))
        return data["localId"], data["idToken"]

    @classmethod
    def sign_up(cls, email: str, password: str) -> tuple:
        """Регистрация. Возвращает (firebase_uid, id_token). При ошибке — Exception."""
        if not _REQUESTS_AVAILABLE:
            raise Exception("Библиотека requests не установлена.\nВыполните: pip install requests")
        resp = _requests.post(
            f"{cls.BASE}:signUp?key={cls.API_KEY}",
            json={"email": email, "password": password, "returnSecureToken": True},
            timeout=10
        )
        data = resp.json()
        if "error" in data:
            raise Exception(cls._translate(data["error"].get("message", "")))
        return data["localId"], data["idToken"]

    @classmethod
    def sign_in_with_google(cls) -> tuple:
        """Google OAuth2 sign-in (PKCE, Desktop flow).
        Возвращает (firebase_uid, email, display_name). При ошибке — Exception.
        Требует файл oauth_client.json (тип Desktop) из Google Cloud Console.
        """
        if not _REQUESTS_AVAILABLE:
            raise Exception("Библиотека requests не установлена.")
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError:
            raise Exception(
                "Библиотека google-auth-oauthlib не установлена.\n"
                "Выполните: pip install google-auth-oauthlib"
            )

        client_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'oauth_client.json')
        if not os.path.exists(client_file):
            raise Exception(
                "Файл oauth_client.json не найден.\n\n"
                "Как получить:\n"
                "1. Зайдите в console.cloud.google.com\n"
                "2. APIs & Services → Credentials\n"
                "3. Create Credentials → OAuth 2.0 Client ID\n"
                "4. Тип приложения: Desktop app\n"
                "5. Скачайте JSON и сохраните как oauth_client.json\n"
                "   рядом с файлом carvix_app.py"
            )

        SCOPES = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
        ]
        flow = InstalledAppFlow.from_client_secrets_file(client_file, SCOPES)
        credentials = flow.run_local_server(port=0, open_browser=True)

        id_token = credentials.id_token
        if not id_token:
            raise Exception("Google не вернул id_token. Попробуйте снова.")

        resp = _requests.post(
            f"{cls.BASE}:signInWithIdp?key={cls.API_KEY}",
            json={
                "requestUri": "http://localhost",
                "postBody": f"id_token={id_token}&providerId=google.com",
                "returnSecureToken": True,
                "returnIdpCredential": True,
            },
            timeout=15,
        )
        data = resp.json()
        if "error" in data:
            raise Exception(cls._translate(data["error"].get("message", "")))

        return data["localId"], data.get("email", ""), data.get("displayName", "")

# =============================================================================
# ЛОГИРОВАНИЕ
# =============================================================================
import os as _os
_log_dir = _os.path.join(_os.environ.get('APPDATA', _os.path.expanduser('~')), 'Carvix')
_os.makedirs(_log_dir, exist_ok=True)
_log_path = _os.path.join(_log_dir, 'carvix_debug.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(_log_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Carvix')

def debug_method(func):
    def wrapper(*args, **kwargs):
        try:
            logger.debug(f"Calling {func.__name__}")
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    return wrapper

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_id(prefix=''):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}{timestamp}-{random_suffix}"

def format_currency(amount):
    return f"{amount:,.2f} ₽".replace(',', ' ')

def format_date(date_obj):
    if isinstance(date_obj, str):
        return date_obj
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%d.%m.%Y')
    if isinstance(date_obj, QDate):
        return date_obj.toString('dd.MM.yyyy')
    return str(date_obj)

# =============================================================================
# БАЗА ДАННЫХ
# =============================================================================

def get_app_data_dir():
    """Returns writable app data directory (%APPDATA%/Carvix)"""
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    path = os.path.join(appdata, 'Carvix')
    os.makedirs(path, exist_ok=True)
    return path

def get_resource_path(filename):
    """Returns path to resource file (works with PyInstaller and normal run)"""
    # PyInstaller creates a temp folder and stores path in sys._MEIPASS
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    # Normal run - look in script directory
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

class Database:
    def __init__(self, db_name=None):
        if db_name is None:
            db_name = os.path.join(get_app_data_dir(), Config.DB_NAME)
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self._migrate_firebase()
        self.seed_initial_data()
        self._clear_local_auth_users()
        self._ensure_dev_users()
        self._ensure_demo_data()

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            self.cursor.execute('PRAGMA journal_mode=WAL')
            self.cursor.execute('PRAGMA foreign_keys = ON')
            logger.info(f"Database connected: {self.db_name}")
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise

    def create_tables(self):
        tables_sql = [
            """CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                permissions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                role_id INTEGER NOT NULL,
                department TEXT,
                is_active INTEGER DEFAULT 1,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (role_id) REFERENCES roles(id)
            )""",
            """CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_number TEXT UNIQUE NOT NULL,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER,
                vin TEXT,
                category TEXT,
                department TEXT,
                mileage INTEGER DEFAULT 0,
                fuel_type TEXT,
                status TEXT DEFAULT 'В работе',
                last_maintenance DATE,
                next_maintenance DATE,
                photo_path TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS repair_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                estimated_hours REAL,
                estimated_cost REAL,
                is_active INTEGER DEFAULT 1
            )""",
            """CREATE TABLE IF NOT EXISTS maintenance_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                interval_km INTEGER,
                interval_months INTEGER,
                estimated_cost REAL,
                is_active INTEGER DEFAULT 1
            )""",
            """CREATE TABLE IF NOT EXISTS defect_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'Средний',
                is_active INTEGER DEFAULT 1
            )""",
            """CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                inn TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                supplier_id INTEGER,
                price REAL DEFAULT 0,
                quantity INTEGER DEFAULT 0,
                min_quantity INTEGER DEFAULT 0,
                location TEXT,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )""",
            """CREATE TABLE IF NOT EXISTS repair_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_number TEXT UNIQUE NOT NULL,
                vehicle_id INTEGER NOT NULL,
                created_by INTEGER NOT NULL,
                assigned_to INTEGER,
                defect_category_id INTEGER,
                repair_type_id INTEGER,
                description TEXT NOT NULL,
                priority TEXT DEFAULT 'Средний',
                status TEXT DEFAULT 'Новая',
                estimated_cost REAL,
                actual_cost REAL,
                estimated_hours REAL,
                actual_hours REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accepted_at TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                closed_at TIMESTAMP,
                photo_before TEXT,
                photo_after TEXT,
                notes TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
                FOREIGN KEY (created_by) REFERENCES users(id),
                FOREIGN KEY (assigned_to) REFERENCES users(id),
                FOREIGN KEY (defect_category_id) REFERENCES defect_categories(id),
                FOREIGN KEY (repair_type_id) REFERENCES repair_types(id)
            )""",
            """CREATE TABLE IF NOT EXISTS maintenance_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_number TEXT UNIQUE NOT NULL,
                vehicle_id INTEGER NOT NULL,
                created_by INTEGER NOT NULL,
                assigned_to INTEGER,
                maintenance_type_id INTEGER,
                description TEXT,
                priority TEXT DEFAULT 'Средний',
                status TEXT DEFAULT 'Новая',
                estimated_cost REAL,
                actual_cost REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scheduled_date DATE,
                completed_at TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
                FOREIGN KEY (created_by) REFERENCES users(id),
                FOREIGN KEY (assigned_to) REFERENCES users(id),
                FOREIGN KEY (maintenance_type_id) REFERENCES maintenance_types(id)
            )""",
            """CREATE TABLE IF NOT EXISTS request_parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                part_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL,
                total_price REAL,
                installed_at TIMESTAMP,
                installed_by INTEGER,
                FOREIGN KEY (request_id) REFERENCES repair_requests(id),
                FOREIGN KEY (part_id) REFERENCES parts(id),
                FOREIGN KEY (installed_by) REFERENCES users(id)
            )""",
            """CREATE TABLE IF NOT EXISTS request_works (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                hours_spent REAL,
                cost REAL,
                performed_by INTEGER,
                performed_at TIMESTAMP,
                FOREIGN KEY (request_id) REFERENCES repair_requests(id),
                FOREIGN KEY (performed_by) REFERENCES users(id)
            )""",
            """CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT,
                file_size INTEGER,
                description TEXT,
                uploaded_by INTEGER NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (request_id) REFERENCES repair_requests(id),
                FOREIGN KEY (uploaded_by) REFERENCES users(id)
            )""",
            """CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT DEFAULT 'info',
                is_read INTEGER DEFAULT 0,
                related_request_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (related_request_id) REFERENCES repair_requests(id)
            )""",
            """CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                old_values TEXT,
                new_values TEXT,
                performed_by INTEGER,
                performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                FOREIGN KEY (performed_by) REFERENCES users(id)
            )""",
            """CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                theme TEXT DEFAULT 'dark',
                language TEXT DEFAULT 'ru',
                notifications_enabled INTEGER DEFAULT 1,
                email_notifications INTEGER DEFAULT 1,
                auto_refresh INTEGER DEFAULT 1,
                refresh_interval INTEGER DEFAULT 30,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )""",
        ]

        for sql in tables_sql:
            try:
                self.cursor.execute(sql)
            except Exception as e:
                logger.error(f"Error creating table: {e}")

        self.connection.commit()
        logger.info("All tables created successfully")
        self._create_indexes()
    
    def _create_indexes(self):
        """Создание индексов для оптимизации запросов"""
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role_id)",
            "CREATE INDEX IF NOT EXISTS idx_vehicles_number ON vehicles(vehicle_number)",
            "CREATE INDEX IF NOT EXISTS idx_vehicles_status ON vehicles(status)",
            "CREATE INDEX IF NOT EXISTS idx_repair_requests_status ON repair_requests(status)",
            "CREATE INDEX IF NOT EXISTS idx_repair_requests_vehicle ON repair_requests(vehicle_id)",
            "CREATE INDEX IF NOT EXISTS idx_repair_requests_created_by ON repair_requests(created_by)",
            "CREATE INDEX IF NOT EXISTS idx_repair_requests_assigned_to ON repair_requests(assigned_to)",
            "CREATE INDEX IF NOT EXISTS idx_parts_number ON parts(part_number)",
            "CREATE INDEX IF NOT EXISTS idx_parts_category ON parts(category)",
            "CREATE INDEX IF NOT EXISTS idx_attachments_request ON attachments(request_id)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read)",
            "CREATE INDEX IF NOT EXISTS idx_audit_log_table ON audit_log(table_name, record_id)",
        ]
        
        for sql in indexes_sql:
            try:
                self.cursor.execute(sql)
            except Exception as e:
                logger.error(f"Error creating index: {e}")
        
        self.connection.commit()
        logger.info("All indexes created successfully")

    def _migrate_firebase(self):
        """Добавляет колонку firebase_uid в таблицу users (если ещё нет)"""
        try:
            self.cursor.execute("ALTER TABLE users ADD COLUMN firebase_uid TEXT")
            self.connection.commit()
            logger.info("Migrated: added firebase_uid column to users")
        except Exception:
            pass  # Колонка уже существует

    @staticmethod
    def _dev_hash(pwd: str) -> str:
        """Lightweight hash for dev-only accounts (no bcrypt dependency)."""
        import hashlib, hmac
        return 'DEV:' + hmac.new(b'carvix-dev', pwd.encode(), hashlib.sha256).hexdigest()

    @staticmethod
    def _dev_verify(pwd: str, stored: str) -> bool:
        import hashlib, hmac
        return stored == 'DEV:' + hmac.new(b'carvix-dev', pwd.encode(), hashlib.sha256).hexdigest()

    def _ensure_dev_users(self):
        """Гарантирует наличие dev-аккаунтов в любой (в т.ч. уже существующей) БД."""
        dev_users = [
            ('admin',       'Администратор Системы', 'admin@carvix.ru',    'Admin123!',   'Администратор'),
            ('director',    'Директор Компании',     'director@carvix.ru', 'Dir123!',     'Директор'),
            ('chief',       'Главный Механик',       'chief@carvix.ru',    'Chief123!',   'Главный механик'),
            ('mechanic',    'Механик Тестовый',      'mechanic@carvix.ru', 'Mech123!',    'Механик'),
            ('dispatcher',  'Диспетчер Тестовый',    'dispatch@carvix.ru', 'Disp123!',    'Диспетчер'),
            ('analyst',     'Аналитик Тестовый',     'analyst@carvix.ru',  'Analyst123!', 'Аналитик'),
            ('user',        'Пользователь Тестовый', 'user@carvix.ru',     'User123!',    'Пользователь'),
        ]
        try:
            for uname, full_name, email, pwd, role_name in dev_users:
                role_row = self.execute_one("SELECT id FROM roles WHERE name = ?", (role_name,))
                if not role_row:
                    continue
                fuid = f'DEV_LOCAL_{uname}'
                exists = self.execute_one(
                    "SELECT id FROM users WHERE firebase_uid = ?", (fuid,)
                )
                if not exists:
                    self.cursor.execute("""
                        INSERT OR IGNORE INTO users
                            (username, full_name, email, password_hash, firebase_uid, role_id, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, 1)
                    """, (uname, full_name, email, self._dev_hash(pwd), fuid, role_row['id']))
                else:
                    # Re-hash if stored hash is not in DEV: format (migration from bcrypt)
                    stored = self.execute_one("SELECT password_hash FROM users WHERE firebase_uid=?", (fuid,))
                    if stored and not stored['password_hash'].startswith('DEV:'):
                        self.cursor.execute(
                            "UPDATE users SET password_hash=? WHERE firebase_uid=?",
                            (self._dev_hash(pwd), fuid)
                        )
            self.connection.commit()
            logger.info("Dev users ensured")
        except Exception as e:
            logger.warning(f"_ensure_dev_users error: {e}")

    def _ensure_demo_data(self):
        """Назначает заявки, ТО и уведомления dev-пользователям для демонстрации ролей.
        Запускается при каждом старте — идемпотентен (не дублирует уже назначенные записи).
        """
        import random, datetime as _dt
        random.seed(42)

        try:
            # Получаем dev-пользователей
            users = {
                r['username']: dict(r)
                for r in self.execute(
                    "SELECT id, username, role_id FROM users WHERE firebase_uid LIKE 'DEV_LOCAL_%'"
                )
            }
            if not users:
                return

            uid_admin    = users.get('admin',      {}).get('id')
            uid_director = users.get('director',   {}).get('id')
            uid_chief    = users.get('chief',       {}).get('id')
            uid_mech     = users.get('mechanic',    {}).get('id')
            uid_disp     = users.get('dispatcher',  {}).get('id')
            uid_analyst  = users.get('analyst',     {}).get('id')
            uid_user     = users.get('user',        {}).get('id')

            vehicles  = [r['id'] for r in self.execute("SELECT id FROM vehicles")]
            rt_rows   = [r['id'] for r in self.execute("SELECT id FROM repair_types")]
            dc_rows   = [r['id'] for r in self.execute("SELECT id FROM defect_categories")]
            mt_rows   = [r['id'] for r in self.execute("SELECT id FROM maintenance_types")]

            if not vehicles or not rt_rows:
                return

            # ── 1. Назначаем заявки: NULL или с несуществующим created_by ──
            null_reqs = self.execute("""
                SELECT id FROM repair_requests
                WHERE created_by IS NULL
                   OR created_by NOT IN (SELECT id FROM users)
                ORDER BY id
            """)
            assignments = [
                # (created_by, assigned_to, status)
                (uid_user,   None,       'Новая'),
                (uid_user,   None,       'Новая'),
                (uid_disp,   uid_mech,   'Принята'),
                (uid_disp,   uid_mech,   'В работе'),
                (uid_disp,   uid_mech,   'В работе'),
                (uid_user,   uid_mech,   'В работе'),
                (uid_disp,   uid_chief,  'Ожидает запчастей'),
                (uid_user,   uid_chief,  'Ожидает запчастей'),
                (uid_disp,   uid_mech,   'Выполнена'),
                (uid_user,   uid_mech,   'Выполнена'),
                (uid_admin,  uid_mech,   'Закрыта'),
                (uid_admin,  uid_mech,   'Закрыта'),
                (uid_disp,   uid_mech,   'Закрыта'),
                (uid_user,   None,       'Новая'),
                (uid_user,   uid_chief,  'Принята'),
                (uid_disp,   uid_mech,   'В работе'),
                (uid_admin,  uid_chief,  'Выполнена'),
                (uid_disp,   uid_mech,   'Закрыта'),
                (uid_user,   None,       'Новая'),
                (uid_disp,   uid_mech,   'В работе'),
                (uid_user,   uid_mech,   'В работе'),
                (uid_disp,   uid_chief,  'Ожидает запчастей'),
                (uid_admin,  uid_mech,   'Закрыта'),
                (uid_disp,   uid_mech,   'Принята'),
                (uid_user,   None,       'Новая'),
                (uid_disp,   uid_mech,   'В работе'),
                (uid_admin,  uid_mech,   'Закрыта'),
                (uid_user,   uid_mech,   'Выполнена'),
                (uid_disp,   uid_chief,  'В работе'),
                (uid_admin,  uid_mech,   'Закрыта'),
            ]
            for i, req_row in enumerate(null_reqs):
                if i >= len(assignments):
                    cb, at, st = uid_admin, uid_mech, 'Закрыта'
                else:
                    cb, at, st = assignments[i]
                now = _dt.datetime.now()
                completed_at = (now - _dt.timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S') \
                    if st in ('Выполнена', 'Закрыта') else None
                closed_at = completed_at if st == 'Закрыта' else None
                accepted_at = (now - _dt.timedelta(days=random.randint(3, 60))).strftime('%Y-%m-%d %H:%M:%S') \
                    if st != 'Новая' else None
                self.cursor.execute("""
                    UPDATE repair_requests
                    SET created_by=?, assigned_to=?, status=?,
                        accepted_at=?, completed_at=?, closed_at=?
                    WHERE id=?
                """, (cb, at, st, accepted_at, completed_at, closed_at, req_row['id']))

            # ── 2. Очищаем устаревшие work-записи с несуществующими авторами
            self.cursor.execute("""
                DELETE FROM request_works
                WHERE performed_by IS NOT NULL
                  AND performed_by NOT IN (SELECT id FROM users)
            """)

            # ── 2b. Добавляем записи о выполненных работах ────────────────
            done_reqs = self.execute(
                "SELECT id FROM repair_requests WHERE status IN ('Выполнена','Закрыта') AND assigned_to IS NOT NULL LIMIT 15"
            )
            work_descs = [
                "Замена масла и масляного фильтра", "Диагностика электронной системы",
                "Замена тормозных колодок (передние)", "Ремонт подвески (передняя балка)",
                "Регулировка развал-схождения", "Замена ремня ГРМ и помпы",
                "Чистка форсунок топливной системы", "Замена аккумулятора",
                "Регулировка клапанов двигателя", "Полная компьютерная диагностика",
            ]
            parts_rows = self.execute("SELECT id, price FROM parts LIMIT 10")
            for rr in done_reqs:
                already = self.execute_one(
                    "SELECT id FROM request_works WHERE request_id=?", (rr['id'],)
                )
                if already:
                    continue
                hours = random.uniform(1.5, 12.0)
                cost  = random.randint(2000, 45000)
                self.cursor.execute("""
                    INSERT OR IGNORE INTO request_works
                        (request_id, description, hours_spent, cost, performed_by, performed_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now', ?))
                """, (rr['id'], random.choice(work_descs), round(hours, 1), cost,
                      uid_mech, f'-{random.randint(1,20)} days'))
                if parts_rows:
                    p = random.choice(parts_rows)
                    self.cursor.execute("""
                        INSERT OR IGNORE INTO request_parts
                            (request_id, part_id, quantity, unit_price, total_price)
                        VALUES (?, ?, ?, ?, ?)
                    """, (rr['id'], p['id'], random.randint(1, 3),
                          p['price'], p['price'] * random.randint(1, 3)))

            # ── 3. Записи ТО с назначениями ───────────────────────────────
            # Удаляем ТО с несуществующими пользователями, чтобы пересоздать
            self.cursor.execute("""
                DELETE FROM maintenance_requests
                WHERE created_by NOT IN (SELECT id FROM users)
                   OR (assigned_to IS NOT NULL AND assigned_to NOT IN (SELECT id FROM users))
            """)
            maint_exists = self.execute_one("SELECT COUNT(*) FROM maintenance_requests")[0]
            if maint_exists == 0 and mt_rows:
                statuses_m = ['Запланировано', 'В процессе', 'Выполнено', 'Запланировано', 'Выполнено']
                for i, v_id in enumerate(vehicles[:5]):
                    mt = mt_rows[i % len(mt_rows)]
                    sched = (_dt.date.today() + _dt.timedelta(days=random.randint(-30, 60))).strftime('%Y-%m-%d')
                    done_dt = (_dt.datetime.now() - _dt.timedelta(days=random.randint(1, 15))).strftime('%Y-%m-%d %H:%M:%S') \
                        if statuses_m[i] == 'Выполнено' else None
                    cost_v = random.randint(5000, 25000) if done_dt else None
                    req_num = f'TO-{_dt.datetime.now().strftime("%Y%m")}-{i+1:04d}'
                    self.cursor.execute("""
                        INSERT OR IGNORE INTO maintenance_requests
                            (request_number, vehicle_id, maintenance_type_id, status,
                             scheduled_date, completed_at, actual_cost,
                             notes, created_by, assigned_to)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (req_num, v_id, mt, statuses_m[i], sched, done_dt, cost_v,
                          'Плановое техническое обслуживание автомобиля', uid_disp, uid_mech))

            # ── 4. Уведомления для разных ролей ───────────────────────────
            notif_exists = self.execute_one("SELECT COUNT(*) FROM notifications")[0]
            if notif_exists == 0:
                notifs = [
                    (uid_admin,    'Новая заявка на ремонт',    'Создана заявка №1: Не заводится двигатель',  'info',    0),
                    (uid_admin,    'Пользователь зарегистрирован', 'Новый пользователь: mechanic@carvix.ru', 'success', 0),
                    (uid_chief,    'Назначена заявка',           'Заявка №3 назначена вам на выполнение',      'info',    0),
                    (uid_chief,    'Срочная заявка!',            'Критическая неисправность — заявка №7',      'warning', 0),
                    (uid_mech,     'Новое задание',              'Вам назначена заявка №3 на диагностику',     'info',    0),
                    (uid_mech,     'Запчасти получены',          'Заявка №7 — запчасти поступили на склад',    'success', 0),
                    (uid_mech,     'Срок истекает',              'Заявка №5 должна быть выполнена сегодня',    'warning', 0),
                    (uid_disp,     'Заявка принята',             'Заявка №3 принята главным механиком',        'success', 0),
                    (uid_disp,     'Запрос на запчасти',         'Запчасти для заявки №7 ожидают одобрения',   'warning', 0),
                    (uid_user,     'Статус заявки',              'Ваша заявка №1 принята в работу',            'info',    0),
                    (uid_user,     'Заявка выполнена',           'Ваша заявка №6 успешно выполнена',           'success', 1),
                    (uid_analyst,  'Отчёт готов',                'Ежемесячный отчёт по затратам доступен',     'info',    0),
                    (uid_director, 'KPI отчёт',                  'Эффективность ремонтной службы: 87%',        'success', 1),
                    (uid_director, 'Превышение бюджета',         'Затраты на ремонт превысили план на 12%',    'warning', 0),
                ]
                for u_id, title, msg, ntype, is_read in notifs:
                    if u_id:
                        self.cursor.execute("""
                            INSERT INTO notifications (user_id, title, message, type, is_read)
                            VALUES (?, ?, ?, ?, ?)
                        """, (u_id, title, msg, ntype, is_read))

            self.connection.commit()
            logger.info("Demo data ensured (role-based assignments, works, maintenance, notifications)")
        except Exception as e:
            logger.warning(f"_ensure_demo_data error: {e}")

    def _clear_local_auth_users(self):
        """Удаляет пользователей без firebase_uid (кроме dev-аккаунтов DEV_LOCAL_)."""
        try:
            self.cursor.execute("PRAGMA foreign_keys = OFF")
            self.cursor.execute(
                "DELETE FROM users WHERE (firebase_uid IS NULL OR firebase_uid = '')"
                " AND firebase_uid NOT LIKE 'DEV_LOCAL_%'"
            )
            removed = self.cursor.rowcount
            self.connection.commit()
            self.cursor.execute("PRAGMA foreign_keys = ON")
            if removed > 0:
                logger.info(f"Removed {removed} local-auth users (no firebase_uid)")
        except Exception as e:
            logger.warning(f"_clear_local_auth_users error: {e}")

    def seed_initial_data(self):
        self.cursor.execute("SELECT COUNT(*) FROM roles")
        if self.cursor.fetchone()[0] > 0:
            return

        # Отключаем FK на время сидинга (много cross-refs, включаем в конце)
        self.cursor.execute("PRAGMA foreign_keys = OFF")

        # Роли
        roles = [
            ('Администратор', 'Полный доступ к системе', 'all'),
            ('Директор', 'Аналитика и управленческие решения', 'analytics,reports,approvals'),
            ('Главный механик', 'Управление ремонтным процессом', 'requests,assignments,control'),
            ('Механик', 'Выполнение ремонтных работ', 'my_requests,works'),
            ('Диспетчер', 'Регистрация и сопровождение заявок', 'requests,vehicles,notifications'),
            ('Аналитик', 'Анализ данных и отчеты', 'analytics,reports,export'),
            ('Пользователь', 'Создание заявок на ремонт', 'create_requests,my_requests'),
        ]
        for name, desc, perms in roles:
            self.cursor.execute("INSERT INTO roles (name, description, permissions) VALUES (?, ?, ?)",
                              (name, desc, perms))


        # Виды ремонта
        repair_types = [
            ('Текущий ремонт', 'Регулярное ТО', 2, 5000),
            ('Капитальный ремонт', 'Полная переборка', 40, 50000),
            ('Срочный ремонт', 'Неотложный ремонт', 4, 10000),
            ('Диагностика', 'Компьютерная диагностика', 1, 2000),
            ('Замена масла', 'Замена масла и фильтров', 1, 3000),
            ('Ремонт двигателя', 'Ремонт двигателя', 20, 30000),
            ('Ремонт трансмиссии', 'Ремонт КПП/АКПП', 15, 25000),
            ('Ремонт ходовой', 'Ремонт подвески', 8, 15000),
            ('Ремонт электрики', 'Ремонт электрооборудования', 5, 8000),
            ('Кузовной ремонт', 'Ремонт кузова', 30, 40000),
        ]
        for name, desc, hours, cost in repair_types:
            self.cursor.execute("INSERT INTO repair_types (name, description, estimated_hours, estimated_cost) VALUES (?, ?, ?, ?)",
                              (name, desc, hours, cost))

        # Виды ТО
        maintenance_types = [
            ('ТО-1', 'Первое ТО', 5000, 3, 8000),
            ('ТО-2', 'Второе ТО', 10000, 6, 15000),
            ('ТО-3', 'Третье ТО', 20000, 12, 25000),
            ('Сезонное ТО', 'Подготовка к сезону', 0, 6, 12000),
            ('Диагностическое ТО', 'Плановая диагностика', 15000, 12, 5000),
        ]
        for name, desc, km, months, cost in maintenance_types:
            self.cursor.execute("INSERT INTO maintenance_types (name, description, interval_km, interval_months, estimated_cost) VALUES (?, ?, ?, ?, ?)",
                              (name, desc, km, months, cost))

        # Категории неисправностей
        defect_categories = [
            ('Двигатель', 'Проблемы с двигателем', 'Высокий'),
            ('Трансмиссия', 'Проблемы с КПП/АКПП', 'Высокий'),
            ('Ходовая часть', 'Проблемы с подвеской', 'Средний'),
            ('Тормозная система', 'Проблемы с тормозами', 'Критический'),
            ('Электрооборудование', 'Проблемы с электрикой', 'Средний'),
            ('Кузов', 'Повреждения кузова', 'Низкий'),
            ('Салон', 'Проблемы в салоне', 'Низкий'),
            ('Система охлаждения', 'Проблемы с охлаждением', 'Высокий'),
            ('Топливная система', 'Проблемы с топливом', 'Высокий'),
            ('Диагностика', 'Требуется диагностика', 'Средний'),
        ]
        for name, desc, priority in defect_categories:
            self.cursor.execute("INSERT INTO defect_categories (name, description, priority) VALUES (?, ?, ?)",
                              (name, desc, priority))

        # Тестовые автомобили
        vehicles = [
            ('А001АА77', 'Toyota', 'Camry', 2020, 'JTDBU4EE3B9123456', 'Легковой', 'Офис', 45000, 'Бензин'),
            ('В002ВВ77', 'Ford', 'Transit', 2019, 'WF0XXXERKF1234567', 'Грузовой', 'Логистика', 78000, 'Дизель'),
            ('С003СС77', 'Lada', 'Vesta', 2021, 'XTA21104012345678', 'Легковой', 'Офис', 23000, 'Бензин'),
            ('Е004ЕЕ77', 'Mercedes', 'Sprinter', 2018, 'WDB9066331S123456', 'Грузовой', 'Логистика', 95000, 'Дизель'),
            ('К005КК77', 'Kia', 'Rio', 2022, 'Z94CT41DBMR123456', 'Легковой', 'Офис', 12000, 'Бензин'),
            ('М006ММ77', 'GAZelle', 'Next', 2020, 'X9L21104012345678', 'Грузовой', 'Логистика', 56000, 'Дизель'),
            ('Н007НН77', 'Hyundai', 'Solaris', 2021, 'Z94CT41DBMR654321', 'Легковой', 'Офис', 34000, 'Бензин'),
            ('О008ОО77', 'Volkswagen', 'Crafter', 2019, 'WV1ZZZ2EZK1123456', 'Грузовой', 'Логистика', 67000, 'Дизель'),
        ]
        for number, brand, model, year, vin, category, dept, mileage, fuel in vehicles:
            self.cursor.execute("""INSERT INTO vehicles (vehicle_number, brand, model, year, vin, category, department, mileage, fuel_type, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'В работе')""",
                (number, brand, model, year, vin, category, dept, mileage, fuel))

        # Поставщики
        suppliers = [
            ('Автозапчасти Плюс', 'Иванов И.И.', '+7(495)123-45-67', 'info@autoplus.ru', 'Москва, ул. Автозаводская, 1', '7701234567'),
            ('ТехноМоторс', 'Петров П.П.', '+7(495)234-56-78', 'sales@technomotors.ru', 'Москва, ш. Энтузиастов, 15', '7702345678'),
            ('Запчасти Опт', 'Сидоров С.С.', '+7(495)345-67-89', 'opt@zapchasti.ru', 'Москва, ул. Профсоюзная, 25', '7703456789'),
            ('МоторСервис', 'Козлов К.К.', '+7(495)456-78-90', 'service@motorserv.ru', 'Москва, пр-т Вернадского, 42', '7704567890'),
        ]
        for name, contact, phone, email, address, inn in suppliers:
            self.cursor.execute("""INSERT INTO suppliers (name, contact_person, phone, email, address, inn)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (name, contact, phone, email, address, inn))

        self.connection.commit()  # Commit vehicles/suppliers/parts before repair requests (FK constraints)

        # Запчасти
        parts = [
            ('OIL-5W30-4L', 'Масло моторное 5W-30 4л', 'Масла и жидкости', 1, 2500, 50, 10, 'Полка A1'),
            ('OIL-5W40-4L', 'Масло моторное 5W-40 4л', 'Масла и жидкости', 1, 2800, 45, 10, 'Полка A1'),
            ('FILTER-OIL-01', 'Фильтр масляный', 'Фильтры', 1, 450, 100, 20, 'Полка B1'),
            ('FILTER-AIR-01', 'Фильтр воздушный', 'Фильтры', 1, 650, 80, 15, 'Полка B2'),
            ('FILTER-FUEL-01', 'Фильтр топливный', 'Фильтры', 2, 850, 60, 12, 'Полка B3'),
            ('BRAKE-PAD-FRONT', 'Колодки тормозные передние', 'Тормозная система', 2, 3200, 40, 8, 'Полка C1'),
            ('BRAKE-PAD-REAR', 'Колодки тормозные задние', 'Тормозная система', 2, 2800, 35, 7, 'Полка C2'),
            ('BRAKE-DISC-FRONT', 'Диск тормозной передний', 'Тормозная система', 3, 4500, 25, 5, 'Полка C3'),
            ('BELT-GENERATOR', 'Ремень генератора', 'Ремни и ролики', 3, 1200, 30, 6, 'Полка D1'),
            ('BELT-TIMING', 'Ремень ГРМ', 'Ремни и ролики', 3, 3500, 20, 4, 'Полка D2'),
            ('BATTERY-60AH', 'Аккумулятор 60 Ah', 'Электрика', 4, 6500, 15, 3, 'Полка E1'),
            ('BATTERY-75AH', 'Аккумулятор 75 Ah', 'Электрика', 4, 7800, 12, 3, 'Полка E1'),
            ('SPARK-PLUG-01', 'Свеча зажигания', 'Электрика', 2, 350, 200, 40, 'Полка E2'),
            ('BULB-H7-55W', 'Лампа H7 55W', 'Электрика', 2, 450, 150, 30, 'Полка E3'),
            ('SHOCK-ABSORBER-FRONT', 'Амортизатор передний', 'Подвеска', 3, 4800, 20, 4, 'Полка F1'),
            ('SHOCK-ABSORBER-REAR', 'Амортизатор задний', 'Подвеска', 3, 4200, 18, 4, 'Полка F2'),
            ('TIE-ROD-END', 'Наконечник рулевой', 'Рулевое управление', 3, 1800, 25, 5, 'Полка F3'),
            ('BALL-JOINT', 'Шаровая опора', 'Подвеска', 3, 2200, 22, 5, 'Полка F4'),
            ('ANTIFREEZE-5L', 'Антифриз 5л', 'Масла и жидкости', 1, 1200, 40, 8, 'Полка A2'),
            ('WIPER-BLADE-24', 'Щетка стеклоочистителя 24"', 'Аксессуары', 4, 850, 60, 12, 'Полка G1'),
        ]
        for part_num, name, category, supplier_id, price, qty, min_qty, location in parts:
            self.cursor.execute("""INSERT INTO parts (part_number, name, description, category, supplier_id, price, quantity, min_quantity, location)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (part_num, name, name, category, supplier_id, price, qty, min_qty, location))

        self.connection.commit()  # Commit parts before creating repair requests

        # Тестовые пользователи добавляются через _ensure_dev_users() при каждом старте

        # Ещё один commit для гарантии что все справочники доступны для FK
        self.connection.commit()

        # Тестовые заявки на ремонт (created_by=0 — будет назначен dev-пользователем позже)
        defect_cats = self.execute("SELECT id, name FROM defect_categories")
        repair_types_data = self.execute("SELECT id, name FROM repair_types")
        vehicles_data = self.execute("SELECT id FROM vehicles")

        statuses = [Config.STATUS_NEW, Config.STATUS_ACCEPTED, Config.STATUS_IN_PROGRESS,
                   Config.STATUS_WAITING_PARTS, Config.STATUS_COMPLETED, Config.STATUS_CLOSED]
        priorities = [Config.PRIORITY_LOW, Config.PRIORITY_MEDIUM, Config.PRIORITY_HIGH, Config.PRIORITY_CRITICAL]
        descriptions = [
            "Не заводится двигатель", "Посторонний шум при торможении",
            "Течь масла из двигателя", "Не работает кондиционер",
            "Вибрация при движении", "Проблема с коробкой передач",
            "Горит Check Engine", "Износ тормозных колодок",
            "Требуется замена масла", "Проблема с рулевым управлением",
            "Не работает стартер", "Перегрев двигателя",
            "Требуется диагностика подвески", "Скрип при повороте руля",
        ]

        for i in range(30):
            vehicle_id = random.choice(vehicles_data)['id']
            defect_cat_id = random.choice(defect_cats)['id']
            repair_type_id = random.choice(repair_types_data)['id']
            status = random.choice(statuses)
            priority = random.choice(priorities)
            description = random.choice(descriptions)
            created_date = datetime.now() - timedelta(days=random.randint(1, 60))
            request_number = f"RM-{created_date.strftime('%Y%m')}-{str(i+1).zfill(3)}"
            estimated_cost = random.randint(5000, 50000)
            actual_cost = (estimated_cost + random.randint(-5000, 10000)
                          if status in [Config.STATUS_COMPLETED, Config.STATUS_CLOSED] else None)
            accepted_at = (created_date + timedelta(hours=random.randint(1, 24))
                          if status != Config.STATUS_NEW else None)
            started_at = (accepted_at + timedelta(hours=random.randint(1, 12))
                         if status in [Config.STATUS_IN_PROGRESS, Config.STATUS_WAITING_PARTS,
                                       Config.STATUS_COMPLETED, Config.STATUS_CLOSED] else None)
            completed_at = (started_at + timedelta(days=random.randint(1, 7))
                           if status in [Config.STATUS_COMPLETED, Config.STATUS_CLOSED] else None)
            self.cursor.execute("""
                INSERT INTO repair_requests (
                    request_number, vehicle_id, created_by, assigned_to,
                    defect_category_id, repair_type_id, description, priority, status,
                    estimated_cost, actual_cost, created_at, accepted_at, started_at, completed_at
                ) VALUES (?, ?, 0, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request_number, vehicle_id,
                defect_cat_id, repair_type_id, description, priority, status,
                estimated_cost, actual_cost, created_date, accepted_at, started_at, completed_at
            ))

        self.connection.commit()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        logger.info("Initial data seeded successfully with 30 repair requests")

    def execute(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Query error: {e}")
            raise

    def execute_one(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Exception as e:
            logger.error(f"Query error: {e}")
            raise

    def execute_insert(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logger.error(f"Insert error: {e}")
            self.connection.rollback()
            raise

    def execute_update(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            logger.error(f"Update error: {e}")
            self.connection.rollback()
            raise

    def close(self):
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

# =============================================================================
# АНИМАЦИИ
# =============================================================================

class AnimationHelper:
    @staticmethod
    def fade_in(widget, duration=300):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        return animation

    @staticmethod
    def fade_out(widget, duration=300):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        return animation

    @staticmethod
    def slide_in(widget, direction='left', duration=400):
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        start_pos = widget.pos()
        if direction == 'left':
            animation.setStartValue(QPoint(-widget.width(), start_pos.y()))
        elif direction == 'right':
            animation.setStartValue(QPoint(widget.parent().width(), start_pos.y()))
        elif direction == 'top':
            animation.setStartValue(QPoint(start_pos.x(), -widget.height()))
        elif direction == 'bottom':
            animation.setStartValue(QPoint(start_pos.x(), widget.parent().height()))
        animation.setEndValue(start_pos)
        return animation

    @staticmethod
    def scale_in(widget, duration=300):
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.Type.OutBack)
        geo = widget.geometry()
        center = geo.center()
        start_geo = QRect(center.x(), center.y(), 0, 0)
        animation.setStartValue(start_geo)
        animation.setEndValue(geo)
        return animation

    @staticmethod
    def fade_page_in(widget, duration=220):
        """Safe no-op stub — opacity effects break QStackedWidget rendering."""
        return None

    @staticmethod
    def pulse(widget, color_hex='#6366F1', duration=600):
        """Pulsing glow on a widget (via shadow)."""
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(0)
        shadow.setColor(QColor(color_hex))
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)
        anim = QPropertyAnimation(shadow, b"blurRadius")
        anim.setDuration(duration)
        anim.setStartValue(0)
        anim.setKeyValueAt(0.5, 24)
        anim.setEndValue(0)
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        return anim


class CountUpAnimation(QObject):
    """Анимирует числовое значение — плавно считает от 0 до target."""
    value_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(16)   # ~60 fps
        self._timer.timeout.connect(self._tick)
        self._start = 0
        self._target = 0
        self._current = 0.0
        self._duration = 600
        self._elapsed = 0

    def animate(self, target: int, duration: int = 600):
        self._target = target
        self._start = 0
        self._current = 0.0
        self._duration = max(duration, 1)
        self._elapsed = 0
        self._timer.start()

    def _tick(self):
        self._elapsed += 16
        t = min(self._elapsed / self._duration, 1.0)
        # ease-out cubic
        ease = 1 - (1 - t) ** 3
        self._current = self._start + (self._target - self._start) * ease
        self.value_changed.emit(int(self._current))
        if t >= 1.0:
            self._timer.stop()
            self.value_changed.emit(self._target)

# =============================================================================
# СТИЛИ
# =============================================================================

class Styles:
    @staticmethod
    def get_main_stylesheet():
        c = Config.COLORS
        accent = c.get('accent', '#6366F1')
        accent_l = c.get('accent_light', '#818CF8')
        accent_d = c.get('accent_dark', '#4F46E5')
        glow = c.get('accent_glow', '#6366F125')
        bg0 = c['bg_primary']
        bg1 = c['bg_secondary']
        bg2 = c['bg_card']
        bg3 = c.get('bg_elevated', '#1A1A2A')
        bgh = c['bg_hover']
        bgi = c.get('bg_input', c['bg_secondary'])
        tp  = c['text_primary']
        ts  = c['text_secondary']
        tm  = c['text_muted']
        td  = c.get('text_disabled', c['text_muted'])
        br  = c['border']
        dv  = c.get('divider', c['border'])
        ok  = c['success']
        err = c['error']
        wrn = c['warning']
        inf = c.get('info', '#38BDF8')
        return f"""
QMainWindow {{ background-color: {bg0}; }}
QWidget {{ background-color: {bg0}; color: {tp};
  font-family: 'Segoe UI Variable Text', 'Segoe UI', 'Inter', Arial, sans-serif; font-size: 14px; }}
QFrame {{ background-color: {bg2}; border-radius: 12px; border: 1px solid {br}; }}
QFrame#card {{ background-color: {bg2}; border-radius: 16px; border: 1px solid {br}; padding: 20px; }}
QLabel {{ color: {tp}; background: transparent; border: none; }}
QLabel#title {{ font-size: 26px; font-weight: 700; color: {tp}; letter-spacing: -0.5px; }}
QLabel#subtitle {{ font-size: 13px; color: {ts}; font-weight: 400; }}
QLabel#accent {{ color: {accent_l}; font-weight: 600; }}
QLabel#sectionHeader {{ font-size: 11px; font-weight: 700; color: {tm};
  letter-spacing: 1.2px; text-transform: uppercase; }}
QLabel#pageTitle {{ font-size: 20px; font-weight: 700; color: {tp}; }}

QPushButton {{
  background-color: {accent}; color: #FFFFFF; border: none;
  border-radius: 10px; padding: 9px 22px; min-height: 36px;
  font-weight: 600; font-size: 13px; letter-spacing: 0.2px;
}}
QPushButton:hover {{ background-color: {accent_l}; }}
QPushButton:pressed {{ background-color: {accent_d}; padding-top: 10px; padding-bottom: 8px; }}
QPushButton:focus {{ outline: none; }}
QPushButton:disabled {{ background-color: {bgh}; color: {td}; border: none; }}
QPushButton#secondary {{
  background-color: transparent; color: {tp}; border: 1px solid {br};
  border-radius: 10px;
}}
QPushButton#secondary:hover {{
  background-color: {bgh}; border-color: {accent}40; color: {accent_l};
}}
QPushButton#secondary:pressed {{ background-color: {bg3}; }}
QPushButton#danger {{
  background-color: {c.get('error_bg','#EF444415')}; color: {err};
  border: 1px solid {err}35; border-radius: 10px;
}}
QPushButton#danger:hover {{ background-color: {err}; color: #fff; }}
QPushButton#success {{
  background-color: {c.get('success_bg','#10B98115')}; color: {ok};
  border: 1px solid {ok}35; border-radius: 10px;
}}
QPushButton#success:hover {{ background-color: {ok}; color: #fff; }}
QPushButton#warning {{
  background-color: {c.get('warning_bg','#F59E0B15')}; color: {wrn};
  border: 1px solid {wrn}35; border-radius: 10px;
}}
QPushButton#warning:hover {{ background-color: {wrn}; color: #fff; }}
QPushButton#icon {{
  background-color: transparent; color: {ts}; border: none;
  padding: 6px; min-height: 30px; min-width: 30px; border-radius: 8px;
}}
QPushButton#icon:hover {{ background-color: {bgh}; color: {tp}; }}

QLineEdit {{
  background-color: {bgi}; color: {tp}; border: 1.5px solid {br};
  border-radius: 10px; padding: 9px 14px; font-size: 14px; min-height: 36px;
  selection-background-color: {accent}40;
}}
QLineEdit:focus {{ border-color: {accent}; background-color: {bg2}; }}
QLineEdit:hover:!focus {{ border-color: {accent}30; }}
QLineEdit::placeholder {{ color: {tm}; }}

QComboBox {{
  background-color: {bgi}; color: {tp}; border: 1.5px solid {br};
  border-radius: 10px; padding: 9px 14px; min-width: 160px; min-height: 36px; font-size: 14px;
}}
QComboBox:hover {{ border-color: {accent}30; }}
QComboBox:focus {{ border-color: {accent}; }}
QComboBox::drop-down {{ border: none; width: 32px; }}
QComboBox QAbstractItemView {{
  background-color: {bg3}; color: {tp}; border: 1px solid {br};
  border-radius: 10px; selection-background-color: {accent};
  selection-color: #fff; padding: 4px; outline: none;
}}
QComboBox QAbstractItemView::item {{
  padding: 8px 14px; border-radius: 6px; min-height: 32px;
}}
QComboBox QAbstractItemView::item:hover {{
  background-color: {bgh};
}}

QTextEdit {{
  background-color: {bgi}; color: {tp}; border: 1.5px solid {br};
  border-radius: 10px; padding: 12px; font-size: 14px; line-height: 1.5;
}}
QTextEdit:focus {{ border-color: {accent}; }}

QTableWidget {{
  background-color: {bg2}; color: {tp}; border: 1px solid {br};
  border-radius: 12px; gridline-color: transparent;
  selection-background-color: {accent}18; selection-color: {tp};
  alternate-background-color: {bg1}; font-size: 13px; outline: none;
}}
QTableWidget::item {{
  padding: 12px 16px; border-bottom: 1px solid {dv}; min-height: 46px;
}}
QTableWidget::item:selected {{
  background-color: {accent}18; color: {tp};
  border-left: 2px solid {accent};
}}
QTableWidget::item:hover {{ background-color: {bgh}; }}
QHeaderView::section {{
  background-color: {bg1}; color: {tm}; padding: 12px 16px;
  border: none; border-bottom: 1.5px solid {br};
  font-weight: 700; font-size: 11px; letter-spacing: 0.8px;
  text-transform: uppercase;
}}
QHeaderView::section:first {{ border-radius: 12px 0 0 0; }}
QHeaderView::section:last {{ border-radius: 0 12px 0 0; }}

QScrollBar:vertical {{
  background-color: transparent; width: 7px; margin: 4px 2px;
}}
QScrollBar::handle:vertical {{
  background-color: {br}; border-radius: 3px; min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{ background-color: {accent}60; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{
  background-color: transparent; height: 7px; margin: 2px 4px;
}}
QScrollBar::handle:horizontal {{
  background-color: {br}; border-radius: 3px; min-width: 28px;
}}
QScrollBar::handle:horizontal:hover {{ background-color: {accent}60; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}

QDateEdit, QTimeEdit {{
  background-color: {bgi}; color: {tp}; border: 1.5px solid {br};
  border-radius: 10px; padding: 9px 14px; font-size: 14px; min-height: 36px;
}}
QDateEdit:focus, QTimeEdit:focus {{ border-color: {accent}; }}
QSpinBox, QDoubleSpinBox {{
  background-color: {bgi}; color: {tp}; border: 1.5px solid {br};
  border-radius: 10px; padding: 9px 14px; font-size: 14px; min-height: 36px;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{ border-color: {accent}; }}

QCheckBox {{ color: {tp}; spacing: 10px; font-size: 14px; }}
QCheckBox::indicator {{
  width: 18px; height: 18px; border-radius: 5px;
  border: 1.5px solid {br}; background-color: {bgi};
}}
QCheckBox::indicator:checked {{
  background-color: {accent}; border-color: {accent};
  image: none;
}}
QCheckBox::indicator:hover {{ border-color: {accent}; }}

QGroupBox {{
  background-color: {bg2}; color: {tp}; border: 1px solid {br};
  border-radius: 12px; margin-top: 14px; padding-top: 14px;
  font-weight: 600; font-size: 13px;
}}
QGroupBox::title {{
  subcontrol-origin: margin; left: 14px; padding: 0 8px; color: {ts};
}}

QTabWidget::pane {{
  background-color: {bg2}; border: 1px solid {br}; border-radius: 12px; top: -1px;
}}
QTabBar::tab {{
  background-color: transparent; color: {tm}; padding: 10px 22px;
  border: none; border-bottom: 2px solid transparent;
  margin-right: 4px; font-weight: 500; font-size: 13px;
}}
QTabBar::tab:selected {{
  color: {tp}; border-bottom: 2px solid {accent}; font-weight: 600;
}}
QTabBar::tab:hover:!selected {{
  color: {ts}; background-color: {bgh}; border-radius: 6px 6px 0 0;
}}

QMenu {{
  background-color: {bg3}; color: {tp}; border: 1px solid {br};
  border-radius: 12px; padding: 6px;
}}
QMenu::item {{ padding: 8px 20px; border-radius: 6px; font-size: 13px; }}
QMenu::item:selected {{ background-color: {accent}; color: #fff; }}
QMenu::separator {{ height: 1px; background-color: {dv}; margin: 4px 0; }}

QProgressBar {{
  background-color: {bg3}; border: none; border-radius: 4px;
  height: 6px; font-size: 0px;
}}
QProgressBar::chunk {{ background-color: {accent}; border-radius: 4px; }}

QStatusBar {{
  background-color: {bg1}; color: {tm}; border-top: 1px solid {br}; font-size: 12px;
}}
QDialog {{ background-color: {bg0}; }}
QMessageBox {{ background-color: {bg0}; color: {tp}; }}
QMessageBox QLabel {{ color: {tp}; }}
QMessageBox QPushButton {{ min-width: 90px; }}
QToolTip {{
  background-color: {bg3}; color: {tp}; border: 1px solid {br};
  border-radius: 8px; padding: 6px 12px; font-size: 12px;
}}
QInputDialog {{ background-color: {bg0}; }}
QInputDialog QLabel {{ color: {tp}; }}
        """

# =============================================================================
# КАСТОМНЫЕ ВИДЖЕТЫ
# =============================================================================

class Card(QFrame):
    def __init__(self, parent=None, clickable=False):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.clickable = clickable
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(8)
        self._shadow.setColor(QColor(0, 0, 0, 80))
        self._shadow.setOffset(0, 2)
        self.setGraphicsEffect(self._shadow)
        if clickable:
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._blur_anim = QPropertyAnimation(self._shadow, b"blurRadius")
        self._blur_anim.setDuration(180)
        self._blur_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def enterEvent(self, event):
        if self.clickable:
            self._shadow.setColor(QColor(99, 102, 241, 55))
            self._shadow.setOffset(0, 6)
            self._blur_anim.stop()
            self._blur_anim.setStartValue(int(self._shadow.blurRadius()))
            self._blur_anim.setEndValue(24)
            self._blur_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.clickable:
            self._shadow.setColor(QColor(0, 0, 0, 80))
            self._shadow.setOffset(0, 2)
            self._blur_anim.stop()
            self._blur_anim.setStartValue(int(self._shadow.blurRadius()))
            self._blur_anim.setEndValue(8)
            self._blur_anim.start()
        super().leaveEvent(event)

class MetricCard(Card):
    def __init__(self, title, value, subtitle="", icon="", color=None, parent=None):
        super().__init__(parent, clickable=True)
        self.color = color or Config.COLORS.get('accent', '#6366F1')
        self._raw_value = value
        self._count_anim = CountUpAnimation(self)
        self._setup_ui(title, value, subtitle, icon)
        self._count_anim.value_changed.connect(self._on_count)

    def _setup_ui(self, title, value, subtitle, icon):
        c = Config.COLORS
        color = self.color
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(20, 18, 20, 18)
        # Icon pill + trend row
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setFixedSize(40, 40)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet(
                f"font-size: 20px; background-color: {color}20;"
                f" border: 1px solid {color}30; border-radius: 10px;"
                f" color: {color}; padding: 0;"
            )
            top_row.addWidget(icon_lbl)
        top_row.addStretch()
        layout.addLayout(top_row)
        layout.addSpacing(12)
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {c['text_muted']}; font-size: 11px; font-weight: 700;"
            f" letter-spacing: 0.8px; text-transform: uppercase; background: transparent;"
        )
        layout.addWidget(title_label)
        layout.addSpacing(4)
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            f"color: {c['text_primary']}; font-size: 32px; font-weight: 700;"
            f" letter-spacing: -1px; background: transparent;"
        )
        layout.addWidget(self.value_label)
        # Subtitle
        if subtitle:
            layout.addSpacing(4)
            sub_label = QLabel(subtitle)
            sub_label.setStyleSheet(
                f"color: {c['text_muted']}; font-size: 12px; background: transparent;"
            )
            layout.addWidget(sub_label)
        # Bottom accent bar
        layout.addStretch()
        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(
            f"background-color: {color}; border-radius: 2px; border: none;"
        )
        layout.addWidget(bar)

    def _on_count(self, val):
        self.value_label.setText(str(val))

    def set_value(self, value: str):
        """Set value; if numeric triggers count-up animation."""
        self._raw_value = value
        # Try numeric animation
        clean = value.replace(' ', '').replace('\u00a0', '').replace(',', '')
        try:
            num = int(float(clean.replace('км', '').replace('₽', '').strip()))
            self.value_label.setText('0')
            self._count_anim.animate(num, 700)
        except (ValueError, AttributeError):
            self.value_label.setText(value)

class StatusBadge(QLabel):
    def __init__(self, status, parent=None):
        super().__init__(status, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_status(status)

    def set_status(self, status):
        color = Config.STATUS_COLORS.get(status, Config.COLORS['text_muted'])
        self.setStyleSheet(
            f"background-color: {color}18; color: {color};"
            f" border: 1px solid {color}30; border-radius: 20px;"
            f" padding: 3px 11px; font-size: 12px; font-weight: 600;"
        )
        self.setText(status)

class PriorityBadge(QLabel):
    def __init__(self, priority, parent=None):
        super().__init__(priority, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_priority(priority)

    def set_priority(self, priority):
        color = Config.PRIORITY_COLORS.get(priority, Config.COLORS['text_muted'])
        self.setStyleSheet(
            f"background-color: {color}18; color: {color};"
            f" border: 1px solid {color}30; border-radius: 20px;"
            f" padding: 3px 11px; font-size: 12px; font-weight: 600;"
        )
        self.setText(priority)

class SidebarButton(QPushButton):
    clicked_signal = pyqtSignal()

    def __init__(self, text, icon="", parent=None):
        super().__init__(text, parent)
        self.icon_text = icon
        self.setCheckable(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._setup_style()
        # Opacity effect for press animation
        self._op = QGraphicsOpacityEffect(self)
        self._op.setOpacity(1.0)
        self.setGraphicsEffect(self._op)
        self._press_anim = QPropertyAnimation(self._op, b"opacity")
        self._press_anim.setDuration(120)
        self._press_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _setup_style(self):
        c = Config.COLORS
        accent = c.get('accent', '#6366F1')
        accent_l = c.get('accent_light', '#818CF8')
        self.setStyleSheet(
            f"QPushButton {{ background-color: transparent; color: {c['text_muted']};"
            f" border: none; border-radius: 8px; padding: 9px 14px;"
            f" text-align: left; font-size: 13px; font-weight: 500; min-height: 38px; }}"
            f" QPushButton:hover {{ background-color: {c['bg_hover']}; color: {c['text_secondary']}; }}"
            f" QPushButton:checked {{ background-color: {accent}15; color: {accent_l};"
            f" font-weight: 600; border-left: 3px solid {accent};"
            f" padding-left: 11px; }}"
        )

    def mousePressEvent(self, event):
        self._press_anim.stop()
        self._press_anim.setStartValue(1.0)
        self._press_anim.setEndValue(0.7)
        self._press_anim.start()
        self.clicked_signal.emit()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._press_anim.stop()
        self._press_anim.setStartValue(self._op.opacity())
        self._press_anim.setEndValue(1.0)
        self._press_anim.start()
        super().mouseReleaseEvent(event)

class SearchBox(QLineEdit):
    def __init__(self, placeholder="Поиск...", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(f"  🔍  {placeholder}")
        self.setClearButtonEnabled(True)
        c = Config.COLORS
        accent = c.get('accent', '#6366F1')
        bgi = c.get('bg_input', c['bg_secondary'])
        self.setStyleSheet(
            f"QLineEdit {{ background-color: {bgi}; border: 1px solid {c['border']};"
            f" border-radius: 10px; padding: 9px 16px; font-size: 14px; min-height: 38px; }}"
            f" QLineEdit:focus {{ border-color: {accent}; background-color: {c['bg_card']}; }}"
        )

class LoadingSpinner(QWidget):
    def __init__(self, size=40, parent=None):
        super().__init__(parent)
        self.size = size
        self.angle = 0
        self.setFixedSize(size, size)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)
        self.timer.start(30)

    def _rotate(self):
        self.angle = (self.angle + 10) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center = self.rect().center()
        radius = self.size // 2 - 5
        import math
        for i in range(8):
            angle = self.angle + i * 45
            alpha = 255 - i * 25
            color = QColor(Config.COLORS.get('accent', '#6366F1'))
            color.setAlpha(alpha)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            x = center.x() + radius * 0.7 * math.cos(math.radians(angle))
            y = center.y() + radius * 0.7 * math.sin(math.radians(angle))
            painter.drawEllipse(int(x - 3), int(y - 3), 6, 6)

# =============================================================================
# GOOGLE AUTH THREAD
# =============================================================================

class GoogleAuthThread(QThread):
    """Запускает Google OAuth flow в отдельном потоке, чтобы не блокировать UI."""
    success = pyqtSignal(str, str, str)   # firebase_uid, email, display_name
    error   = pyqtSignal(str)

    def run(self):
        try:
            uid, email, name = FirebaseAuth.sign_in_with_google()
            self.success.emit(uid, email, name)
        except Exception as e:
            self.error.emit(str(e))

# =============================================================================
# ОКНО АВТОРИЗАЦИИ
# =============================================================================

class LoginWindow(QMainWindow):
    login_successful = pyqtSignal(dict)

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle(Config.APP_NAME)
        self.setMinimumSize(820, 540)
        self.setFixedSize(860, 580)
        
        # Устанавливаем иконку окна
        for icon_file in ['avatarka.png', 'img.png']:
            icon_path = get_resource_path(icon_file)
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                break
        
        self.setStyleSheet(self._get_login_stylesheet())
        self._setup_ui()
        self._center_window()

    @staticmethod
    def _get_login_stylesheet():
        c = Config.COLORS
        accent = c.get('accent', '#6366F1')
        accent_l = c.get('accent_light', '#818CF8')
        accent_d = c.get('accent_dark', '#4F46E5')
        bgi = c.get('bg_input', c['bg_secondary'])
        return (
            f"QWidget#loginCentral {{ background-color: {c['bg_primary']}; }}"
            f" QFrame#loginCard {{ background-color: {c['bg_card']};"
            f" border: 1px solid {c['border']}; border-radius: 20px; }}"
            f" QLabel#loginTitle {{ font-size: 24px; font-weight: 700;"
            f" color: {c['text_primary']}; letter-spacing: -0.5px; background: transparent; }}"
            f" QLabel#loginLabel {{ color: {c['text_secondary']}; font-size: 13px;"
            f" font-weight: 500; background: transparent; }}"
            f" QLineEdit#loginInput {{ background-color: {bgi}; border: 1px solid {c['border']};"
            f" border-radius: 10px; padding: 11px 15px; font-size: 14px;"
            f" color: {c['text_primary']}; min-height: 42px; selection-background-color: {accent}; }}"
            f" QLineEdit#loginInput:focus {{ border-color: {accent}; background-color: {c['bg_secondary']}; }}"
            f" QPushButton#loginPrimary {{ background-color: {accent}; color: #FFFFFF;"
            f" border: none; border-radius: 10px; padding: 12px 24px;"
            f" font-size: 14px; font-weight: 600; min-height: 44px; }}"
            f" QPushButton#loginPrimary:hover {{ background-color: {accent_l}; }}"
            f" QPushButton#loginPrimary:pressed {{ background-color: {accent_d}; }}"
        )

    @staticmethod
    def _get_login_primary_button_stylesheet():
        c = Config.COLORS
        accent = c.get('accent', '#6366F1')
        accent_l = c.get('accent_light', '#818CF8')
        accent_d = c.get('accent_dark', '#4F46E5')
        return (
            f"QPushButton {{ background-color: {accent}; color: #FFFFFF;"
            f" border: none; border-radius: 10px; padding: 12px 24px;"
            f" font-size: 14px; font-weight: 600; min-height: 44px; }}"
            f" QPushButton:hover {{ background-color: {accent_l}; }}"
            f" QPushButton:pressed {{ background-color: {accent_d}; }}"
            f" QPushButton:disabled {{ background-color: {c['bg_hover']}; color: {c['text_muted']}; }}"
        )

    def _center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _setup_ui(self):
        c = Config.COLORS
        accent = c.get('accent', '#6366F1')

        central_widget = QWidget()
        central_widget.setObjectName("loginCentral")
        self.setCentralWidget(central_widget)
        root = QHBoxLayout(central_widget)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── LEFT brand panel ──────────────────────────────
        left = QWidget()
        left.setFixedWidth(300)
        left.setStyleSheet(f"background-color: {accent};")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(40, 50, 40, 40)
        ll.setSpacing(0)
        ll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if os.path.exists('img.png'):
            b_logo = QLabel()
            b_logo.setPixmap(
                QPixmap('img.png').scaled(72, 72, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
            )
            b_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            b_logo.setStyleSheet("background: transparent;")
            ll.addWidget(b_logo)
            ll.addSpacing(20)

        b_name = QLabel("CARVIX")
        b_name.setStyleSheet(
            "font-size: 30px; font-weight: 800; color: #FFFFFF;"
            " letter-spacing: 5px; background: transparent;"
        )
        b_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ll.addWidget(b_name)
        ll.addSpacing(10)

        tagline = QLabel("Fleet Management System")
        tagline.setStyleSheet(
            "font-size: 13px; color: rgba(255,255,255,0.70); background: transparent;"
        )
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ll.addWidget(tagline)
        ll.addStretch()

        for feat in ["📊  Аналитика и отчёты", "🔧  Управление ремонтами", "🚗  Контроль автопарка"]:
            fl = QLabel(feat)
            fl.setStyleSheet(
                "font-size: 12px; color: rgba(255,255,255,0.80);"
                " background: transparent; padding: 3px 0;"
            )
            ll.addWidget(fl)

        ll.addSpacing(28)
        ver_lbl = QLabel(f"Firebase Auth  •  v{Config.APP_VERSION}")
        ver_lbl.setStyleSheet(
            "font-size: 10px; color: rgba(255,255,255,0.40); background: transparent;"
        )
        ver_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ll.addWidget(ver_lbl)
        root.addWidget(left)

        # ── RIGHT forms panel ──────────────────────────────
        right = QWidget()
        right.setStyleSheet(f"background-color: {c['bg_primary']};")
        right_outer = QVBoxLayout(right)
        right_outer.setContentsMargins(0, 0, 0, 0)
        right_outer.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Stacked: 0=login, 1=register
        self._form_stack = QStackedWidget()
        self._form_stack.setStyleSheet("background: transparent;")
        right_outer.addWidget(self._form_stack)

        # --- Login form ---
        self._form_stack.addWidget(self._build_login_form(c, accent))

        # --- Register form ---
        self._form_stack.addWidget(self._build_register_form(c, accent))

        self._form_stack.setCurrentIndex(0)
        root.addWidget(right, 1)

    def _make_field_label(self, text, c):
        lbl = QLabel(text)
        lbl.setObjectName("loginLabel")
        lbl.setStyleSheet("background: transparent;")
        return lbl

    def _make_input(self, placeholder, password=False):
        inp = QLineEdit()
        inp.setObjectName("loginInput")
        inp.setPlaceholderText(placeholder)
        inp.setMinimumHeight(44)
        if password:
            inp.setEchoMode(QLineEdit.EchoMode.Password)
        return inp

    def _build_login_form(self, c, accent):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(60, 0, 60, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.setSpacing(0)

        title = QLabel("Войти в аккаунт")
        title.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {c['text_primary']}; background: transparent;"
        )
        layout.addWidget(title)
        subtitle = QLabel("Вход через зарегистрированный email")
        subtitle.setStyleSheet(
            f"font-size: 13px; color: {c['text_muted']}; background: transparent;"
        )
        layout.addWidget(subtitle)
        layout.addSpacing(28)

        layout.addWidget(self._make_field_label("Email", c))
        layout.addSpacing(5)
        self.login_input = self._make_input("Введите email")
        layout.addWidget(self.login_input)
        layout.addSpacing(14)

        layout.addWidget(self._make_field_label("Пароль", c))
        layout.addSpacing(5)
        self.password_input = self._make_input("Введите пароль", password=True)
        self.password_input.returnPressed.connect(self._handle_login)
        layout.addWidget(self.password_input)
        layout.addSpacing(22)

        self.login_button = QPushButton("Войти")
        self.login_button.setObjectName("loginPrimary")
        self.login_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.login_button.setFixedHeight(44)
        self.login_button.setDefault(True)
        self.login_button.setStyleSheet(self._get_login_primary_button_stylesheet())
        self.login_button.clicked.connect(self._handle_login)
        layout.addWidget(self.login_button)
        layout.addSpacing(16)

        switch = QPushButton("Нет аккаунта?  Зарегистрироваться")
        switch.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {accent};"
            f" border: none; font-size: 13px; text-align: left; }}"
            f" QPushButton:hover {{ color: {c.get('accent_light', accent)}; }}"
        )
        switch.clicked.connect(lambda: self._form_stack.setCurrentIndex(1))
        layout.addWidget(switch)
        layout.addSpacing(16)

        # Divider
        div_row = QHBoxLayout()
        div_row.setSpacing(8)
        for _ in range(2):
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setStyleSheet(f"color: {c['border']}; background: {c['border']};")
            div_row.addWidget(line, 1)
        or_lbl = QLabel("или")
        or_lbl.setStyleSheet(
            f"color: {c['text_muted']}; font-size: 11px; background: transparent;"
        )
        div_row.insertWidget(1, or_lbl)
        layout.addLayout(div_row)
        layout.addSpacing(12)

        google_btn = QPushButton("  Войти через Google")
        google_btn.setFixedHeight(44)
        google_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        google_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c['bg_card']};"
            f" color: {c['text_primary']}; border: 1px solid {c['border']};"
            f" border-radius: 8px; font-size: 13px; font-weight: 500;"
            f" padding: 0 16px; text-align: center; }}"
            f" QPushButton:hover {{ background-color: {c['bg_hover']};"
            f" border-color: {c.get('accent', '#6366F1')}; }}"
        )
        google_btn.clicked.connect(self._start_google_auth)
        layout.addWidget(google_btn)
        layout.addStretch()
        return w

    def _build_register_form(self, c, accent):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(60, 0, 60, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.setSpacing(0)

        title = QLabel("Создать аккаунт")
        title.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {c['text_primary']}; background: transparent;"
        )
        layout.addWidget(title)
        subtitle = QLabel("Регистрация через Google Firebase")
        subtitle.setStyleSheet(
            f"font-size: 13px; color: {c['text_muted']}; background: transparent;"
        )
        layout.addWidget(subtitle)
        layout.addSpacing(22)

        layout.addWidget(self._make_field_label("Полное имя", c))
        layout.addSpacing(5)
        self.reg_name_input = self._make_input("Имя Фамилия Отчество")
        layout.addWidget(self.reg_name_input)
        layout.addSpacing(12)

        layout.addWidget(self._make_field_label("Email", c))
        layout.addSpacing(5)
        self.reg_email_input = self._make_input("Введите email")
        layout.addWidget(self.reg_email_input)
        layout.addSpacing(12)

        layout.addWidget(self._make_field_label("Пароль (min 6 символов)", c))
        layout.addSpacing(5)
        self.reg_password_input = self._make_input("Введите пароль", password=True)
        layout.addWidget(self.reg_password_input)
        layout.addSpacing(12)

        layout.addWidget(self._make_field_label("Подтверждение пароля", c))
        layout.addSpacing(5)
        self.reg_confirm_input = self._make_input("Повторите пароль", password=True)
        self.reg_confirm_input.returnPressed.connect(self._handle_register)
        layout.addWidget(self.reg_confirm_input)
        layout.addSpacing(20)

        reg_btn = QPushButton("Зарегистрироваться")
        reg_btn.setObjectName("loginPrimary")
        reg_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        reg_btn.setFixedHeight(44)
        reg_btn.setStyleSheet(self._get_login_primary_button_stylesheet())
        reg_btn.clicked.connect(self._handle_register)
        layout.addWidget(reg_btn)
        layout.addSpacing(14)

        switch = QPushButton("Уже есть аккаунт?  Войти")
        switch.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {accent};"
            f" border: none; font-size: 13px; text-align: left; }}"
            f" QPushButton:hover {{ color: {c.get('accent_light', accent)}; }}"
        )
        switch.clicked.connect(lambda: self._form_stack.setCurrentIndex(0))
        layout.addWidget(switch)
        layout.addStretch()
        return w

    def _handle_login(self):
        email = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Ошибка", "Введите email и пароль")
            return

        self.login_button.setEnabled(False)
        self.login_button.setText("Проверка...")
        QApplication.processEvents()

        try:
            # ── Dev-режим: локальный вход без Firebase ────────────────
            dev_user = self.db.execute_one("""
                SELECT u.*, r.name as role_name, r.permissions
                FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE u.email = ? AND u.is_active = 1
                  AND u.firebase_uid LIKE 'DEV_LOCAL_%'
            """, (email,))
            if dev_user:
                dev_dict = dict(dev_user)
                ok = Database._dev_verify(password, dev_dict.get('password_hash', ''))
                if ok:
                    self.db.execute_update(
                        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                        (dev_dict['id'],)
                    )
                    self.login_successful.emit(dev_dict)
                    self.close()
                    return
                else:
                    QMessageBox.warning(self, "Ошибка входа", "Неверный пароль")
                    return

            # ── Firebase auth ─────────────────────────────────────────
            firebase_uid, _ = FirebaseAuth.sign_in(email, password)

            user = self.db.execute_one("""
                SELECT u.*, r.name as role_name, r.permissions
                FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE u.firebase_uid = ? AND u.is_active = 1
            """, (firebase_uid,))

            if not user:
                QMessageBox.warning(
                    self, "Доступ запрещён",
                    "Аккаунт Firebase найден, но пользователь не зарегистрирован в системе.\n"
                    "Перейдите на вкладку «Регистрация» и зарегистрируйтесь."
                )
                return

            user_dict = dict(user)
            self.db.execute_update(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user_dict['id'],)
            )
            self.login_successful.emit(user_dict)
            self.close()

        except Exception as e:
            logger.error(f"Login error: {e}")
            QMessageBox.critical(self, "Ошибка входа", str(e))
        finally:
            self.login_button.setEnabled(True)
            self.login_button.setText("Войти")

    def _start_google_auth(self):
        """Запускает Google OAuth flow в отдельном потоке."""
        self._google_thread = GoogleAuthThread()
        self._google_thread.success.connect(self._handle_google_auth)
        self._google_thread.error.connect(
            lambda msg: QMessageBox.critical(self, "Ошибка Google", msg)
        )
        self._google_thread.start()

    def _handle_google_auth(self, firebase_uid: str, email: str, display_name: str):
        """Вызывается после успешного Google OAuth.
        Если пользователь уже есть в БД — входит, иначе — регистрирует.
        """
        try:
            user = self.db.execute_one("""
                SELECT u.*, r.name as role_name, r.permissions
                FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE u.firebase_uid = ? AND u.is_active = 1
            """, (firebase_uid,))

            if user:
                # Уже зарегистрирован — просто входим
                self.db.execute_update(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                    (dict(user)['id'],)
                )
                self.login_successful.emit(dict(user))
                self.close()
                return

            # Новый пользователь — авторегистрация
            users_count = self.db.execute_one("SELECT COUNT(*) FROM users")[0]
            role_name = 'Администратор' if users_count == 0 else 'Пользователь'
            role = self.db.execute_one(
                "SELECT id FROM roles WHERE name = ?", (role_name,)
            )
            if not role:
                QMessageBox.critical(self, "Ошибка", "Роли не найдены в БД.")
                return

            full_name = display_name or email.split('@')[0]
            self.db.execute_insert("""
                INSERT INTO users
                  (username, password_hash, firebase_uid, full_name, email, role_id, is_active)
                VALUES (?, '', ?, ?, ?, ?, 1)
            """, (email, firebase_uid, full_name, email, role['id']))

            # Загружаем только что созданного пользователя
            user = self.db.execute_one("""
                SELECT u.*, r.name as role_name, r.permissions
                FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE u.firebase_uid = ?
            """, (firebase_uid,))

            QMessageBox.information(
                self, "Аккаунт создан",
                f"Добро пожаловать, {full_name}!\nРоль: {role_name}"
            )
            self.login_successful.emit(dict(user))
            self.close()

        except Exception as e:
            logger.error(f"Google auth handler error: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))

    def _handle_register(self):
        full_name = self.reg_name_input.text().strip()
        email = self.reg_email_input.text().strip()
        password = self.reg_password_input.text()
        confirm = self.reg_confirm_input.text()

        if not full_name or not email or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return
        if len(password) < 6:
            QMessageBox.warning(self, "Ошибка", "Пароль должен быть не менее 6 символов")
            return

        try:
            # Определяем роль: первый участник — админ, остальные — Пользователь
            users_count = self.db.execute_one("SELECT COUNT(*) FROM users")[0]
            role_name = 'Администратор' if users_count == 0 else 'Пользователь'

            role = self.db.execute_one(
                "SELECT id FROM roles WHERE name = ?", (role_name,)
            )
            if not role:
                QMessageBox.critical(self, "Ошибка", "Роли не найдены в БД. Перезапустите приложение.")
                return

            firebase_uid, _ = FirebaseAuth.sign_up(email, password)

            self.db.execute_insert("""
                INSERT INTO users
                  (username, password_hash, firebase_uid, full_name, email, role_id, is_active)
                VALUES (?, '', ?, ?, ?, ?, 1)
            """, (email, firebase_uid, full_name, email, role['id']))

            QMessageBox.information(
                self, "Регистрация завершена",
                f"Аккаунт создан.\nРоль: {role_name}\n\nТеперь войдите с этим email и паролем."
            )
            self._form_stack.setCurrentIndex(0)
            self.login_input.setText(email)

        except Exception as e:
            logger.error(f"Register error: {e}")
            QMessageBox.critical(self, "Ошибка регистрации", str(e))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self._handle_login()
        super().keyPressEvent(event)

# =============================================================================
# ГЛАВНОЕ ОКНО
# =============================================================================

class MainWindow(QMainWindow):
    def __init__(self, db, current_user):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.role = current_user.get('role_name', '')
        self.setWindowTitle(f"{Config.APP_NAME} - {self.current_user.get('full_name', '')}")
        self.setMinimumSize(1400, 900)
        
        # Устанавливаем иконку окна
        for icon_file in ['avatarka.png', 'img.png']:
            icon_path = get_resource_path(icon_file)
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                break
        
        self.setStyleSheet(Styles.get_main_stylesheet())
        self._setup_ui()
        self._center_window()
        self.showMaximized()

    def _center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        central_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {Config.COLORS['bg_primary']};
            }}
        """)

        # Боковая панель
        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar)

        # Контентная область
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"background-color: {Config.COLORS['bg_primary']};")
        main_layout.addWidget(self.content_stack, 1)

        # Создаем страницы
        self._create_pages()

    def _create_sidebar(self):
        c = Config.COLORS
        accent = c.get('accent', '#6366F1')
        err = c.get('error', '#EF4444')

        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(
            f"QWidget {{ background-color: {c['bg_secondary']};"
            f" border-right: 1px solid {c['border']}; }}"
        )
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # ── Logo strip ────────────────────────────────────────────────
        logo_strip = QWidget()
        logo_strip.setFixedHeight(60)
        logo_strip.setStyleSheet(
            f"QWidget {{ background-color: {c['bg_secondary']};"
            f" border-bottom: 1px solid {c['border']}; }}"
        )
        logo_row = QHBoxLayout(logo_strip)
        logo_row.setContentsMargins(16, 0, 16, 0)
        logo_row.setSpacing(10)
        if os.path.exists('img.png'):
            logo_img = QLabel()
            px = QPixmap('img.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
            logo_img.setPixmap(px)
            logo_img.setStyleSheet("background: transparent;")
            logo_row.addWidget(logo_img)
        logo_text = QLabel("CARVIX")
        logo_text.setStyleSheet(
            f"font-size: 16px; font-weight: 800; color: {c['text_primary']};"
            f" letter-spacing: 3px; background: transparent;"
        )
        logo_row.addWidget(logo_text)
        logo_row.addStretch()
        layout.addWidget(logo_strip)

        # ── User info block ───────────────────────────────────────────
        user_block = QWidget()
        user_block.setStyleSheet("background: transparent;")
        user_layout = QHBoxLayout(user_block)
        user_layout.setContentsMargins(16, 14, 16, 12)
        user_layout.setSpacing(10)

        avatar = QLabel(self.current_user.get('full_name', 'U')[0].upper())
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(
            f"background-color: {accent}25; color: {accent}; font-size: 15px;"
            f" font-weight: 700; border-radius: 18px; border: 1px solid {accent}40;"
        )
        user_layout.addWidget(avatar)

        text_col = QVBoxLayout()
        text_col.setSpacing(1)
        name_lbl = QLabel(self.current_user.get('full_name', ''))
        name_lbl.setStyleSheet(
            f"color: {c['text_primary']}; font-size: 13px; font-weight: 600; background: transparent;"
        )
        role_lbl = QLabel(self.role)
        role_lbl.setStyleSheet(
            f"color: {c['text_muted']}; font-size: 11px; background: transparent;"
        )
        text_col.addWidget(name_lbl)
        text_col.addWidget(role_lbl)
        user_layout.addLayout(text_col)
        user_layout.addStretch()

        # Notification badge
        notif_badge = QFrame()
        notif_badge.setStyleSheet(
            f"QFrame {{ background-color: {accent}18; border-radius: 10px; border: 1px solid {accent}30; }}"
        )
        nb_layout = QHBoxLayout(notif_badge)
        nb_layout.setContentsMargins(7, 3, 7, 3)
        nb_layout.setSpacing(3)
        nb_icon = QLabel("🔔")
        nb_icon.setStyleSheet("font-size: 11px; background: transparent;")
        nb_layout.addWidget(nb_icon)
        self.notif_count_label = QLabel("0")
        self.notif_count_label.setStyleSheet(
            f"color: {accent}; font-size: 11px; font-weight: 700; background: transparent;"
        )
        nb_layout.addWidget(self.notif_count_label)
        user_layout.addWidget(notif_badge)

        layout.addWidget(user_block)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"color: {c['border']}; background: {c['border']}; max-height: 1px;")
        layout.addWidget(div)

        # ── Navigation ────────────────────────────────────────────────
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        nav_scroll.setStyleSheet("background: transparent; border: none;")

        nav_widget = QWidget()
        nav_widget.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setSpacing(1)
        nav_layout.setContentsMargins(8, 8, 8, 8)

        self.menu_buttons = {}
        self._update_notifications_count()

        def section(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(
                f"color: {c['text_muted']}; font-size: 10px; font-weight: 700;"
                f" letter-spacing: 1.2px; background: transparent;"
                f" padding: 10px 8px 4px 8px;"
            )
            nav_layout.addWidget(lbl)

        # Main navigation
        section("НАВИГАЦИЯ")
        if self.role in ['Администратор', 'Директор', 'Аналитик', 'Главный механик', 'Диспетчер']:
            self._add_menu_button(nav_layout, "dashboard", "📊", "Дашборд")
        if self.role in ['Администратор', 'Главный механик', 'Диспетчер']:
            self._add_menu_button(nav_layout, "requests", "🔧", "Заявки на ремонт")
        elif self.role in ['Механик', 'Пользователь']:
            icon = "🔧" if self.role == 'Механик' else "📋"
            self._add_menu_button(nav_layout, "my_requests", icon, "Мои заявки")
        if self.role in ['Администратор', 'Главный механик', 'Диспетчер']:
            self._add_menu_button(nav_layout, "maintenance", "🔩", "Техобслуживание")
        if self.role in ['Администратор', 'Главный механик', 'Диспетчер', 'Аналитик']:
            self._add_menu_button(nav_layout, "vehicles", "🚗", "Автопарк")

        # Reports
        if self.role in ['Администратор', 'Директор', 'Аналитик']:
            section("АНАЛИТИКА")
            self._add_menu_button(nav_layout, "analytics", "📈", "Аналитика")

        # Admin
        if self.role == 'Администратор':
            section("УПРАВЛЕНИЕ")
            self._add_menu_button(nav_layout, "users", "👥", "Пользователи")
            self._add_menu_button(nav_layout, "reference", "📚", "Справочники")
        if self.role in ['Администратор', 'Главный механик']:
            self._add_menu_button(nav_layout, "parts", "⚙️", "Запчасти")

        nav_layout.addStretch()
        nav_scroll.setWidget(nav_widget)
        layout.addWidget(nav_scroll, 1)

        # Divider
        div2 = QFrame()
        div2.setFrameShape(QFrame.Shape.HLine)
        div2.setStyleSheet(f"color: {c['border']}; background: {c['border']}; max-height: 1px;")
        layout.addWidget(div2)

        # ── Bottom section ────────────────────────────────────────────
        bottom = QWidget()
        bottom.setStyleSheet("background: transparent;")
        bottom_layout = QVBoxLayout(bottom)
        bottom_layout.setSpacing(1)
        bottom_layout.setContentsMargins(8, 8, 8, 8)

        self._add_menu_button(bottom_layout, "profile", "👤", "Профиль")
        self._add_menu_button(bottom_layout, "settings", "⚙️", "Настройки")

        logout_btn = QPushButton("🚪  Выход из системы")
        logout_btn.setStyleSheet(
            f"QPushButton {{ background-color: transparent; color: {c['text_secondary']};"
            f" border: none; border-radius: 8px; padding: 9px 14px; text-align: left;"
            f" font-size: 13px; font-weight: 500; min-height: 38px; }}"
            f" QPushButton:hover {{ background-color: {err}18; color: {err}; }}"
        )
        logout_btn.clicked.connect(self._logout)
        bottom_layout.addWidget(logout_btn)
        layout.addWidget(bottom)

        return sidebar

    def _add_menu_button(self, layout, page_id, icon, text):
        btn = SidebarButton(f"{icon}  {text}")
        btn.clicked_signal.connect(lambda: self._switch_page(page_id))
        layout.addWidget(btn)
        self.menu_buttons[page_id] = btn

    def _switch_page(self, page_id):
        for btn in self.menu_buttons.values():
            btn.setChecked(False)
        if page_id in self.menu_buttons:
            self.menu_buttons[page_id].setChecked(True)

        page_map = {
            "dashboard": 0,
            "requests": 1,
            "my_requests": 2,
            "maintenance": 3,
            "vehicles": 4,
            "analytics": 5,
            "users": 6,
            "reference": 7,
            "parts": 8,
            "profile": 9,
            "settings": 10,
        }
        if page_id in page_map:
            idx = page_map[page_id]
            self.content_stack.setCurrentIndex(idx)
            # Trigger page refresh callback if registered
            refresh_fn = getattr(self, '_page_refresh_callbacks', {}).get(page_id)
            if refresh_fn:
                try:
                    refresh_fn()
                except Exception as e:
                    logger.warning(f"Page refresh error for {page_id}: {e}")

    def _create_pages(self):
        self._page_refresh_callbacks = {}

        # Страница 0: Дашборд
        self.content_stack.addWidget(self._create_dashboard_page())
        self._page_refresh_callbacks["dashboard"] = self._update_dashboard
        # Страница 1: Заявки на ремонт
        self.content_stack.addWidget(self._create_requests_page())
        self._page_refresh_callbacks["requests"] = self._load_requests
        # Страница 2: Мои заявки
        self.content_stack.addWidget(self._create_my_requests_page())
        self._page_refresh_callbacks["my_requests"] = self._load_my_requests
        # Страница 3: ТО
        self.content_stack.addWidget(self._create_maintenance_page())
        self._page_refresh_callbacks["maintenance"] = self._load_maintenance
        # Страница 4: Автопарк
        self.content_stack.addWidget(self._create_vehicles_page())
        self._page_refresh_callbacks["vehicles"] = self._load_vehicles
        # Страница 5: Аналитика
        self.content_stack.addWidget(self._create_analytics_page())
        # Страница 6: Пользователи
        self.content_stack.addWidget(self._create_users_page())
        self._page_refresh_callbacks["users"] = self._load_users
        # Страница 7: Справочники
        self.content_stack.addWidget(self._create_reference_page())
        # Страница 8: Запчасти
        self.content_stack.addWidget(self._create_parts_page())
        self._page_refresh_callbacks["parts"] = self._load_parts
        # Страница 9: Профиль
        self.content_stack.addWidget(self._create_profile_page())
        # Страница 10: Настройки
        self.content_stack.addWidget(self._create_settings_page())

        # Устанавливаем начальную страницу
        if "dashboard" in self.menu_buttons:
            self._switch_page("dashboard")
        elif "my_requests" in self.menu_buttons:
            self._switch_page("my_requests")
        elif "requests" in self.menu_buttons:
            self._switch_page("requests")

    def _update_notifications_count(self):
        """Обновление счетчика непрочитанных уведомлений"""
        try:
            count = self.db.execute_one(
                "SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0",
                (self.current_user['id'],)
            )[0] or 0
            self.notif_count_label.setText(str(count))
            accent = Config.COLORS.get('accent', '#6366F1')
            if count > 0:
                self.notif_count_label.setStyleSheet(f"color: {accent}; font-size: 13px; font-weight: 700; background: transparent;")
            else:
                self.notif_count_label.setStyleSheet(f"color: {Config.COLORS['text_primary']}; font-size: 13px; font-weight: 600; background: transparent;")
        except Exception as e:
            logger.error(f"Error updating notifications count: {e}")
    
    def _create_notification(self, user_id, title, message, notif_type='info', related_request_id=None):
        """Создание уведомления"""
        try:
            self.db.cursor.execute(
                """INSERT INTO notifications (user_id, title, message, type, related_request_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, title, message, notif_type, related_request_id)
            )
            self.db.connection.commit()
            self._update_notifications_count()
        except Exception as e:
            logger.error(f"Error creating notification: {e}")

    def _logout(self):
        reply = QMessageBox.question(self, "Подтверждение", "Вы действительно хотите выйти?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            from PyQt6.QtCore import QProcess
            QProcess.startDetached(sys.executable, sys.argv)

    # =============================================================================
    # СТРАНИЦА ДАШБОРДА
    # =============================================================================

    def _create_dashboard_page(self):
        c = Config.COLORS
        accent = c.get('accent', '#6366F1')
        page = QWidget()
        page.setStyleSheet(f"background-color: {c['bg_primary']};")
        main_layout = QVBoxLayout(page)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ── Greeting header bar ──────────────────────────────────────
        header_bar = QWidget()
        header_bar.setFixedHeight(76)
        header_bar.setStyleSheet(
            f"QWidget {{ background-color: {c['bg_secondary']};"
            f" border-bottom: 1px solid {c['border']}; }}"
        )
        hdr = QHBoxLayout(header_bar)
        hdr.setContentsMargins(28, 0, 28, 0)

        now = datetime.now()
        hour = now.hour
        grt = "Доброе утро" if hour < 12 else ("Добрый день" if hour < 18 else "Добрый вечер")
        name_part = self.current_user.get('full_name', '').split()[0] if self.current_user.get('full_name') else ''
        greet_lbl = QLabel(f"{grt}{(', ' + name_part) if name_part else ''}!")
        greet_lbl.setStyleSheet(
            f"font-size: 19px; font-weight: 700; color: {c['text_primary']}; background: transparent;"
        )
        date_lbl = QLabel(now.strftime("%d %B %Y, %A"))
        date_lbl.setStyleSheet(
            f"font-size: 12px; color: {c['text_muted']}; background: transparent;"
        )
        greet_col = QVBoxLayout()
        greet_col.setSpacing(2)
        greet_col.addWidget(greet_lbl)
        greet_col.addWidget(date_lbl)
        hdr.addLayout(greet_col)
        hdr.addStretch()

        refresh_btn = QPushButton("↻  Обновить")
        refresh_btn.setObjectName("secondary")
        refresh_btn.setFixedHeight(34)
        refresh_btn.clicked.connect(self._update_dashboard)
        hdr.addWidget(refresh_btn)
        main_layout.addWidget(header_bar)

        # ── Scrollable content ──────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        content_w = QWidget()
        content_w.setStyleSheet(f"background-color: {c['bg_primary']};")
        layout = QVBoxLayout(content_w)
        layout.setSpacing(20)
        layout.setContentsMargins(28, 24, 28, 24)

        # ── KPI cards ───────────────────────────────────────────────
        total_vehicles = len(self.db.execute("SELECT id FROM vehicles"))
        active_repairs = len(self.db.execute(
            "SELECT id FROM repair_requests WHERE status IN ('Новая', 'Принята', 'В работе')"
        ))
        completed_month = len(self.db.execute("""
            SELECT id FROM repair_requests
            WHERE status = 'Закрыта'
            AND strftime('%Y-%m', closed_at) = strftime('%Y-%m', 'now')
        """))
        avg_mileage = self.db.execute_one("SELECT AVG(mileage) FROM vehicles")[0] or 0

        self.metric_cards = {}
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(14)
        cards_data = [
            ('vehicles', "АВТОМОБИЛЕЙ",  str(total_vehicles),                         "Всего в парке",   "🚗", accent),
            ('repairs',  "В РЕМОНТЕ",    str(active_repairs),                          "Активных заявок", "🔧", c.get('error', '#EF4444')),
            ('completed',"ВЫПОЛНЕНО",    str(completed_month),                         "За этот месяц",   "✅", c.get('success', '#10B981')),
            ('mileage',  "ПРОБЕГ",       f"{int(avg_mileage):,} км".replace(',', ' '), "Средний по парку","📊", c.get('accent_purple', '#8B5CF6')),
        ]
        for key, title, val, sub, icon, color in cards_data:
            card = MetricCard(title, val, sub, icon, color)
            kpi_layout.addWidget(card)
            self.metric_cards[key] = card
        layout.addLayout(kpi_layout)

        # ── Two-column content area ──────────────────────────────────
        cols = QHBoxLayout()
        cols.setSpacing(16)

        # Left: recent requests table
        table_card = Card()
        table_card_layout = QVBoxLayout(table_card)
        table_card_layout.setContentsMargins(18, 16, 18, 16)
        table_card_layout.setSpacing(12)

        tbl_hdr = QHBoxLayout()
        tbl_title = QLabel("Последние заявки")
        tbl_title.setStyleSheet(
            f"font-size: 14px; font-weight: 700; color: {c['text_primary']}; background: transparent;"
        )
        tbl_hdr.addWidget(tbl_title)
        tbl_hdr.addStretch()
        view_all = QPushButton("Все заявки →")
        view_all.setObjectName("secondary")
        view_all.setFixedHeight(28)
        view_all.clicked.connect(
            lambda: self._switch_page("requests" if "requests" in self.menu_buttons else "my_requests")
        )
        tbl_hdr.addWidget(view_all)
        table_card_layout.addLayout(tbl_hdr)

        self.recent_requests_table = QTableWidget()
        self.recent_requests_table.setColumnCount(5)
        self.recent_requests_table.setHorizontalHeaderLabels(["Номер", "Авто", "Статус", "Дата", "Приоритет"])
        self.recent_requests_table.horizontalHeader().setStretchLastSection(True)
        self.recent_requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.recent_requests_table.verticalHeader().setVisible(False)
        self.recent_requests_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.recent_requests_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.recent_requests_table.setAlternatingRowColors(True)
        table_card_layout.addWidget(self.recent_requests_table)
        cols.addWidget(table_card, 3)

        # Right: status chart + quick breakdown
        right_col = QVBoxLayout()
        right_col.setSpacing(14)

        status_chart = self._create_status_chart()
        right_col.addWidget(status_chart)

        # Vehicle status breakdown card
        breakdown_card = Card()
        bk_layout = QVBoxLayout(breakdown_card)
        bk_layout.setContentsMargins(18, 14, 18, 14)
        bk_layout.setSpacing(10)
        bk_title = QLabel("Состояние автопарка")
        bk_title.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {c['text_primary']}; background: transparent;"
        )
        bk_layout.addWidget(bk_title)
        try:
            for row in self.db.execute("SELECT status, COUNT(*) as cnt FROM vehicles GROUP BY status"):
                row_w = QWidget()
                row_w.setStyleSheet("background: transparent;")
                row_l = QHBoxLayout(row_w)
                row_l.setContentsMargins(0, 0, 0, 0)
                row_l.setSpacing(8)
                dot = QLabel("●")
                sc = Config.STATUS_COLORS.get(row['status'], c['text_muted'])
                dot.setStyleSheet(f"color: {sc}; font-size: 10px; background: transparent;")
                row_l.addWidget(dot)
                nm = QLabel(row['status'])
                nm.setStyleSheet(f"color: {c['text_secondary']}; font-size: 13px; background: transparent;")
                row_l.addWidget(nm)
                row_l.addStretch()
                cnt = QLabel(str(row['cnt']))
                cnt.setStyleSheet(
                    f"color: {c['text_primary']}; font-size: 13px; font-weight: 700; background: transparent;"
                )
                row_l.addWidget(cnt)
                bk_layout.addWidget(row_w)
        except Exception:
            pass
        right_col.addWidget(breakdown_card)
        right_col.addStretch()
        cols.addLayout(right_col, 2)

        layout.addLayout(cols)
        layout.addStretch()
        scroll.setWidget(content_w)
        main_layout.addWidget(scroll, 1)

        self._load_recent_requests()
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_dashboard)
        self.update_timer.start(30000)
        return page

    def _create_status_chart(self):
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Статусы автомобилей")
        title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {Config.COLORS['text_primary']};")
        layout.addWidget(title)

        if MATPLOTLIB_AVAILABLE:
            figure = Figure(figsize=(5, 3), facecolor=Config.COLORS['bg_card'])
            ax = figure.add_subplot(111)
            ax.set_facecolor(Config.COLORS['bg_card'])

            # Данные для круговой диаграммы
            statuses = self.db.execute("""
                SELECT status, COUNT(*) as count FROM vehicles GROUP BY status
            """)

            if statuses:
                labels = [s['status'] for s in statuses]
                values = [s['count'] for s in statuses]
                colors_list = [Config.COLORS['accent_cyan'], Config.COLORS['accent_pink'], 
                              Config.COLORS['accent_green'], Config.COLORS['accent_purple']]

                ax.pie(values, labels=labels, autopct='%1.0f%%', startangle=90,
                       colors=colors_list[:len(labels)],
                       textprops={'color': Config.COLORS['text_primary']})

            canvas = FigureCanvas(figure)
            layout.addWidget(canvas)
        else:
            no_chart = QLabel("Графики недоступны (matplotlib не установлен)")
            no_chart.setStyleSheet(f"color: {Config.COLORS['text_secondary']};")
            layout.addWidget(no_chart)

        return card

    def _create_requests_chart(self):
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Заявки по месяцам")
        title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {Config.COLORS['text_primary']};")
        layout.addWidget(title)

        if MATPLOTLIB_AVAILABLE:
            figure = Figure(figsize=(5, 3), facecolor=Config.COLORS['bg_card'])
            ax = figure.add_subplot(111)
            ax.set_facecolor(Config.COLORS['bg_card'])

            # Данные для графика
            data = self.db.execute("""
                SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count 
                FROM repair_requests 
                GROUP BY month 
                ORDER BY month DESC 
                LIMIT 6
            """)

            if data:
                months = [d['month'] for d in reversed(data)]
                counts = [d['count'] for d in reversed(data)]

                ax.plot(months, counts, marker='o', color=Config.COLORS['accent_cyan'], linewidth=2)
                ax.fill_between(months, counts, alpha=0.3, color=Config.COLORS['accent_cyan'])
                tc = Config.COLORS['text_secondary']
                bc = Config.COLORS['border']
                ax.set_xlabel('Месяц', color=tc)
                ax.set_ylabel('Количество', color=tc)
                ax.tick_params(colors=tc)
                ax.spines['bottom'].set_color(bc)
                ax.spines['left'].set_color(bc)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

            canvas = FigureCanvas(figure)
            layout.addWidget(canvas)
        else:
            no_chart = QLabel("Графики недоступны")
            no_chart.setStyleSheet(f"color: {Config.COLORS['text_secondary']};")
            layout.addWidget(no_chart)

        return card

    def _load_recent_requests(self):
        requests = self.db.execute("""
            SELECT r.request_number, v.vehicle_number, r.status, r.created_at, r.priority
            FROM repair_requests r
            JOIN vehicles v ON r.vehicle_id = v.id
            ORDER BY r.created_at DESC
            LIMIT 10
        """)

        self.recent_requests_table.setRowCount(len(requests))
        for i, req in enumerate(requests):
            self.recent_requests_table.setItem(i, 0, QTableWidgetItem(req['request_number']))
            self.recent_requests_table.setItem(i, 1, QTableWidgetItem(req['vehicle_number']))

            status_item = QTableWidgetItem(req['status'])
            status_color = Config.STATUS_COLORS.get(req['status'], Config.COLORS['text_secondary'])
            status_item.setForeground(QColor(status_color))
            self.recent_requests_table.setItem(i, 2, status_item)

            self.recent_requests_table.setItem(i, 3, QTableWidgetItem(str(req['created_at'])[:10]))

            priority_item = QTableWidgetItem(req['priority'])
            priority_color = Config.PRIORITY_COLORS.get(req['priority'], Config.COLORS['text_secondary'])
            priority_item.setForeground(QColor(priority_color))
            self.recent_requests_table.setItem(i, 4, priority_item)

        self.recent_requests_table.resizeColumnsToContents()

    def _update_dashboard(self):
        # Обновляем метрики
        total_vehicles = len(self.db.execute("SELECT id FROM vehicles"))
        active_repairs = len(self.db.execute("SELECT id FROM repair_requests WHERE status IN ('Новая', 'Принята', 'В работе')"))
        completed_month = len(self.db.execute("""
            SELECT id FROM repair_requests 
            WHERE status = 'Закрыта' 
            AND strftime('%Y-%m', closed_at) = strftime('%Y-%m', 'now')
        """))
        avg_mileage = self.db.execute_one("SELECT AVG(mileage) FROM vehicles")[0] or 0

        self.metric_cards['vehicles'].set_value(str(total_vehicles))
        self.metric_cards['repairs'].set_value(str(active_repairs))
        self.metric_cards['completed'].set_value(str(completed_month))
        self.metric_cards['mileage'].set_value(f"{int(avg_mileage):,} км".replace(',', ' '))

        self._load_recent_requests()

    # =============================================================================
    # СТРАНИЦА ЗАЯВОК НА РЕМОНТ
    # =============================================================================

    def _create_requests_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Заголовок
        header_layout = QHBoxLayout()
        header = QLabel("🔧 Управление ремонтами")
        header.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {Config.COLORS['text_primary']}; background: transparent;")
        header_layout.addWidget(header)
        header_layout.addStretch()

        create_btn = QPushButton("+ Создать заявку")
        create_btn.clicked.connect(self._show_create_request_dialog)
        header_layout.addWidget(create_btn)

        export_pdf_btn = QPushButton("📄 PDF")
        export_pdf_btn.setObjectName("secondary")
        export_pdf_btn.clicked.connect(lambda: self._export_requests('pdf'))
        header_layout.addWidget(export_pdf_btn)

        layout.addLayout(header_layout)

        # Фильтры
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(10)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Все статусы")
        for status in [Config.STATUS_NEW, Config.STATUS_ACCEPTED, Config.STATUS_IN_PROGRESS, 
                       Config.STATUS_WAITING_PARTS, Config.STATUS_COMPLETED, Config.STATUS_CLOSED]:
            self.status_filter.addItem(status)
        self.status_filter.currentTextChanged.connect(self._load_requests)
        filters_layout.addWidget(self.status_filter)

        self.priority_filter = QComboBox()
        self.priority_filter.addItem("Все приоритеты")
        for priority in [Config.PRIORITY_LOW, Config.PRIORITY_MEDIUM, Config.PRIORITY_HIGH, Config.PRIORITY_CRITICAL]:
            self.priority_filter.addItem(priority)
        self.priority_filter.currentTextChanged.connect(self._load_requests)
        filters_layout.addWidget(self.priority_filter)

        self.vehicle_filter = QComboBox()
        self.vehicle_filter.addItem("Все ТС")
        vehicles = self.db.execute("SELECT id, vehicle_number FROM vehicles ORDER BY vehicle_number")
        for v in vehicles:
            self.vehicle_filter.addItem(v['vehicle_number'], v['id'])
        self.vehicle_filter.currentIndexChanged.connect(self._load_requests)
        filters_layout.addWidget(self.vehicle_filter)

        filters_layout.addStretch()

        self.search_input = SearchBox("Поиск по номеру заявки...")
        self.search_input.textChanged.connect(self._load_requests)
        filters_layout.addWidget(self.search_input)

        layout.addLayout(filters_layout)

        # Таблица заявок
        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(9)
        self.requests_table.setHorizontalHeaderLabels([
            "Номер", "Автомобиль", "Тип ремонта", "Статус", "Приоритет", 
            "Создана", "Назначена", "Стоимость", "Действия"
        ])
        self.requests_table.horizontalHeader().setStretchLastSection(True)
        self.requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.requests_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.requests_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.requests_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.requests_table.setWordWrap(True)
        self.requests_table.setAlternatingRowColors(True)
        layout.addWidget(self.requests_table)

        # Загружаем данные
        self._load_requests()

        return page

    def _load_requests(self):
        query = """
            SELECT r.*, v.vehicle_number, v.brand, v.model, rt.name as repair_type_name,
                   creator.full_name as creator_name, assignee.full_name as assignee_name
            FROM repair_requests r
            JOIN vehicles v ON r.vehicle_id = v.id
            LEFT JOIN repair_types rt ON r.repair_type_id = rt.id
            LEFT JOIN users creator ON r.created_by = creator.id
            LEFT JOIN users assignee ON r.assigned_to = assignee.id
            WHERE 1=1
        """
        params = []

        # Фильтр по статусу
        status = self.status_filter.currentText()
        if status != "Все статусы":
            query += " AND r.status = ?"
            params.append(status)

        # Фильтр по приоритету
        priority = self.priority_filter.currentText()
        if priority != "Все приоритеты":
            query += " AND r.priority = ?"
            params.append(priority)

        # Фильтр по ТС
        vehicle_id = self.vehicle_filter.currentData()
        if vehicle_id:
            query += " AND r.vehicle_id = ?"
            params.append(vehicle_id)

        # Поиск
        search = self.search_input.text().strip()
        if search:
            query += " AND r.request_number LIKE ?"
            params.append(f"%{search}%")

        query += " ORDER BY r.created_at DESC"

        requests = self.db.execute(query, params)

        self.requests_table.setRowCount(len(requests))
        for i, req in enumerate(requests):
            self.requests_table.setItem(i, 0, QTableWidgetItem(req['request_number']))
            self.requests_table.setItem(i, 1, QTableWidgetItem(f"{req['brand']} {req['model']} ({req['vehicle_number']})"))
            self.requests_table.setItem(i, 2, QTableWidgetItem(req['repair_type_name'] or '-'))

            status_item = QTableWidgetItem(req['status'])
            status_color = Config.STATUS_COLORS.get(req['status'], Config.COLORS['text_secondary'])
            status_item.setForeground(QColor(status_color))
            self.requests_table.setItem(i, 3, status_item)

            priority_item = QTableWidgetItem(req['priority'])
            priority_color = Config.PRIORITY_COLORS.get(req['priority'], Config.COLORS['text_secondary'])
            priority_item.setForeground(QColor(priority_color))
            self.requests_table.setItem(i, 4, priority_item)

            self.requests_table.setItem(i, 5, QTableWidgetItem(str(req['created_at'])[:16]))
            self.requests_table.setItem(i, 6, QTableWidgetItem(req['assignee_name'] or '-'))
            self.requests_table.setItem(i, 7, QTableWidgetItem(format_currency(req['estimated_cost'] or 0)))

            # Кнопки действий
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setSpacing(5)
            actions_layout.setContentsMargins(5, 2, 5, 2)

            view_btn = QPushButton("👁")
            view_btn.setFixedSize(30, 30)
            view_btn.setToolTip("Просмотр")
            view_btn.clicked.connect(lambda checked, r=req: self._view_request(r))
            actions_layout.addWidget(view_btn)

            if self.role in ['Администратор', 'Главный механик']:
                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(30, 30)
                edit_btn.setToolTip("Редактировать")
                edit_btn.clicked.connect(lambda checked, r=req: self._edit_request(r))
                actions_layout.addWidget(edit_btn)

            actions_layout.addStretch()
            self.requests_table.setCellWidget(i, 8, actions_widget)

        self.requests_table.resizeColumnsToContents()

    def _show_create_request_dialog(self):
        dialog = CreateRequestDialog(self.db, self.current_user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_requests()
            self._update_dashboard()

    def _view_request(self, request):
        dialog = ViewRequestDialog(self.db, request, self.current_user, self)
        dialog.exec()

    def _edit_request(self, request):
        dialog = EditRequestDialog(self.db, request, self.current_user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_requests()
            self._update_dashboard()

    def _export_requests(self, format_type):
        if format_type == 'excel' and PANDAS_AVAILABLE:
            filename, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "requests.xlsx", "Excel files (*.xlsx)")
            if filename:
                requests = self.db.execute("""
                    SELECT r.request_number, v.vehicle_number, r.status, r.priority, 
                           r.created_at, r.estimated_cost, r.actual_cost
                    FROM repair_requests r
                    JOIN vehicles v ON r.vehicle_id = v.id
                """)
                df = pd.DataFrame([dict(r) for r in requests])
                df.to_excel(filename, index=False)
                QMessageBox.information(self, "Успех", f"Данные экспортированы в {filename}")
        elif format_type == 'pdf' and REPORTLAB_AVAILABLE:
            filename, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "requests.pdf", "PDF files (*.pdf)")
            if filename:
                self._export_to_pdf(filename)
                QMessageBox.information(self, "Успех", f"Данные экспортированы в {filename}")
        else:
            QMessageBox.warning(self, "Ошибка", "Необходимые библиотеки не установлены")

    def _export_to_pdf(self, filename):
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        title = Paragraph("Отчет по заявкам на ремонт", styles['Heading1'])
        elements.append(title)
        elements.append(Spacer(1, 20))

        requests = self.db.execute("""
            SELECT r.request_number, v.vehicle_number, r.status, r.priority, r.created_at
            FROM repair_requests r
            JOIN vehicles v ON r.vehicle_id = v.id
        """)

        data = [["Номер", "Автомобиль", "Статус", "Приоритет", "Дата создания"]]
        for req in requests:
            data.append([req['request_number'], req['vehicle_number'], req['status'], 
                        req['priority'], str(req['created_at'])[:10]])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        doc.build(elements)

    # =============================================================================
    # СТРАНИЦА МОИХ ЗАЯВОК (ДЛЯ МЕХАНИКОВ И ПОЛЬЗОВАТЕЛЕЙ)
    # =============================================================================

    def _create_my_requests_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Заголовок
        header_layout = QHBoxLayout()
        header = QLabel("📝 Мои заявки")
        header.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {Config.COLORS['text_primary']}; background: transparent;")
        header_layout.addWidget(header)
        header_layout.addStretch()

        # Кнопка создания заявки для пользователей
        if self.role == 'Пользователь':
            create_btn = QPushButton("+ Создать заявку")
            create_btn.clicked.connect(self._show_create_request_dialog)
            header_layout.addWidget(create_btn)

        layout.addLayout(header_layout)

        # Таблица
        self.my_requests_table = QTableWidget()
        self.my_requests_table.setColumnCount(7)
        self.my_requests_table.setHorizontalHeaderLabels([
            "Номер", "Автомобиль", "Описание", "Статус", "Приоритет", "Дата", "Действия"
        ])
        self.my_requests_table.horizontalHeader().setStretchLastSection(True)
        self.my_requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.my_requests_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.my_requests_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.my_requests_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.my_requests_table.setWordWrap(True)
        layout.addWidget(self.my_requests_table)

        # Загружаем данные
        self._load_my_requests()

        return page

    def _load_my_requests(self):
        if self.role == 'Механик':
            # Заявки, назначенные механику
            requests = self.db.execute("""
                SELECT r.*, v.vehicle_number, v.brand, v.model
                FROM repair_requests r
                JOIN vehicles v ON r.vehicle_id = v.id
                WHERE r.assigned_to = ?
                ORDER BY r.created_at DESC
            """, (self.current_user['id'],))
        else:
            # Заявки, созданные пользователем
            requests = self.db.execute("""
                SELECT r.*, v.vehicle_number, v.brand, v.model
                FROM repair_requests r
                JOIN vehicles v ON r.vehicle_id = v.id
                WHERE r.created_by = ?
                ORDER BY r.created_at DESC
            """, (self.current_user['id'],))

        self.my_requests_table.setRowCount(len(requests))
        for i, req in enumerate(requests):
            self.my_requests_table.setItem(i, 0, QTableWidgetItem(req['request_number']))
            self.my_requests_table.setItem(i, 1, QTableWidgetItem(f"{req['brand']} {req['model']}"))
            self.my_requests_table.setItem(i, 2, QTableWidgetItem(req['description'][:50] + "..." if len(req['description']) > 50 else req['description']))

            status_item = QTableWidgetItem(req['status'])
            status_color = Config.STATUS_COLORS.get(req['status'], Config.COLORS['text_secondary'])
            status_item.setForeground(QColor(status_color))
            self.my_requests_table.setItem(i, 3, status_item)

            priority_item = QTableWidgetItem(req['priority'])
            priority_color = Config.PRIORITY_COLORS.get(req['priority'], Config.COLORS['text_secondary'])
            priority_item.setForeground(QColor(priority_color))
            self.my_requests_table.setItem(i, 4, priority_item)

            self.my_requests_table.setItem(i, 5, QTableWidgetItem(str(req['created_at'])[:16]))

            # Кнопки действий
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setSpacing(5)
            actions_layout.setContentsMargins(5, 2, 5, 2)

            view_btn = QPushButton("👁")
            view_btn.setFixedSize(30, 30)
            view_btn.clicked.connect(lambda checked, r=req: self._view_request(r))
            actions_layout.addWidget(view_btn)

            if self.role == 'Механик' and req['status'] in ['Принята', 'В работе']:
                work_btn = QPushButton("🔧")
                work_btn.setFixedSize(30, 30)
                work_btn.setToolTip("Добавить работу")
                work_btn.clicked.connect(lambda checked, r=req: self._add_work_to_request(r))
                actions_layout.addWidget(work_btn)

            actions_layout.addStretch()
            self.my_requests_table.setCellWidget(i, 6, actions_widget)

        self.my_requests_table.resizeColumnsToContents()

    def _add_work_to_request(self, request):
        dialog = AddWorkDialog(self.db, request, self.current_user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_my_requests()

    # =============================================================================
    # СТРАНИЦА ТО
    # =============================================================================

    def _create_maintenance_page(self):
        page = QWidget()
        page.setStyleSheet(f"background-color: {Config.COLORS['bg_primary']};")
        layout = QVBoxLayout(page)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr, _ = self._create_page_header(
            "🔩", "Техническое обслуживание",
            "График и история ТО автопарка"
        )
        layout.addWidget(hdr)
        inner = QWidget()
        inner.setStyleSheet(f"background-color: {Config.COLORS['bg_primary']};")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setSpacing(16)
        inner_lay.setContentsMargins(24, 20, 24, 24)

        # Таблица ТО
        self.maintenance_table = QTableWidget()
        self.maintenance_table.setColumnCount(8)
        self.maintenance_table.setHorizontalHeaderLabels([
            "Номер", "Автомобиль", "Тип ТО", "Статус", "Запланировано", "Выполнено", "Стоимость", "Действия"
        ])
        self.maintenance_table.horizontalHeader().setStretchLastSection(True)
        self.maintenance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.maintenance_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.maintenance_table.setWordWrap(True)
        inner_lay.addWidget(self.maintenance_table)
        layout.addWidget(inner, 1)

        self._load_maintenance()

        return page

    def _load_maintenance(self):
        maintenance = self.db.execute("""
            SELECT m.*, v.vehicle_number, v.brand, v.model, mt.name as maintenance_type_name
            FROM maintenance_requests m
            JOIN vehicles v ON m.vehicle_id = v.id
            LEFT JOIN maintenance_types mt ON m.maintenance_type_id = mt.id
            ORDER BY m.created_at DESC
        """)

        self.maintenance_table.setRowCount(len(maintenance))
        for i, m in enumerate(maintenance):
            self.maintenance_table.setItem(i, 0, QTableWidgetItem(m['request_number']))
            self.maintenance_table.setItem(i, 1, QTableWidgetItem(f"{m['brand']} {m['model']}"))
            self.maintenance_table.setItem(i, 2, QTableWidgetItem(m['maintenance_type_name'] or '-'))
            self.maintenance_table.setItem(i, 3, QTableWidgetItem(m['status']))
            self.maintenance_table.setItem(i, 4, QTableWidgetItem(str(m['scheduled_date']) or '-'))
            self.maintenance_table.setItem(i, 5, QTableWidgetItem(str(m['completed_at'])[:16] if m['completed_at'] else '-'))
            self.maintenance_table.setItem(i, 6, QTableWidgetItem(format_currency(m['estimated_cost'] or 0)))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setSpacing(5)
            actions_layout.setContentsMargins(5, 2, 5, 2)

            view_btn = QPushButton("👁")
            view_btn.setFixedSize(30, 30)
            actions_layout.addWidget(view_btn)

            actions_layout.addStretch()
            self.maintenance_table.setCellWidget(i, 7, actions_widget)

        self.maintenance_table.resizeColumnsToContents()

    # =============================================================================
    # СТРАНИЦА АВТОПАРКА
    # =============================================================================

    def _create_vehicles_page(self):
        page = QWidget()
        page.setStyleSheet(f"background-color: {Config.COLORS['bg_primary']};")
        layout = QVBoxLayout(page)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        add_cb = self._show_add_vehicle_dialog if self.role == 'Администратор' else None
        hdr, _ = self._create_page_header(
            "🚗", "Автопарк",
            "Управление транспортными средствами",
            action_btn_text="+ Добавить ТС" if add_cb else "",
            action_btn_cb=add_cb
        )
        layout.addWidget(hdr)
        inner = QWidget()
        inner.setStyleSheet(f"background-color: {Config.COLORS['bg_primary']};")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setSpacing(12)
        inner_lay.setContentsMargins(24, 16, 24, 24)

        # Фильтры
        filters_layout = QHBoxLayout()

        self.vehicle_status_filter = QComboBox()
        self.vehicle_status_filter.addItems(["Все статусы", "В работе", "На ремонте", "На ТО", "Списан"])
        self.vehicle_status_filter.currentTextChanged.connect(self._load_vehicles)
        filters_layout.addWidget(self.vehicle_status_filter)

        self.vehicle_dept_filter = QComboBox()
        self.vehicle_dept_filter.addItem("Все подразделения")
        depts = self.db.execute("SELECT DISTINCT department FROM vehicles WHERE department IS NOT NULL")
        for d in depts:
            self.vehicle_dept_filter.addItem(d['department'])
        self.vehicle_dept_filter.currentTextChanged.connect(self._load_vehicles)
        filters_layout.addWidget(self.vehicle_dept_filter)

        filters_layout.addStretch()

        self.vehicle_search = SearchBox("Поиск по номеру, марке, модели...")
        self.vehicle_search.textChanged.connect(self._load_vehicles)
        filters_layout.addWidget(self.vehicle_search)

        inner_lay.addLayout(filters_layout)

        # Таблица
        self.vehicles_table = QTableWidget()
        self.vehicles_table.setColumnCount(10)
        self.vehicles_table.setHorizontalHeaderLabels([
            "Номер", "Марка", "Модель", "Год", "Категория", "Подразделение",
            "Пробег", "Статус", "След. ТО", "Действия"
        ])
        self.vehicles_table.horizontalHeader().setStretchLastSection(True)
        self.vehicles_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.vehicles_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.vehicles_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.vehicles_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.vehicles_table.setWordWrap(True)
        inner_lay.addWidget(self.vehicles_table)
        layout.addWidget(inner, 1)

        self._load_vehicles()

        return page

    def _load_vehicles(self):
        query = "SELECT * FROM vehicles WHERE 1=1"
        params = []

        status = self.vehicle_status_filter.currentText()
        if status != "Все статусы":
            query += " AND status = ?"
            params.append(status)

        dept = self.vehicle_dept_filter.currentText()
        if dept != "Все подразделения":
            query += " AND department = ?"
            params.append(dept)

        search = self.vehicle_search.text().strip()
        if search:
            query += " AND (vehicle_number LIKE ? OR brand LIKE ? OR model LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

        query += " ORDER BY vehicle_number"

        vehicles = self.db.execute(query, params)

        self.vehicles_table.setRowCount(len(vehicles))
        for i, v in enumerate(vehicles):
            self.vehicles_table.setItem(i, 0, QTableWidgetItem(v['vehicle_number']))
            self.vehicles_table.setItem(i, 1, QTableWidgetItem(v['brand']))
            self.vehicles_table.setItem(i, 2, QTableWidgetItem(v['model']))
            self.vehicles_table.setItem(i, 3, QTableWidgetItem(str(v['year']) if v['year'] else '-'))
            self.vehicles_table.setItem(i, 4, QTableWidgetItem(v['category'] or '-'))
            self.vehicles_table.setItem(i, 5, QTableWidgetItem(v['department'] or '-'))
            self.vehicles_table.setItem(i, 6, QTableWidgetItem(f"{v['mileage']:,} км".replace(',', ' ')))
            self.vehicles_table.setItem(i, 7, QTableWidgetItem(v['status']))
            self.vehicles_table.setItem(i, 8, QTableWidgetItem(str(v['next_maintenance']) or '-'))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setSpacing(5)
            actions_layout.setContentsMargins(5, 2, 5, 2)

            view_btn = QPushButton("👁")
            view_btn.setFixedSize(30, 30)
            actions_layout.addWidget(view_btn)

            if self.role == 'Администратор':
                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(30, 30)
                actions_layout.addWidget(edit_btn)

            actions_layout.addStretch()
            self.vehicles_table.setCellWidget(i, 9, actions_widget)

        self.vehicles_table.resizeColumnsToContents()

    def _show_add_vehicle_dialog(self):
        QMessageBox.information(self, "Информация", "Функция добавления ТС будет реализована в следующей версии")

    # =============================================================================
    # СТРАНИЦА АНАЛИТИКИ
    # =============================================================================

    def _create_analytics_page(self):
        page = QWidget()
        page.setStyleSheet(f"background-color: {Config.COLORS['bg_primary']};")
        layout = QVBoxLayout(page)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr, _ = self._create_page_header(
            "📈", "Аналитика автопарка",
            "KPI, статистика затрат и эффективность"
        )
        layout.addWidget(hdr)
        inner = QWidget()
        inner.setStyleSheet(f"background-color: {Config.COLORS['bg_primary']};")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setSpacing(16)
        inner_lay.setContentsMargins(24, 20, 24, 24)

        # KPI карточки
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)

        # Расчет KPI
        total_repairs = len(self.db.execute("SELECT id FROM repair_requests"))
        total_cost = self.db.execute_one("SELECT SUM(actual_cost) FROM repair_requests WHERE actual_cost IS NOT NULL")[0] or 0
        avg_repair_time = self.db.execute_one("""
            SELECT AVG(julianday(completed_at) - julianday(created_at)) 
            FROM repair_requests WHERE completed_at IS NOT NULL
        """)[0] or 0

        kpi1 = MetricCard("Всего ремонтов", str(total_repairs), "За все время", "🔧", Config.COLORS['accent_cyan'])
        kpi_layout.addWidget(kpi1)

        kpi2 = MetricCard("Общие затраты", format_currency(total_cost), "На ремонты", "💰", Config.COLORS['accent_pink'])
        kpi_layout.addWidget(kpi2)

        kpi3 = MetricCard("Ср. время ремонта", f"{avg_repair_time:.1f} дн", "От создания до закрытия", "⏱️", Config.COLORS['accent_green'])
        kpi_layout.addWidget(kpi3)

        kpi4 = MetricCard("Эффективность", "87%", "KPI ремонтной службы", "📈", Config.COLORS['accent_purple'])
        kpi_layout.addWidget(kpi4)

        inner_lay.addLayout(kpi_layout)

        # Графики
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)

        cost_chart = self._create_cost_chart()
        charts_layout.addWidget(cost_chart)

        problems_chart = self._create_problems_chart()
        charts_layout.addWidget(problems_chart)

        inner_lay.addLayout(charts_layout)

        # Кнопки экспорта
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        export_excel_btn = QPushButton("📊 Экспорт в Excel")
        export_excel_btn.setObjectName("secondary")
        export_excel_btn.clicked.connect(lambda: self._export_analytics('excel'))
        export_layout.addWidget(export_excel_btn)

        export_pdf_btn = QPushButton("📄 Экспорт в PDF")
        export_pdf_btn.setObjectName("secondary")
        export_pdf_btn.clicked.connect(lambda: self._export_analytics('pdf'))
        export_layout.addWidget(export_pdf_btn)

        inner_lay.addLayout(export_layout)
        inner_lay.addStretch()
        layout.addWidget(inner, 1)

        return page

    def _create_cost_chart(self):
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Затраты на ремонт по месяцам")
        title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {Config.COLORS['text_primary']};")
        layout.addWidget(title)

        if MATPLOTLIB_AVAILABLE:
            figure = Figure(figsize=(6, 4), facecolor=Config.COLORS['bg_card'])
            ax = figure.add_subplot(111)
            ax.set_facecolor(Config.COLORS['bg_card'])

            data = self.db.execute("""
                SELECT strftime('%Y-%m', created_at) as month, 
                       SUM(COALESCE(actual_cost, estimated_cost, 0)) as cost
                FROM repair_requests 
                GROUP BY month 
                ORDER BY month DESC 
                LIMIT 6
            """)

            if data:
                months = [d['month'] for d in reversed(data)]
                costs = [d['cost'] or 0 for d in reversed(data)]

                bars = ax.bar(months, costs, color=Config.COLORS['accent_cyan'])
                tc = Config.COLORS['text_secondary']
                bc = Config.COLORS['border']
                ax.set_xlabel('Месяц', color=tc)
                ax.set_ylabel('Сумма (руб)', color=tc)
                ax.tick_params(colors=tc)
                ax.spines['bottom'].set_color(bc)
                ax.spines['left'].set_color(bc)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

                # Добавляем значения на столбцы
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height):,}'.replace(',', ' '),
                           ha='center', va='bottom', color=tc, fontsize=9)

            canvas = FigureCanvas(figure)
            layout.addWidget(canvas)
        else:
            no_chart = QLabel("Графики недоступны")
            no_chart.setStyleSheet(f"color: {Config.COLORS['text_secondary']};")
            layout.addWidget(no_chart)

        return card

    def _create_problems_chart(self):
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Топ проблемных единиц")
        title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {Config.COLORS['text_primary']};")
        layout.addWidget(title)

        if MATPLOTLIB_AVAILABLE:
            figure = Figure(figsize=(6, 4), facecolor=Config.COLORS['bg_card'])
            ax = figure.add_subplot(111)
            ax.set_facecolor(Config.COLORS['bg_card'])

            data = self.db.execute("""
                SELECT v.vehicle_number, COUNT(*) as count
                FROM repair_requests r
                JOIN vehicles v ON r.vehicle_id = v.id
                GROUP BY r.vehicle_id
                ORDER BY count DESC
                LIMIT 5
            """)

            if data:
                vehicles = [d['vehicle_number'] for d in data]
                counts = [d['count'] for d in data]

                bars = ax.barh(vehicles, counts, color=Config.COLORS['accent_pink'])
                tc = Config.COLORS['text_secondary']
                bc = Config.COLORS['border']
                ax.set_xlabel('Количество заявок', color=tc)
                ax.tick_params(colors=tc)
                ax.spines['bottom'].set_color(bc)
                ax.spines['left'].set_color(bc)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

            canvas = FigureCanvas(figure)
            layout.addWidget(canvas)
        else:
            no_chart = QLabel("Графики недоступны")
            no_chart.setStyleSheet(f"color: {Config.COLORS['text_secondary']};")
            layout.addWidget(no_chart)

        return card

    def _export_analytics(self, format_type):
        QMessageBox.information(self, "Информация", f"Экспорт аналитики в {format_type.upper()} будет реализован в следующей версии")

    # =============================================================================
    # СТРАНИЦА ПОЛЬЗОВАТЕЛЕЙ
    # =============================================================================

    def _create_users_page(self):
        page = QWidget()
        page.setStyleSheet(f"background-color: {Config.COLORS['bg_primary']};")
        layout = QVBoxLayout(page)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr, _ = self._create_page_header(
            "👥", "Пользователи",
            "Управление аккаунтами и ролями",
            action_btn_text="+ Добавить пользователя",
            action_btn_cb=self._show_add_user_dialog
        )
        layout.addWidget(hdr)
        inner = QWidget()
        inner.setStyleSheet(f"background-color: {Config.COLORS['bg_primary']};")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setSpacing(12)
        inner_lay.setContentsMargins(24, 16, 24, 24)

        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(7)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Имя пользователя", "ФИО", "Email", "Роль", "Статус", "Действия"
        ])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.users_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.users_table.setWordWrap(True)
        inner_lay.addWidget(self.users_table)
        layout.addWidget(inner, 1)

        self._load_users()

        return page

    def _load_users(self):
        users = self.db.execute("""
            SELECT u.*, r.name as role_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            ORDER BY u.id
        """)

        self.users_table.setRowCount(len(users))
        for i, u in enumerate(users):
            self.users_table.setItem(i, 0, QTableWidgetItem(str(u['id'])))
            self.users_table.setItem(i, 1, QTableWidgetItem(u['username']))
            self.users_table.setItem(i, 2, QTableWidgetItem(u['full_name']))
            self.users_table.setItem(i, 3, QTableWidgetItem(u['email'] or '-'))
            self.users_table.setItem(i, 4, QTableWidgetItem(u['role_name']))

            status = "Активен" if u['is_active'] else "Заблокирован"
            status_item = QTableWidgetItem(status)
            status_color = Config.COLORS['success'] if u['is_active'] else Config.COLORS['error']
            status_item.setForeground(QColor(status_color))
            self.users_table.setItem(i, 5, status_item)

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setSpacing(5)
            actions_layout.setContentsMargins(5, 2, 5, 2)

            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda checked, user=u: self._edit_user(user))
            actions_layout.addWidget(edit_btn)

            actions_layout.addStretch()
            self.users_table.setCellWidget(i, 6, actions_widget)

        self.users_table.resizeColumnsToContents()

    def _show_add_user_dialog(self):
        dialog = AddUserDialog(self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_users()

    def _edit_user(self, user):
        dialog = EditUserDialog(self.db, user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_users()

    # =============================================================================
    # СТРАНИЦА СПРАВОЧНИКОВ
    # =============================================================================

    def _create_reference_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("📚 Справочники")
        header.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {Config.COLORS['text_primary']}; background: transparent;")
        layout.addWidget(header)
        layout.addSpacing(20)

        # Табы для разных справочников
        tabs = QTabWidget()
        tabs.tabBar().setUsesScrollButtons(True)
        tabs.tabBar().setElideMode(Qt.TextElideMode.ElideRight)
        tabs.tabBar().setExpanding(False)
        tabs.setDocumentMode(True)

        # Типы ремонта
        repair_types_tab = self._create_reference_tab("repair_types", ["Название", "Описание", "Часы", "Стоимость"])
        tabs.addTab(repair_types_tab, "Виды ремонта")

        # Типы ТО
        maintenance_types_tab = self._create_reference_tab("maintenance_types", ["Название", "Описание", "Пробег", "Месяцы", "Стоимость"])
        tabs.addTab(maintenance_types_tab, "Виды ТО")

        # Категории неисправностей
        defect_tab = self._create_reference_tab("defect_categories", ["Название", "Описание", "Приоритет"])
        tabs.addTab(defect_tab, "Категории неисправностей")

        # Поставщики
        suppliers_tab = self._create_reference_tab("suppliers", ["Название", "Контакт", "Телефон", "Email"])
        tabs.addTab(suppliers_tab, "Поставщики")

        layout.addWidget(tabs)

        return page

    def _create_reference_tab(self, table_name, columns):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)

        # Кнопка добавления
        add_btn = QPushButton("+ Добавить")
        add_btn.clicked.connect(lambda: self._add_reference_item(table_name))
        layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # Таблица
        table = QTableWidget()
        table.setColumnCount(len(columns) + 1)
        table.setHorizontalHeaderLabels(columns + ["Действия"])
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setWordWrap(True)
        layout.addWidget(table)

        # Сохраняем ссылку на таблицу
        setattr(self, f"{table_name}_table", table)

        # Загружаем данные
        self._load_reference_data(table_name)

        return tab

    def _load_reference_data(self, table_name):
        table = getattr(self, f"{table_name}_table", None)
        if not table:
            return

        data = self.db.execute(f"SELECT * FROM {table_name} WHERE is_active = 1")

        table.setRowCount(len(data))
        for i, row in enumerate(data):
            col_idx = 0
            for key in row.keys():
                if key not in ['id', 'is_active', 'created_at']:
                    table.setItem(i, col_idx, QTableWidgetItem(str(row[key]) if row[key] else '-'))
                    col_idx += 1

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setSpacing(5)
            actions_layout.setContentsMargins(5, 2, 5, 2)

            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(30, 30)
            actions_layout.addWidget(edit_btn)

            actions_layout.addStretch()
            table.setCellWidget(i, col_idx, actions_widget)

        table.resizeColumnsToContents()

    def _add_reference_item(self, table_name):
        QMessageBox.information(self, "Информация", f"Добавление в справочник '{table_name}' будет реализовано в следующей версии")

    # =============================================================================
    # СТРАНИЦА ЗАПЧАСТЕЙ
    # =============================================================================

    def _create_parts_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header_layout = QHBoxLayout()
        header = QLabel("🔩 Запчасти и материалы")
        header.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {Config.COLORS['text_primary']}; background: transparent;")
        header_layout.addWidget(header)
        header_layout.addStretch()

        add_btn = QPushButton("+ Добавить запчасть")
        add_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {Config.COLORS['accent_cyan']}; color: {Config.COLORS['bg_primary']}; 
                         border: none; border-radius: 8px; padding: 10px 20px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {Config.COLORS['accent_pink']}; }}
        """)
        add_btn.clicked.connect(self._show_add_part_dialog)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        # Фильтры
        filters_layout = QHBoxLayout()

        self.part_category_filter = QComboBox()
        self.part_category_filter.addItem("Все категории")
        categories = self.db.execute("SELECT DISTINCT category FROM parts WHERE category IS NOT NULL")
        for c in categories:
            self.part_category_filter.addItem(c['category'])
        self.part_category_filter.currentTextChanged.connect(self._load_parts)
        filters_layout.addWidget(self.part_category_filter)

        filters_layout.addStretch()

        self.part_search = SearchBox("Поиск по артикулу, названию...")
        self.part_search.textChanged.connect(self._load_parts)
        filters_layout.addWidget(self.part_search)

        layout.addLayout(filters_layout)

        # Таблица
        self.parts_table = QTableWidget()
        self.parts_table.setColumnCount(9)
        self.parts_table.setHorizontalHeaderLabels([
            "Артикул", "Название", "Категория", "Поставщик", "Цена", "Кол-во", "Мин. кол-во", "Место", "Действия"
        ])
        self.parts_table.horizontalHeader().setStretchLastSection(True)
        self.parts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.parts_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.parts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.parts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.parts_table.setWordWrap(True)
        layout.addWidget(self.parts_table)

        self._load_parts()

        return page

    def _load_parts(self):
        query = """
            SELECT p.*, s.name as supplier_name
            FROM parts p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.is_active = 1
        """
        params = []

        category = self.part_category_filter.currentText()
        if category != "Все категории":
            query += " AND p.category = ?"
            params.append(category)

        search = self.part_search.text().strip()
        if search:
            query += " AND (p.part_number LIKE ? OR p.name LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        query += " ORDER BY p.name"

        parts = self.db.execute(query, params)

        self.parts_table.setRowCount(len(parts))
        for i, p in enumerate(parts):
            self.parts_table.setItem(i, 0, QTableWidgetItem(p['part_number']))
            self.parts_table.setItem(i, 1, QTableWidgetItem(p['name']))
            self.parts_table.setItem(i, 2, QTableWidgetItem(p['category'] or '-'))
            self.parts_table.setItem(i, 3, QTableWidgetItem(p['supplier_name'] or '-'))
            self.parts_table.setItem(i, 4, QTableWidgetItem(format_currency(p['price'])))

            qty_item = QTableWidgetItem(str(p['quantity']))
            if p['quantity'] <= p['min_quantity']:
                qty_item.setForeground(QColor(Config.COLORS['error']))
            self.parts_table.setItem(i, 5, qty_item)

            self.parts_table.setItem(i, 6, QTableWidgetItem(str(p['min_quantity'])))
            self.parts_table.setItem(i, 7, QTableWidgetItem(p['location'] or '-'))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setSpacing(5)
            actions_layout.setContentsMargins(5, 2, 5, 2)

            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(30, 30)
            actions_layout.addWidget(edit_btn)

            actions_layout.addStretch()
            self.parts_table.setCellWidget(i, 8, actions_widget)

        self.parts_table.resizeColumnsToContents()

    def _show_add_part_dialog(self):
        QMessageBox.information(self, "Информация", "Функция добавления запчастей будет реализована в следующей версии")

    # =============================================================================
    # СТРАНИЦА ПРОФИЛЯ
    # =============================================================================

    def _create_profile_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("👤 Профиль пользователя")
        header.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {Config.COLORS['text_primary']}; background: transparent;")
        layout.addWidget(header)
        layout.addSpacing(20)

        # Карточка профиля
        profile_card = Card()
        profile_layout = QVBoxLayout(profile_card)
        profile_layout.setSpacing(20)
        profile_layout.setContentsMargins(30, 30, 30, 30)

        # Информация о пользователе
        info_layout = QGridLayout()
        info_layout.setSpacing(15)

        labels = [
            ("Имя пользователя:", self.current_user.get('username', '')),
            ("Полное имя:", self.current_user.get('full_name', '')),
            ("Email:", self.current_user.get('email', 'Не указан')),
            ("Телефон:", self.current_user.get('phone', 'Не указан')),
            ("Роль:", self.role),
            ("Подразделение:", self.current_user.get('department', 'Не указано')),
        ]

        for i, (label_text, value) in enumerate(labels):
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {Config.COLORS['text_secondary']}; font-size: 14px; font-weight: 600;")
            info_layout.addWidget(label, i, 0)
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet(f"color: {Config.COLORS['text_primary']}; font-size: 15px;")
            info_layout.addWidget(value_label, i, 1)

        profile_layout.addLayout(info_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        edit_btn = QPushButton("✏️ Редактировать профиль")
        edit_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {Config.COLORS['accent_cyan']}; color: {Config.COLORS['bg_primary']}; 
                         border: none; border-radius: 8px; padding: 12px 24px; font-weight: bold; font-size: 14px; }}
            QPushButton:hover {{ background-color: {Config.COLORS['accent_purple']}; }}
        """)
        edit_btn.clicked.connect(self._edit_profile)
        buttons_layout.addWidget(edit_btn)
        
        change_password_btn = QPushButton("🔒 Изменить пароль")
        change_password_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {Config.COLORS['bg_hover']}; color: {Config.COLORS['text_primary']}; 
                         border: 2px solid {Config.COLORS['border']}; border-radius: 8px; padding: 12px 24px; font-weight: bold; font-size: 14px; }}
            QPushButton:hover {{ background-color: {Config.COLORS['accent_purple']}; border-color: {Config.COLORS['accent_purple']}; }}
        """)
        change_password_btn.clicked.connect(self._change_password)
        buttons_layout.addWidget(change_password_btn)
        
        profile_layout.addLayout(buttons_layout)
        
        layout.addWidget(profile_card)
        layout.addStretch()

        return page

    def _edit_profile(self):
        QMessageBox.information(self, "Информация", "Функция редактирования профиля в разработке")

    def _change_password(self):
        QMessageBox.information(self, "Информация", "Функция смены пароля в разработке")

    # =============================================================================
    # СТРАНИЦА НАСТРОЕК
    # =============================================================================

    def _create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("⚙️ Настройки приложения")
        header.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {Config.COLORS['text_primary']}; background: transparent;")
        layout.addWidget(header)
        layout.addSpacing(20)

        # Карточка настроек внешнего вида
        appearance_card = Card()
        appearance_layout = QVBoxLayout(appearance_card)
        appearance_layout.setSpacing(20)
        appearance_layout.setContentsMargins(30, 30, 30, 30)

        appearance_title = QLabel("🎨 Внешний вид")
        appearance_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {Config.COLORS['text_primary']};")
        appearance_layout.addWidget(appearance_title)

        # Переключатель темы
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Тема приложения:")
        theme_label.setStyleSheet(f"color: {Config.COLORS['text_secondary']}; font-size: 15px;")
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Темная 🌙", "Светлая ☀️"])
        self.theme_combo.setCurrentIndex(0)  # Темная по умолчанию
        self.theme_combo.currentIndexChanged.connect(self._change_theme)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        appearance_layout.addLayout(theme_layout)
        layout.addWidget(appearance_card)

        # Карточка настроек уведомлений
        notifications_card = Card()
        notifications_layout = QVBoxLayout(notifications_card)
        notifications_layout.setSpacing(20)
        notifications_layout.setContentsMargins(30, 30, 30, 30)

        notifications_title = QLabel("🔔 Уведомления")
        notifications_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {Config.COLORS['text_primary']};")
        notifications_layout.addWidget(notifications_title)

        # Чекбоксы
        self.notifications_enabled_cb = QCheckBox("Включить уведомления")
        self.notifications_enabled_cb.setChecked(True)
        self.notifications_enabled_cb.setStyleSheet(f"color: {Config.COLORS['text_primary']}; font-size: 14px;")
        notifications_layout.addWidget(self.notifications_enabled_cb)

        self.email_notifications_cb = QCheckBox("Отправлять уведомления на email")
        self.email_notifications_cb.setChecked(True)
        self.email_notifications_cb.setStyleSheet(f"color: {Config.COLORS['text_primary']}; font-size: 14px;")
        notifications_layout.addWidget(self.email_notifications_cb)

        layout.addWidget(notifications_card)

        # Карточка настроек обновления
        refresh_card = Card()
        refresh_layout = QVBoxLayout(refresh_card)
        refresh_layout.setSpacing(20)
        refresh_layout.setContentsMargins(30, 30, 30, 30)

        refresh_title = QLabel("🔄 Обновление данных")
        refresh_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {Config.COLORS['text_primary']};")
        refresh_layout.addWidget(refresh_title)

        self.auto_refresh_cb = QCheckBox("Автоматическое обновление")
        self.auto_refresh_cb.setChecked(True)
        self.auto_refresh_cb.setStyleSheet(f"color: {Config.COLORS['text_primary']}; font-size: 14px;")
        refresh_layout.addWidget(self.auto_refresh_cb)

        layout.addWidget(refresh_card)

        # Кнопка сохранения
        save_btn = QPushButton("💾 Сохранить настройки")
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addStretch()

        # Загружаем сохраненные настройки
        self._load_settings()

        return page

    def _change_theme(self, index):
        """Изменение темы без перезапуска"""
        theme = 'dark' if index == 0 else 'light'
        ThemeManager.apply_theme(theme)
        self._save_theme_silent(theme)
        self._rebuild_ui()

    def _save_theme_silent(self, theme):
        """Сохранить тему в БД без UI-диалога"""
        try:
            existing = self.db.execute_one(
                "SELECT id FROM user_settings WHERE user_id = ?",
                (self.current_user['id'],)
            )
            if existing:
                self.db.cursor.execute(
                    "UPDATE user_settings SET theme = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (theme, self.current_user['id'])
                )
            else:
                self.db.cursor.execute(
                    "INSERT INTO user_settings (user_id, theme, notifications_enabled, email_notifications, auto_refresh) VALUES (?, ?, 1, 1, 1)",
                    (self.current_user['id'], theme)
                )
            self.db.connection.commit()
        except Exception as e:
            logger.error(f"Error saving theme: {e}")

    def _create_page_header(self, icon: str, title: str, subtitle: str = "",
                            action_btn_text: str = "", action_btn_cb=None,
                            secondary_btn_text: str = "", secondary_btn_cb=None) -> tuple:
        """Returns (header_widget, layout_for_extra_widgets).
        Builds a polished fixed-height header bar for any content page.
        """
        c = Config.COLORS
        accent = c.get('accent', '#6366F1')
        bar = QWidget()
        bar.setFixedHeight(72)
        bar.setStyleSheet(
            f"QWidget {{ background-color: {c['bg_secondary']};"
            f" border-bottom: 1px solid {c['border']}; }}"
        )
        row = QHBoxLayout(bar)
        row.setContentsMargins(28, 0, 28, 0)
        row.setSpacing(14)

        # Icon circle
        ic = QLabel(icon)
        ic.setFixedSize(40, 40)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ic.setStyleSheet(
            f"font-size: 18px; background-color: {accent}18;"
            f" border: 1px solid {accent}30; border-radius: 10px;"
        )
        row.addWidget(ic)

        # Title + subtitle
        col = QVBoxLayout()
        col.setSpacing(1)
        tl = QLabel(title)
        tl.setStyleSheet(
            f"font-size: 17px; font-weight: 700; color: {c['text_primary']}; background: transparent;"
        )
        col.addWidget(tl)
        if subtitle:
            sl = QLabel(subtitle)
            sl.setStyleSheet(
                f"font-size: 12px; color: {c['text_muted']}; background: transparent;"
            )
            col.addWidget(sl)
        row.addLayout(col)
        row.addStretch()

        # Optional action buttons
        if secondary_btn_text and secondary_btn_cb:
            s_btn = QPushButton(secondary_btn_text)
            s_btn.setObjectName("secondary")
            s_btn.setFixedHeight(34)
            s_btn.clicked.connect(secondary_btn_cb)
            row.addWidget(s_btn)

        if action_btn_text and action_btn_cb:
            a_btn = QPushButton(action_btn_text)
            a_btn.setFixedHeight(34)
            a_btn.clicked.connect(action_btn_cb)
            row.addWidget(a_btn)

        return bar, row

    def _rebuild_ui(self):
        """Перестроить UI с текущими цветами темы"""
        current_idx = self.content_stack.currentIndex() if hasattr(self, 'content_stack') else 0
        # Обновляем глобальный stylesheet
        new_ss = Styles.get_main_stylesheet()
        self.setStyleSheet(new_ss)
        QApplication.instance().setStyleSheet(new_ss)
        # Удаляем старый central widget
        old = self.centralWidget()
        if old:
            old.hide()
            old.setParent(None)
            old.deleteLater()
        # Перестраиваем
        self._setup_ui()
        # Восстанавливаем текущую страницу
        if hasattr(self, 'content_stack') and self.content_stack.count() > 0:
            self.content_stack.setCurrentIndex(
                min(current_idx, self.content_stack.count() - 1)
            )
        if hasattr(self, 'notif_count_label'):
            self._update_notifications_count()

    def _load_settings(self):
        """Загрузка настроек пользователя"""
        try:
            settings = self.db.execute_one(
                "SELECT * FROM user_settings WHERE user_id = ?",
                (self.current_user['id'],)
            )
            if settings:
                theme_index = 0 if settings['theme'] == 'dark' else 1
                # Блокируем сигнал, чтобы не запустить _change_theme
                self.theme_combo.blockSignals(True)
                self.theme_combo.setCurrentIndex(theme_index)
                self.theme_combo.blockSignals(False)
                self.notifications_enabled_cb.setChecked(bool(settings['notifications_enabled']))
                self.email_notifications_cb.setChecked(bool(settings['email_notifications']))
                self.auto_refresh_cb.setChecked(bool(settings['auto_refresh']))
        except Exception as e:
            logger.error(f"Error loading settings: {e}")

    def _save_settings(self):
        """Сохранение настроек пользователя"""
        try:
            theme = 'dark' if self.theme_combo.currentIndex() == 0 else 'light'
            
            # Проверяем существуют ли настройки
            existing = self.db.execute_one(
                "SELECT id FROM user_settings WHERE user_id = ?",
                (self.current_user['id'],)
            )
            
            if existing:
                # Обновляем
                self.db.cursor.execute("""
                    UPDATE user_settings 
                    SET theme = ?, notifications_enabled = ?, email_notifications = ?, 
                        auto_refresh = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (
                    theme,
                    1 if self.notifications_enabled_cb.isChecked() else 0,
                    1 if self.email_notifications_cb.isChecked() else 0,
                    1 if self.auto_refresh_cb.isChecked() else 0,
                    self.current_user['id']
                ))
            else:
                # Создаем
                self.db.cursor.execute("""
                    INSERT INTO user_settings (user_id, theme, notifications_enabled, email_notifications, auto_refresh)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    self.current_user['id'],
                    theme,
                    1 if self.notifications_enabled_cb.isChecked() else 0,
                    1 if self.email_notifications_cb.isChecked() else 0,
                    1 if self.auto_refresh_cb.isChecked() else 0
                ))
            
            self.db.connection.commit()
            QMessageBox.information(self, "Успех", "Настройки сохранены!")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения настроек: {e}")

# =============================================================================
# ДИАЛОГОВЫЕ ОКНА
# =============================================================================

class CreateRequestDialog(QDialog):
    def __init__(self, db, current_user, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_user = current_user
        self.setWindowTitle("Создание заявки на ремонт")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(Styles.get_main_stylesheet())
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        header = QLabel("Новая заявка на ремонт")
        header.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {Config.COLORS['text_primary']};")
        layout.addWidget(header)

        # Форма
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Автомобиль
        self.vehicle_combo = QComboBox()
        vehicles = self.db.execute("SELECT id, vehicle_number, brand, model FROM vehicles WHERE status = 'В работе' ORDER BY vehicle_number")
        for v in vehicles:
            self.vehicle_combo.addItem(f"{v['brand']} {v['model']} ({v['vehicle_number']})", v['id'])
        form_layout.addRow("Автомобиль:", self.vehicle_combo)

        # Тип ремонта
        self.repair_type_combo = QComboBox()
        repair_types = self.db.execute("SELECT id, name FROM repair_types WHERE is_active = 1 ORDER BY name")
        for rt in repair_types:
            self.repair_type_combo.addItem(rt['name'], rt['id'])
        form_layout.addRow("Тип ремонта:", self.repair_type_combo)

        # Категория неисправности
        self.defect_combo = QComboBox()
        defects = self.db.execute("SELECT id, name FROM defect_categories WHERE is_active = 1 ORDER BY name")
        for d in defects:
            self.defect_combo.addItem(d['name'], d['id'])
        form_layout.addRow("Категория неисправности:", self.defect_combo)

        # Приоритет
        self.priority_combo = QComboBox()
        for p in [Config.PRIORITY_LOW, Config.PRIORITY_MEDIUM, Config.PRIORITY_HIGH, Config.PRIORITY_CRITICAL]:
            self.priority_combo.addItem(p)
        form_layout.addRow("Приоритет:", self.priority_combo)

        # Описание
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Опишите проблему подробно...")
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Описание:", self.description_input)

        # Предполагаемая стоимость
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 1000000)
        self.cost_input.setSuffix(" ₽")
        self.cost_input.setGroupSeparatorShown(True)
        form_layout.addRow("Предполагаемая стоимость:", self.cost_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Создать заявку")
        save_btn.clicked.connect(self._save_request)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

    def _save_request(self):
        vehicle_id = self.vehicle_combo.currentData()
        repair_type_id = self.repair_type_combo.currentData()
        defect_id = self.defect_combo.currentData()
        priority = self.priority_combo.currentText()
        description = self.description_input.toPlainText().strip()
        cost = self.cost_input.value()

        if not description:
            QMessageBox.warning(self, "Ошибка", "Введите описание проблемы")
            return

        try:
            request_number = f"RM-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

            self.db.execute_insert("""
                INSERT INTO repair_requests (request_number, vehicle_id, created_by, repair_type_id, 
                                            defect_category_id, description, priority, estimated_cost, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (request_number, vehicle_id, self.current_user['id'], repair_type_id, 
                  defect_id, description, priority, cost, Config.STATUS_NEW))

            QMessageBox.information(self, "Успех", f"Заявка {request_number} создана успешно!")
            self.accept()
        except Exception as e:
            logger.error(f"Error creating request: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать заявку: {str(e)}")

class ViewRequestDialog(QDialog):
    def __init__(self, db, request, current_user, parent=None):
        super().__init__(parent)
        self.db = db
        self.request = request
        self.current_user = current_user
        self.setWindowTitle(f"Заявка {request['request_number']}")
        self.setMinimumSize(700, 600)
        self.setStyleSheet(Styles.get_main_stylesheet())
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        header_layout = QHBoxLayout()
        header = QLabel(f"Заявка {self.request['request_number']}")
        header.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {Config.COLORS['text_primary']};")
        header_layout.addWidget(header)

        status_badge = StatusBadge(self.request['status'])
        header_layout.addWidget(status_badge)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Информация о заявке
        info_card = Card()
        info_layout = QFormLayout(info_card)
        info_layout.setSpacing(10)

        info_layout.addRow("Автомобиль:", QLabel(f"{self.request.get('brand', '')} {self.request.get('model', '')} ({self.request.get('vehicle_number', '')})"))
        info_layout.addRow("Описание:", QLabel(self.request['description']))
        info_layout.addRow("Приоритет:", PriorityBadge(self.request['priority']))
        info_layout.addRow("Тип ремонта:", QLabel(self.request.get('repair_type_name') or '-'))
        info_layout.addRow("Создана:", QLabel(str(self.request['created_at'])[:16]))
        info_layout.addRow("Создатель:", QLabel(self.request.get('creator_name') or '-'))
        info_layout.addRow("Назначена:", QLabel(self.request.get('assignee_name') or 'Не назначена'))
        info_layout.addRow("Предполагаемая стоимость:", QLabel(format_currency(self.request.get('estimated_cost') or 0)))

        layout.addWidget(info_card)

        # Кнопки действий
        if self.current_user.get('role_name') in ['Администратор', 'Главный механик']:
            actions_layout = QHBoxLayout()

            if self.request['status'] == Config.STATUS_NEW:
                accept_btn = QPushButton("Принять в работу")
                accept_btn.clicked.connect(self._accept_request)
                actions_layout.addWidget(accept_btn)

                assign_btn = QPushButton("Назначить механика")
                assign_btn.clicked.connect(self._assign_mechanic)
                actions_layout.addWidget(assign_btn)

            elif self.request['status'] in [Config.STATUS_ACCEPTED, Config.STATUS_IN_PROGRESS]:
                complete_btn = QPushButton("Завершить")
                complete_btn.clicked.connect(self._complete_request)
                actions_layout.addWidget(complete_btn)

            actions_layout.addStretch()
            layout.addLayout(actions_layout)

        layout.addStretch()

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.setObjectName("secondary")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def _accept_request(self):
        try:
            self.db.execute_update("""
                UPDATE repair_requests SET status = ?, accepted_at = CURRENT_TIMESTAMP WHERE id = ?
            """, (Config.STATUS_ACCEPTED, self.request['id']))
            QMessageBox.information(self, "Успех", "Заявка принята в работу")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _assign_mechanic(self):
        mechanics = self.db.execute("SELECT u.id, u.full_name FROM users u JOIN roles r ON u.role_id = r.id WHERE r.name = 'Механик' AND u.is_active = 1")

        items = [m['full_name'] for m in mechanics]
        item, ok = QInputDialog.getItem(self, "Назначение механика", "Выберите механика:", items, 0, False)

        if ok and item:
            mechanic_id = next(m['id'] for m in mechanics if m['full_name'] == item)
            try:
                self.db.execute_update("""
                    UPDATE repair_requests SET assigned_to = ?, status = ? WHERE id = ?
                """, (mechanic_id, Config.STATUS_ACCEPTED, self.request['id']))
                QMessageBox.information(self, "Успех", f"Механик {item} назначен")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def _complete_request(self):
        reply = QMessageBox.question(self, "Подтверждение", "Завершить заявку?")
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.execute_update("""
                    UPDATE repair_requests SET status = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?
                """, (Config.STATUS_COMPLETED, self.request['id']))
                QMessageBox.information(self, "Успех", "Заявка завершена")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

class EditRequestDialog(QDialog):
    def __init__(self, db, request, current_user, parent=None):
        super().__init__(parent)
        self.db = db
        self.request = request
        self.current_user = current_user
        self.setWindowTitle(f"Редактирование заявки {request['request_number']}")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(Styles.get_main_stylesheet())
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        header = QLabel(f"Редактирование заявки {self.request['request_number']}")
        header.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {Config.COLORS['text_primary']};")
        layout.addWidget(header)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Статус
        self.status_combo = QComboBox()
        for s in [Config.STATUS_NEW, Config.STATUS_ACCEPTED, Config.STATUS_IN_PROGRESS, 
                  Config.STATUS_WAITING_PARTS, Config.STATUS_COMPLETED, Config.STATUS_CLOSED]:
            self.status_combo.addItem(s)
        self.status_combo.setCurrentText(self.request['status'])
        form_layout.addRow("Статус:", self.status_combo)

        # Приоритет
        self.priority_combo = QComboBox()
        for p in [Config.PRIORITY_LOW, Config.PRIORITY_MEDIUM, Config.PRIORITY_HIGH, Config.PRIORITY_CRITICAL]:
            self.priority_combo.addItem(p)
        self.priority_combo.setCurrentText(self.request['priority'])
        form_layout.addRow("Приоритет:", self.priority_combo)

        # Описание
        self.description_input = QTextEdit()
        self.description_input.setText(self.request['description'])
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Описание:", self.description_input)

        # Стоимость
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 1000000)
        self.cost_input.setSuffix(" ₽")
        self.cost_input.setValue(self.request.get('estimated_cost') or 0)
        form_layout.addRow("Предполагаемая стоимость:", self.cost_input)

        # Фактическая стоимость
        self.actual_cost_input = QDoubleSpinBox()
        self.actual_cost_input.setRange(0, 1000000)
        self.actual_cost_input.setSuffix(" ₽")
        self.actual_cost_input.setValue(self.request.get('actual_cost') or 0)
        form_layout.addRow("Фактическая стоимость:", self.actual_cost_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self._save_changes)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

    def _save_changes(self):
        try:
            self.db.execute_update("""
                UPDATE repair_requests 
                SET status = ?, priority = ?, description = ?, estimated_cost = ?, actual_cost = ?
                WHERE id = ?
            """, (self.status_combo.currentText(), self.priority_combo.currentText(),
                  self.description_input.toPlainText(), self.cost_input.value(),
                  self.actual_cost_input.value(), self.request['id']))

            QMessageBox.information(self, "Успех", "Изменения сохранены")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

class AddWorkDialog(QDialog):
    def __init__(self, db, request, current_user, parent=None):
        super().__init__(parent)
        self.db = db
        self.request = request
        self.current_user = current_user
        self.setWindowTitle("Добавление работы")
        self.setMinimumSize(500, 400)
        self.setStyleSheet(Styles.get_main_stylesheet())
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        header = QLabel("Добавление выполненной работы")
        header.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {Config.COLORS['text_primary']};")
        layout.addWidget(header)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Описание работы
        self.work_description = QTextEdit()
        self.work_description.setPlaceholderText("Опишите выполненную работу...")
        self.work_description.setMaximumHeight(100)
        form_layout.addRow("Описание работы:", self.work_description)

        # Затраченные часы
        self.hours_input = QDoubleSpinBox()
        self.hours_input.setRange(0.5, 100)
        self.hours_input.setSuffix(" ч")
        self.hours_input.setDecimals(1)
        form_layout.addRow("Затраченные часы:", self.hours_input)

        # Стоимость работы
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 100000)
        self.cost_input.setSuffix(" ₽")
        form_layout.addRow("Стоимость работы:", self.cost_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Добавить работу")
        save_btn.clicked.connect(self._save_work)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

    def _save_work(self):
        description = self.work_description.toPlainText().strip()
        if not description:
            QMessageBox.warning(self, "Ошибка", "Введите описание работы")
            return

        try:
            self.db.execute_insert("""
                INSERT INTO request_works (request_id, description, hours_spent, cost, performed_by, performed_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (self.request['id'], description, self.hours_input.value(), 
                  self.cost_input.value(), self.current_user['id']))

            QMessageBox.information(self, "Успех", "Работа добавлена")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

class AddUserDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Добавление пользователя")
        self.setMinimumSize(500, 450)
        self.setStyleSheet(Styles.get_main_stylesheet())
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        header = QLabel("Новый пользователь")
        header.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {Config.COLORS['text_primary']};")
        layout.addWidget(header)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин")
        form_layout.addRow("Логин:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Введите пароль")
        form_layout.addRow("Пароль:", self.password_input)

        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Введите ФИО")
        form_layout.addRow("ФИО:", self.fullname_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        form_layout.addRow("Email:", self.email_input)

        self.role_combo = QComboBox()
        roles = self.db.execute("SELECT id, name FROM roles ORDER BY name")
        for r in roles:
            self.role_combo.addItem(r['name'], r['id'])
        form_layout.addRow("Роль:", self.role_combo)

        self.department_input = QLineEdit()
        self.department_input.setPlaceholderText("Подразделение (опционально)")
        form_layout.addRow("Подразделение:", self.department_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Создать")
        save_btn.clicked.connect(self._save_user)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

    def _save_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        fullname = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        role_id = self.role_combo.currentData()
        department = self.department_input.text().strip()

        if not all([username, password, fullname]):
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля")
            return

        try:
            self.db.execute_insert("""
                INSERT INTO users (username, password_hash, full_name, email, role_id, department, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (username, hash_password(password), fullname, email, role_id, department))

            QMessageBox.information(self, "Успех", "Пользователь создан")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

class EditUserDialog(QDialog):
    def __init__(self, db, user, parent=None):
        super().__init__(parent)
        self.db = db
        self.user = user
        self.setWindowTitle(f"Редактирование пользователя {user['username']}")
        self.setMinimumSize(500, 400)
        self.setStyleSheet(Styles.get_main_stylesheet())
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        header = QLabel(f"Редактирование: {self.user['full_name']}")
        header.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {Config.COLORS['text_primary']};")
        layout.addWidget(header)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.fullname_input = QLineEdit()
        self.fullname_input.setText(self.user['full_name'])
        form_layout.addRow("ФИО:", self.fullname_input)

        self.email_input = QLineEdit()
        self.email_input.setText(self.user['email'] or '')
        form_layout.addRow("Email:", self.email_input)

        self.role_combo = QComboBox()
        roles = self.db.execute("SELECT id, name FROM roles ORDER BY name")
        for r in roles:
            self.role_combo.addItem(r['name'], r['id'])
        self.role_combo.setCurrentText(self.user['role_name'])
        form_layout.addRow("Роль:", self.role_combo)

        self.active_check = QCheckBox("Активен")
        self.active_check.setChecked(bool(self.user['is_active']))
        form_layout.addRow("Статус:", self.active_check)

        layout.addLayout(form_layout)
        layout.addStretch()

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self._save_changes)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

    def _save_changes(self):
        try:
            self.db.execute_update("""
                UPDATE users SET full_name = ?, email = ?, role_id = ?, is_active = ? WHERE id = ?
            """, (self.fullname_input.text(), self.email_input.text(),
                  self.role_combo.currentData(), int(self.active_check.isChecked()),
                  self.user['id']))

            QMessageBox.information(self, "Успех", "Изменения сохранены")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

# Добавляем импорт QInputDialog
from PyQt6.QtWidgets import QInputDialog

# =============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# =============================================================================

def main():
    """Главная функция запуска приложения"""
    try:
        # Создаем приложение
        app = QApplication(sys.argv)
        app.setApplicationName("Carvix SF Pro UI")
        app.setApplicationVersion(Config.APP_VERSION)

        # Fusion: на Windows иначе системная тема часто «съедает» фон/границы кнопок в QSS
        fusion_style = QStyleFactory.create("Fusion")
        if fusion_style is not None:
            app.setStyle(fusion_style)

        # Устанавливаем более современный и читаемый шрифт
        preferred_fonts = ["Segoe UI Variable Text", "Segoe UI", "Arial"]
        available_families = set(QFontDatabase.families())
        selected_family = next((name for name in preferred_fonts if name in available_families), "Segoe UI")
        font = QFont(selected_family, 10)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        app.setFont(font)

        # Создаем базу данных
        db = Database()

        # Создаем и показываем окно авторизации
        login_window = LoginWindow(db)

        # Переменная для хранения текущего пользователя
        current_user = [None]

        def on_login_success(user):
            current_user[0] = user

        login_window.login_successful.connect(on_login_success)
        login_window.show()

        # Запускаем цикл событий
        result = app.exec()

        # Если авторизация успешна, открываем главное окно
        if current_user[0]:
            # Загружаем сохранённую тему до создания UI
            try:
                saved = db.execute_one(
                    "SELECT theme FROM user_settings WHERE user_id = ?",
                    (current_user[0]['id'],)
                )
                if saved and saved.get('theme') == 'light':
                    ThemeManager.apply_theme('light')
            except Exception:
                pass
            main_window = MainWindow(db, current_user[0])
            main_window.show()
            result = app.exec()

        # Закрываем соединение с БД
        db.close()

        return result

    except Exception as e:
        logger.critical(f"Application error: {e}")
        logger.critical(traceback.format_exc())

        # Показываем сообщение об ошибке
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setWindowTitle("Критическая ошибка")
        error_msg.setText("Произошла критическая ошибка при запуске приложения")
        error_msg.setDetailedText(str(e) + "\n\n" + traceback.format_exc())
        error_msg.exec()

        return 1

if __name__ == "__main__":
    sys.exit(main())
