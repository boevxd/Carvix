#!/usr/bin/env python3
"""
Скрипт установки зависимостей для Carvix AutoManager
"""

import subprocess
import sys

def install_package(package):
    """Установка пакета через pip"""
    print(f"Установка {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} установлен успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки {package}: {e}")
        return False

def main():
    print("=" * 60)
    print("Установка зависимостей для Carvix AutoManager")
    print("=" * 60)
    print()
    
    # Обязательные зависимости
    required = [
        "PyQt6>=6.0.0",
    ]
    
    # Опциональные зависимости
    optional = [
        "matplotlib>=3.5.0",
        "pandas>=1.3.0",
        "reportlab>=3.6.0",
    ]
    
    print("Установка обязательных зависимостей:")
    print("-" * 60)
    for package in required:
        install_package(package)
    
    print()
    print("Установка опциональных зависимостей:")
    print("-" * 60)
    for package in optional:
        install_package(package)
    
    print()
    print("=" * 60)
    print("Установка завершена!")
    print("=" * 60)
    print()
    print("Для запуска приложения выполните:")
    print("  python carvix_app.py")
    print()

if __name__ == "__main__":
    main()
