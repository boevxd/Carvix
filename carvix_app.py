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
    QThread, QDate, QTime, QDateTime, QRect, QMargins
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
# ЛОГИРОВАНИЕ
# =============================================================================

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('carvix_debug.log', encoding='utf-8'),
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

class Database:
    def __init__(self, db_name=Config.DB_NAME):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.seed_initial_data()

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
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
            """CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT DEFAULT 'info',
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
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

    def seed_initial_data(self):
        self.cursor.execute("SELECT COUNT(*) FROM roles")
        if self.cursor.fetchone()[0] > 0:
            return

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

        # Администратор
        self.cursor.execute("SELECT id FROM roles WHERE name = 'Администратор'")
        admin_role_id = self.cursor.fetchone()[0]
        self.cursor.execute("""INSERT INTO users (username, password_hash, full_name, email, role_id, is_active)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ('admin', hash_password('admin'), 'Администратор Системы', 'admin@carvix.ru', admin_role_id, 1))

        # Тестовые пользователи
        test_users = [
            ('director', 'Директор', 'director@carvix.ru', 'Директор'),
            ('chief_mechanic', 'Главный Механик', 'chief@carvix.ru', 'Главный механик'),
            ('mechanic1', 'Иванов И.И.', 'mechanic1@carvix.ru', 'Механик'),
            ('dispatcher', 'Диспетчер', 'dispatcher@carvix.ru', 'Диспетчер'),
            ('analyst', 'Аналитик', 'analyst@carvix.ru', 'Аналитик'),
            ('user1', 'Петров П.П.', 'user1@carvix.ru', 'Пользователь'),
        ]
        for username, full_name, email, role_name in test_users:
            self.cursor.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
            role_id = self.cursor.fetchone()
            if role_id:
                self.cursor.execute("""INSERT INTO users (username, password_hash, full_name, email, role_id, is_active)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (username, hash_password('123456'), full_name, email, role_id[0], 1))

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

        # Тестовые заявки на ремонт
        self.cursor.execute("SELECT id FROM users WHERE username = 'user1'")
        user1_id = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT id FROM users WHERE username = 'mechanic1'")
        mechanic1_id = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT id FROM users WHERE username = 'chief_mechanic'")
        chief_id = self.cursor.fetchone()[0]
        
        # Получаем ID категорий и типов
        defect_cats = self.execute("SELECT id, name FROM defect_categories")
        repair_types_data = self.execute("SELECT id, name FROM repair_types")
        vehicles_data = self.execute("SELECT id FROM vehicles")
        
        import random
        from datetime import timedelta
        
        statuses = [Config.STATUS_NEW, Config.STATUS_ACCEPTED, Config.STATUS_IN_PROGRESS, 
                   Config.STATUS_WAITING_PARTS, Config.STATUS_COMPLETED, Config.STATUS_CLOSED]
        priorities = [Config.PRIORITY_LOW, Config.PRIORITY_MEDIUM, Config.PRIORITY_HIGH, Config.PRIORITY_CRITICAL]
        
        descriptions = [
            "Не заводится двигатель",
            "Посторонний шум при торможении",
            "Течь масла из двигателя",
            "Не работает кондиционер",
            "Вибрация при движении",
            "Проблема с коробкой передач",
            "Горит Check Engine",
            "Не работает стеклоподъемник",
            "Износ тормозных колодок",
            "Требуется замена масла",
            "Проблема с рулевым управлением",
            "Не работает стартер",
            "Перегрев двигателя",
            "Требуется диагностика подвески",
            "Скрип при повороте руля",
        ]
        
        # Создаем 30 тестовых заявок
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
            actual_cost = estimated_cost + random.randint(-5000, 10000) if status in [Config.STATUS_COMPLETED, Config.STATUS_CLOSED] else None
            
            assigned_to = mechanic1_id if status not in [Config.STATUS_NEW] else None
            accepted_at = created_date + timedelta(hours=random.randint(1, 24)) if status not in [Config.STATUS_NEW] else None
            started_at = accepted_at + timedelta(hours=random.randint(1, 12)) if status in [Config.STATUS_IN_PROGRESS, Config.STATUS_WAITING_PARTS, Config.STATUS_COMPLETED, Config.STATUS_CLOSED] else None
            completed_at = started_at + timedelta(days=random.randint(1, 7)) if status in [Config.STATUS_COMPLETED, Config.STATUS_CLOSED] else None
            
            self.cursor.execute("""
                INSERT INTO repair_requests (
                    request_number, vehicle_id, created_by, assigned_to,
                    defect_category_id, repair_type_id, description, priority, status,
                    estimated_cost, actual_cost, created_at, accepted_at, started_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request_number, vehicle_id, user1_id, assigned_to,
                defect_cat_id, repair_type_id, description, priority, status,
                estimated_cost, actual_cost, created_date, accepted_at, started_at, completed_at
            ))
        
        self.connection.commit()
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
        return f"""
QMainWindow {{ background-color: {bg0}; }}
QWidget {{ background-color: {bg0}; color: {tp}; font-family: 'Segoe UI', 'Inter', 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; }}
QFrame {{ background-color: {bg2}; border-radius: 12px; border: 1px solid {br}; }}
QFrame#card {{ background-color: {bg2}; border-radius: 16px; border: 1px solid {br}; padding: 24px; }}
QLabel {{ color: {tp}; background: transparent; border: none; }}
QLabel#title {{ font-size: 28px; font-weight: 700; color: {tp}; letter-spacing: -0.5px; }}
QLabel#subtitle {{ font-size: 14px; color: {ts}; font-weight: 400; }}
QLabel#accent {{ color: {accent_l}; font-weight: 600; }}
QLabel#sectionHeader {{ font-size: 11px; font-weight: 700; color: {tm}; letter-spacing: 1px; }}
QPushButton {{ background-color: {accent}; color: #FFFFFF; border: none; border-radius: 10px; padding: 9px 20px; min-height: 38px; font-weight: 600; font-size: 13px; letter-spacing: 0.1px; }}
QPushButton:hover {{ background-color: {accent_l}; }}
QPushButton:pressed {{ background-color: {accent_d}; }}
QPushButton:focus {{ outline: none; border: 2px solid {accent_l}; }}
QPushButton:disabled {{ background-color: {bgh}; color: {td}; border: none; }}
QPushButton#secondary {{ background-color: {bg3}; color: {tp}; border: 1px solid {br}; }}
QPushButton#secondary:hover {{ background-color: {bgh}; border-color: {accent}; color: {accent_l}; }}
QPushButton#danger {{ background-color: {c.get('error_bg','#EF444415')}; color: {err}; border: 1px solid {err}45; }}
QPushButton#danger:hover {{ background-color: {err}; color: #fff; border-color: {err}; }}
QPushButton#success {{ background-color: {c.get('success_bg','#10B98115')}; color: {ok}; border: 1px solid {ok}45; }}
QPushButton#success:hover {{ background-color: {ok}; color: #fff; border-color: {ok}; }}
QLineEdit {{ background-color: {bgi}; color: {tp}; border: 1px solid {br}; border-radius: 10px; padding: 9px 14px; font-size: 14px; min-height: 38px; selection-background-color: {accent}; }}
QLineEdit:focus {{ border-color: {accent}; background-color: {bg2}; }}
QLineEdit::placeholder {{ color: {tm}; }}
QComboBox {{ background-color: {bgi}; color: {tp}; border: 1px solid {br}; border-radius: 10px; padding: 9px 14px; min-width: 160px; min-height: 38px; font-size: 14px; }}
QComboBox:hover {{ border-color: {accent}; }}
QComboBox:focus {{ border-color: {accent}; }}
QComboBox::drop-down {{ border: none; width: 28px; }}
QComboBox QAbstractItemView {{ background-color: {bg3}; color: {tp}; border: 1px solid {br}; border-radius: 10px; selection-background-color: {accent}; selection-color: #fff; padding: 4px; outline: none; }}
QComboBox QAbstractItemView::item {{ padding: 8px 14px; border-radius: 6px; min-height: 30px; }}
QTextEdit {{ background-color: {bgi}; color: {tp}; border: 1px solid {br}; border-radius: 10px; padding: 12px; font-size: 14px; }}
QTextEdit:focus {{ border-color: {accent}; }}
QTableWidget {{ background-color: {bg2}; color: {tp}; border: 1px solid {br}; border-radius: 12px; gridline-color: {dv}; selection-background-color: {glow}; selection-color: {tp}; alternate-background-color: {bg1}; font-size: 13px; outline: none; }}
QTableWidget::item {{ padding: 12px 16px; border-bottom: 1px solid {dv}; min-height: 44px; }}
QTableWidget::item:selected {{ background-color: {glow}; color: {tp}; }}
QTableWidget::item:hover {{ background-color: {bgh}; }}
QHeaderView::section {{ background-color: {bg1}; color: {tm}; padding: 11px 16px; border: none; border-bottom: 1px solid {br}; font-weight: 700; font-size: 11px; letter-spacing: 0.8px; }}
QScrollBar:vertical {{ background-color: transparent; width: 6px; margin: 0; }}
QScrollBar::handle:vertical {{ background-color: {br}; border-radius: 3px; min-height: 24px; }}
QScrollBar::handle:vertical:hover {{ background-color: {tm}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{ background-color: transparent; height: 6px; margin: 0; }}
QScrollBar::handle:horizontal {{ background-color: {br}; border-radius: 3px; min-width: 24px; }}
QScrollBar::handle:horizontal:hover {{ background-color: {tm}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
QDateEdit, QTimeEdit {{ background-color: {bgi}; color: {tp}; border: 1px solid {br}; border-radius: 10px; padding: 9px 14px; font-size: 14px; min-height: 38px; }}
QDateEdit:focus, QTimeEdit:focus {{ border-color: {accent}; }}
QSpinBox, QDoubleSpinBox {{ background-color: {bgi}; color: {tp}; border: 1px solid {br}; border-radius: 10px; padding: 9px 14px; font-size: 14px; min-height: 38px; }}
QSpinBox:focus, QDoubleSpinBox:focus {{ border-color: {accent}; }}
QCheckBox {{ color: {tp}; spacing: 10px; font-size: 14px; }}
QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 5px; border: 1.5px solid {br}; background-color: {bgi}; }}
QCheckBox::indicator:checked {{ background-color: {accent}; border-color: {accent}; }}
QCheckBox::indicator:hover {{ border-color: {accent}; }}
QGroupBox {{ background-color: {bg2}; color: {tp}; border: 1px solid {br}; border-radius: 12px; margin-top: 12px; padding-top: 12px; font-weight: 600; font-size: 13px; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 14px; padding: 0 8px; color: {ts}; }}
QTabWidget::pane {{ background-color: {bg2}; border: 1px solid {br}; border-radius: 12px; top: -1px; }}
QTabBar::tab {{ background-color: transparent; color: {tm}; padding: 10px 20px; border: none; border-bottom: 2px solid transparent; margin-right: 2px; font-weight: 500; font-size: 13px; }}
QTabBar::tab:selected {{ color: {tp}; border-bottom: 2px solid {accent}; font-weight: 600; }}
QTabBar::tab:hover:!selected {{ color: {ts}; background-color: {bgh}; border-radius: 6px 6px 0 0; }}
QMenu {{ background-color: {bg3}; color: {tp}; border: 1px solid {br}; border-radius: 12px; padding: 6px; }}
QMenu::item {{ padding: 8px 20px; border-radius: 6px; font-size: 13px; }}
QMenu::item:selected {{ background-color: {accent}; color: #fff; }}
QMenu::separator {{ height: 1px; background-color: {dv}; margin: 4px 0; }}
QProgressBar {{ background-color: {bg3}; border: none; border-radius: 3px; height: 5px; font-size: 0px; }}
QProgressBar::chunk {{ background-color: {accent}; border-radius: 3px; }}
QStatusBar {{ background-color: {bg1}; color: {tm}; border-top: 1px solid {br}; font-size: 12px; }}
QToolBar {{ background-color: {bg1}; border: none; spacing: 8px; padding: 8px; }}
QDialog {{ background-color: {bg0}; }}
QMessageBox {{ background-color: {bg0}; }}
QMessageBox QPushButton {{ min-width: 90px; }}
QToolTip {{ background-color: {bg3}; color: {tp}; border: 1px solid {br}; border-radius: 6px; padding: 5px 10px; font-size: 12px; }}
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
        self._setup_shadow()
        if clickable:
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def _setup_shadow(self, hovered=False):
        shadow = QGraphicsDropShadowEffect(self)
        if hovered:
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(99, 102, 241, 50))  # Indigo glow
            shadow.setOffset(0, 4)
        else:
            shadow.setBlurRadius(8)
            shadow.setColor(QColor(0, 0, 0, 80))
            shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

    def enterEvent(self, event):
        if self.clickable:
            shadow = self.graphicsEffect()
            if shadow:
                shadow.setBlurRadius(20)
                shadow.setColor(QColor(99, 102, 241, 50))  # Indigo glow
                shadow.setOffset(0, 4)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.clickable:
            self._setup_shadow()
        super().leaveEvent(event)

class MetricCard(Card):
    def __init__(self, title, value, subtitle="", icon="", color=None, parent=None):
        super().__init__(parent, clickable=True)
        self.color = color or Config.COLORS.get('accent', '#6366F1')
        self._setup_ui(title, value, subtitle, icon)

    def _setup_ui(self, title, value, subtitle, icon):
        c = Config.COLORS
        accent = c.get('accent', '#6366F1')
        color = self.color
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(20, 18, 20, 18)
        # Icon pill
        if icon:
            icon_row = QHBoxLayout()
            icon_row.setContentsMargins(0, 0, 0, 0)
            icon_lbl = QLabel(icon)
            icon_lbl.setFixedSize(40, 40)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet(
                f"font-size: 20px; background-color: {color}20;"
                f" border: 1px solid {color}35; border-radius: 10px;"
                f" color: {color}; padding: 0;"
            )
            icon_row.addWidget(icon_lbl)
            icon_row.addStretch()
            layout.addLayout(icon_row)
            layout.addSpacing(12)
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {c['text_muted']}; font-size: 11px; font-weight: 700;"
            f" letter-spacing: 0.8px; background: transparent;"
        )
        layout.addWidget(title_label)
        layout.addSpacing(4)
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(
            f"color: {c['text_primary']}; font-size: 32px; font-weight: 700;"
            f" letter-spacing: -1px; background: transparent;"
        )
        layout.addWidget(value_label)
        self.value_label = value_label
        # Subtitle
        if subtitle:
            layout.addSpacing(4)
            sub_label = QLabel(subtitle)
            sub_label.setStyleSheet(
                f"color: {c['text_muted']}; font-size: 12px; background: transparent;"
            )
            layout.addWidget(sub_label)
        layout.addStretch()

    def set_value(self, value):
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

    def _setup_style(self):
        c = Config.COLORS
        accent = c.get('accent', '#6366F1')
        accent_l = c.get('accent_light', '#818CF8')
        self.setStyleSheet(
            f"QPushButton {{ background-color: transparent; color: {c['text_muted']};"
            f" border: none; border-radius: 8px; padding: 9px 14px;"
            f" text-align: left; font-size: 14px; font-weight: 500; min-height: 38px; }}"
            f" QPushButton:hover {{ background-color: {c['bg_hover']}; color: {c['text_secondary']}; }}"
            f" QPushButton:checked {{ background-color: {accent}18; color: {accent_l};"
            f" font-weight: 600; border-left: 2px solid {accent}; }}"
        )

    def mousePressEvent(self, event):
        self.clicked_signal.emit()
        super().mousePressEvent(event)

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
# ОКНО АВТОРИЗАЦИИ
# =============================================================================

class LoginWindow(QMainWindow):
    login_successful = pyqtSignal(dict)

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle(Config.APP_NAME)
        self.setMinimumSize(450, 550)
        self.setFixedSize(500, 700)
        
        # Устанавливаем иконку окна
        if os.path.exists('img.png'):
            self.setWindowIcon(QIcon('img.png'))
        
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
        central_widget = QWidget()
        central_widget.setObjectName("loginCentral")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Логотип
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.setSpacing(8)

        logo_label = QLabel()
        if os.path.exists('img.png'):
            pixmap = QPixmap('img.png')
            scaled_pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("🚗")
            logo_label.setStyleSheet("font-size: 80px; background: transparent;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo_label)

        subtitle_label = QLabel("Fleet Management System")
        subtitle_label.setStyleSheet(f"font-size: 14px; color: {Config.COLORS['text_secondary']}; background: transparent;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(subtitle_label)

        main_layout.addWidget(logo_container)
        main_layout.addSpacing(30)

        # Форма авторизации
        form_card = Card()
        form_card.setObjectName("loginCard")
        form_card.setFixedWidth(380)
        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(14)
        form_layout.setContentsMargins(35, 30, 35, 30)

        auth_title = QLabel("Вход в систему")
        auth_title.setObjectName("loginTitle")
        auth_title.setStyleSheet("background: transparent;")
        auth_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(auth_title)

        form_layout.addSpacing(16)

        # Логин
        login_label = QLabel("Логин")
        login_label.setObjectName("loginLabel")
        login_label.setStyleSheet("background: transparent;")
        form_layout.addWidget(login_label)

        self.login_input = QLineEdit()
        self.login_input.setObjectName("loginInput")
        self.login_input.setPlaceholderText("Введите логин")
        self.login_input.setText("admin")
        self.login_input.setMinimumHeight(50)
        form_layout.addWidget(self.login_input)

        # Пароль
        password_label = QLabel("Пароль")
        password_label.setObjectName("loginLabel")
        password_label.setStyleSheet("background: transparent;")
        form_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setObjectName("loginInput")
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setText("admin")
        self.password_input.setMinimumHeight(50)
        form_layout.addWidget(self.password_input)

        form_layout.addSpacing(16)

        # Кнопка входа
        self.login_button = QPushButton("Войти")
        self.login_button.setObjectName("loginPrimary")
        self.login_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.login_button.setFixedHeight(42)
        self.login_button.setDefault(True)
        self.login_button.setAutoDefault(True)
        self.login_button.setStyleSheet(self._get_login_primary_button_stylesheet())
        self.login_button.clicked.connect(self._handle_login)
        form_layout.addWidget(self.login_button)

        form_layout.addSpacing(5)

        # Тестовые данные
        test_info = QLabel()
        test_info.setTextFormat(Qt.TextFormat.RichText)
        test_info.setText(
            "<div style='text-align: center; line-height: 1.6;'>"
            "<span style='color: #7E879C; font-size: 11px;'>Тестовые логины (пароль: <b style='color: #00FFFF;'>123456</b>)</span><br>"
            "<span style='color: #A3ACC2; font-size: 11px;'><b style='color: #00FFFF;'>admin</b> • <b style='color: #00FFFF;'>director</b> • <b style='color: #00FFFF;'>mechanic1</b></span>"
            "</div>"
        )
        test_info.setWordWrap(True)
        test_info.setStyleSheet(f"background: transparent; padding: 8px 0;")
        test_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(test_info)

        main_layout.addWidget(form_card, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

    def _handle_login(self):
        username = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        try:
            user = self.db.execute_one("""
                SELECT u.*, r.name as role_name, r.permissions 
                FROM users u 
                JOIN roles r ON u.role_id = r.id 
                WHERE u.username = ? AND u.password_hash = ? AND u.is_active = 1
            """, (username, hash_password(password)))

            if user:
                user_dict = dict(user)
                self.db.execute_update(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                    (user_dict['id'],)
                )
                self.login_successful.emit(user_dict)
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
        except Exception as e:
            logger.error(f"Login error: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка авторизации: {str(e)}")

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
        if os.path.exists('img.png'):
            self.setWindowIcon(QIcon('img.png'))
        
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
        sidebar = QWidget()
        sidebar.setFixedWidth(248)
        sidebar.setStyleSheet(
            f"QWidget {{ background-color: {Config.COLORS['bg_secondary']};"
            f" border-right: 1px solid {Config.COLORS['border']}; }}"
        )
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(2)
        layout.setContentsMargins(12, 20, 12, 20)

        # Логотип
        logo_container = QWidget()
        logo_container.setStyleSheet("background: transparent;")
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(10)
        
        if os.path.exists('img.png'):
            logo_img = QLabel()
            pixmap = QPixmap('img.png')
            scaled_pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_img.setPixmap(scaled_pixmap)
            logo_layout.addWidget(logo_img)
        
        logo_text = QLabel("CARVIX")
        logo_text.setStyleSheet(
            f"font-size: 17px; font-weight: 700; color: {Config.COLORS['text_primary']};"
            f" background: transparent; letter-spacing: 2.5px;"
        )
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        
        layout.addWidget(logo_container)

        # Инфо о пользователе
        # User info block
        user_block = QFrame()
        user_block.setStyleSheet(
            f"QFrame {{ background-color: {Config.COLORS.get('bg_elevated','#1A1A2A')};"
            f" border-radius: 10px; border: 1px solid {Config.COLORS['border']}; }}"
        )
        user_block_layout = QVBoxLayout(user_block)
        user_block_layout.setContentsMargins(12, 10, 12, 10)
        user_block_layout.setSpacing(2)
        user_info = QLabel(self.current_user.get('full_name', ''))
        user_info.setStyleSheet(
            f"color: {Config.COLORS['text_primary']}; font-size: 13px;"
            f" font-weight: 600; background: transparent;"
        )
        user_block_layout.addWidget(user_info)
        role_label = QLabel(self.role)
        role_label.setStyleSheet(
            f"color: {Config.COLORS['text_muted']}; font-size: 11px; background: transparent;"
        )
        user_block_layout.addWidget(role_label)
        layout.addWidget(user_block)
        layout.addSpacing(16)
        
        # Notification pill
        notifications_card = QFrame()
        c_notif = Config.COLORS
        accent = c_notif.get('accent', '#6366F1')
        notifications_card.setStyleSheet(
            f"QFrame {{ background-color: {accent}15; border-radius: 8px;"
            f" border: 1px solid {accent}30; }}"
        )
        notif_layout = QHBoxLayout(notifications_card)
        notif_layout.setContentsMargins(10, 7, 10, 7)
        notif_layout.setSpacing(6)
        notif_icon = QLabel("🔔")
        notif_icon.setStyleSheet("font-size: 13px; background: transparent;")
        notif_layout.addWidget(notif_icon)
        self.notif_count_label = QLabel("0")
        self.notif_count_label.setStyleSheet(
            f"color: {Config.COLORS['text_primary']}; font-size: 13px;"
            f" font-weight: 700; background: transparent;"
        )
        notif_layout.addWidget(self.notif_count_label)
        notif_text = QLabel("уведомлений")
        notif_text.setStyleSheet(
            f"color: {Config.COLORS['text_muted']}; font-size: 11px; background: transparent;"
        )
        notif_layout.addWidget(notif_text)
        notif_layout.addStretch()
        layout.addWidget(notifications_card)
        layout.addSpacing(8)

        # Кнопки меню в зависимости от роли
        self.menu_buttons = {}
        
        # Обновляем счетчик уведомлений
        self._update_notifications_count()

        # Общие пункты для всех
        if self.role in ['Администратор', 'Директор', 'Аналитик', 'Главный механик', 'Диспетчер']:
            self._add_menu_button(layout, "dashboard", "📊", "Дашборд")

        # Заявки
        if self.role in ['Администратор', 'Главный механик', 'Диспетчер']:
            self._add_menu_button(layout, "requests", "🔧", "Заявки на ремонт")
        elif self.role == 'Механик':
            self._add_menu_button(layout, "my_requests", "🔧", "Мои заявки")
        elif self.role == 'Пользователь':
            self._add_menu_button(layout, "my_requests", "📋", "Мои заявки")

        # ТО
        if self.role in ['Администратор', 'Главный механик', 'Диспетчер']:
            self._add_menu_button(layout, "maintenance", "🔩", "Техническое обслуживание")

        # Автопарк
        if self.role in ['Администратор', 'Главный механик', 'Диспетчер', 'Аналитик']:
            self._add_menu_button(layout, "vehicles", "🚗", "Автопарк")

        # Аналитика
        if self.role in ['Администратор', 'Директор', 'Аналитик']:
            self._add_menu_button(layout, "analytics", "📈", "Аналитика")

        # Справочники (админ)
        if self.role == 'Администратор':
            self._add_menu_button(layout, "users", "👥", "Пользователи")
            self._add_menu_button(layout, "reference", "📚", "Справочники")

        # Запчасти
        if self.role in ['Администратор', 'Главный механик']:
            self._add_menu_button(layout, "parts", "⚙️", "Запчасти")

        layout.addStretch()

        # Профиль и настройки
        self._add_menu_button(layout, "profile", "👤", "Профиль")
        self._add_menu_button(layout, "settings", "⚙️", "Настройки")
        
        layout.addSpacing(10)

        # Выход
        logout_btn = QPushButton("🚪  Выход")
        logout_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {Config.COLORS['bg_card']}; color: {Config.COLORS['text_secondary']}; border: 2px solid {Config.COLORS['border']}; border-radius: 12px; padding: 14px; text-align: left; font-weight: 600; font-size: 15px; }}
            QPushButton:hover {{ background-color: {Config.COLORS['error']}22; color: {Config.COLORS['error']}; border-color: {Config.COLORS['error']}; }}
        """)
        logout_btn.clicked.connect(self._logout)
        layout.addWidget(logout_btn)

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
            self.content_stack.setCurrentIndex(page_map[page_id])

    def _create_pages(self):
        # Страница 0: Дашборд
        self.content_stack.addWidget(self._create_dashboard_page())
        # Страница 1: Заявки на ремонт
        self.content_stack.addWidget(self._create_requests_page())
        # Страница 2: Мои заявки
        self.content_stack.addWidget(self._create_my_requests_page())
        # Страница 3: ТО
        self.content_stack.addWidget(self._create_maintenance_page())
        # Страница 4: Автопарк
        self.content_stack.addWidget(self._create_vehicles_page())
        # Страница 5: Аналитика
        self.content_stack.addWidget(self._create_analytics_page())
        # Страница 6: Пользователи
        self.content_stack.addWidget(self._create_users_page())
        # Страница 7: Справочники
        self.content_stack.addWidget(self._create_reference_page())
        # Страница 8: Запчасти
        self.content_stack.addWidget(self._create_parts_page())
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
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Заголовок
        header = QLabel("📊 Обзор автопарка")
        header.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {Config.COLORS['text_primary']}; background: transparent;")
        layout.addWidget(header)
        layout.addSpacing(20)

        # Метрики
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)

        # Получаем данные для метрик
        total_vehicles = len(self.db.execute("SELECT id FROM vehicles"))
        active_repairs = len(self.db.execute("SELECT id FROM repair_requests WHERE status IN ('Новая', 'Принята', 'В работе')"))
        completed_month = len(self.db.execute("""
            SELECT id FROM repair_requests 
            WHERE status = 'Закрыта' 
            AND strftime('%Y-%m', closed_at) = strftime('%Y-%m', 'now')
        """))

        # Средний пробег
        avg_mileage = self.db.execute_one("SELECT AVG(mileage) FROM vehicles")[0] or 0

        # Создаем карточки метрик
        self.metric_cards = {}

        card1 = MetricCard("Автомобилей", str(total_vehicles), "Всего в парке", "🚗", Config.COLORS['accent_cyan'])
        metrics_layout.addWidget(card1)
        self.metric_cards['vehicles'] = card1

        card2 = MetricCard("В ремонте", str(active_repairs), "Активных заявок", "🔧", Config.COLORS['accent_pink'])
        metrics_layout.addWidget(card2)
        self.metric_cards['repairs'] = card2

        card3 = MetricCard("Выполнено", str(completed_month), "За текущий месяц", "✅", Config.COLORS['accent_green'])
        metrics_layout.addWidget(card3)
        self.metric_cards['completed'] = card3

        card4 = MetricCard("Средний пробег", f"{int(avg_mileage):,} км".replace(',', ' '), "По автопарку", "📊", Config.COLORS['accent_purple'])
        metrics_layout.addWidget(card4)
        self.metric_cards['mileage'] = card4

        layout.addLayout(metrics_layout)

        # Графики и таблица
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая часть - графики
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(16)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # График статусов
        status_chart = self._create_status_chart()
        left_layout.addWidget(status_chart)

        # График заявок по месяцам
        requests_chart = self._create_requests_chart()
        left_layout.addWidget(requests_chart)

        content_splitter.addWidget(left_widget)

        # Правая часть - таблица последних заявок
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(16)
        right_layout.setContentsMargins(0, 0, 0, 0)

        recent_label = QLabel("📋 Последние заявки")
        recent_label.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {Config.COLORS['text_primary']}; background: transparent;")
        right_layout.addWidget(recent_label)

        self.recent_requests_table = QTableWidget()
        self.recent_requests_table.setColumnCount(5)
        self.recent_requests_table.setHorizontalHeaderLabels(["Номер", "Авто", "Статус", "Дата", "Приоритет"])
        self.recent_requests_table.horizontalHeader().setStretchLastSection(True)
        self.recent_requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.recent_requests_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.recent_requests_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.recent_requests_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.recent_requests_table.setWordWrap(True)
        right_layout.addWidget(self.recent_requests_table)

        content_splitter.addWidget(right_widget)
        content_splitter.setSizes([350, 650])

        layout.addWidget(content_splitter, 1)

        # Заполняем таблицу
        self._load_recent_requests()

        # Таймер обновления
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_dashboard)
        self.update_timer.start(30000)  # Обновление каждые 30 секунд

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
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("⚙️ Техническое обслуживание")
        header.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {Config.COLORS['text_primary']}; background: transparent;")
        layout.addWidget(header)
        layout.addSpacing(20)

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
        layout.addWidget(self.maintenance_table)

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
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header_layout = QHBoxLayout()
        header = QLabel("🚗 Автопарк")
        header.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {Config.COLORS['text_primary']}; background: transparent;")
        header_layout.addWidget(header)
        header_layout.addStretch()

        if self.role == 'Администратор':
            add_btn = QPushButton("+ Добавить ТС")
            add_btn.clicked.connect(self._show_add_vehicle_dialog)
            header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

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

        layout.addLayout(filters_layout)

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
        layout.addWidget(self.vehicles_table)

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
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("📈 Аналитика автопарка")
        header.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {Config.COLORS['text_primary']}; background: transparent;")
        layout.addWidget(header)
        layout.addSpacing(20)

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

        layout.addLayout(kpi_layout)

        # Графики
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)

        # График затрат по месяцам
        cost_chart = self._create_cost_chart()
        charts_layout.addWidget(cost_chart)

        # График проблемных единиц
        problems_chart = self._create_problems_chart()
        charts_layout.addWidget(problems_chart)

        layout.addLayout(charts_layout)

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

        layout.addLayout(export_layout)

        layout.addStretch()

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
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header_layout = QHBoxLayout()
        header = QLabel("👥 Пользователи")
        header.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {Config.COLORS['text_primary']}; background: transparent;")
        header_layout.addWidget(header)
        header_layout.addStretch()

        add_btn = QPushButton("+ Добавить пользователя")
        add_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {Config.COLORS['accent_cyan']}; color: {Config.COLORS['bg_primary']}; 
                         border: none; border-radius: 8px; padding: 10px 20px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {Config.COLORS['accent_pink']}; }}
        """)
        add_btn.clicked.connect(self._show_add_user_dialog)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

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
        layout.addWidget(self.users_table)

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
        """Изменение темы приложения"""
        theme = 'dark' if index == 0 else 'light'
        ThemeManager.apply_theme(theme)
        self._save_settings()
        theme_name = 'тёмную' if theme == 'dark' else 'светлую'
        reply = QMessageBox.question(
            self, "Применить тему",
            f"Тема изменена на {theme_name}.\n\nДля полного применения необходим перезапуск. Перезапустить сейчас?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.instance().quit()
            subprocess.Popen([sys.executable] + sys.argv)

    def _load_settings(self):
        """Загрузка настроек пользователя"""
        try:
            settings = self.db.execute_one(
                "SELECT * FROM user_settings WHERE user_id = ?",
                (self.current_user['id'],)
            )
            if settings:
                # Устанавливаем значения
                theme_index = 0 if settings['theme'] == 'dark' else 1
                self.theme_combo.setCurrentIndex(theme_index)
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
