#!/usr/bin/env python3
"""
Скрипт запуска Carvix AutoManager с проверкой зависимостей
"""

import sys
import subprocess

def check_dependencies():
    """Проверка установленных зависимостей"""
    missing = []
    
    try:
        import PyQt6
        print("✅ PyQt6 установлен")
    except ImportError:
        missing.append("PyQt6")
        print("❌ PyQt6 не установлен")
    
    # Опциональные зависимости
    optional = {
        'matplotlib': 'matplotlib (для графиков)',
        'pandas': 'pandas (для Excel экспорта)',
        'reportlab': 'reportlab (для PDF экспорта)',
    }
    
    for module, name in optional.items():
        try:
            __import__(module)
            print(f"✅ {name} установлен")
        except ImportError:
            print(f"⚠️  {name} не установлен (опционально)")
    
    return missing

def install_dependencies(packages):
    """Установка недостающих пакетов"""
    print(f"\nУстановка недостающих пакетов: {', '.join(packages)}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        print("✅ Установка завершена")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки: {e}")
        return False

def main():
    print("=" * 60)
    print("Carvix AutoManager - Запуск приложения")
    print("=" * 60)
    print()
    
    # Проверка зависимостей
    print("Проверка зависимостей:")
    print("-" * 60)
    missing = check_dependencies()
    
    if missing:
        print()
        response = input("Установить недостающие зависимости? (y/n): ")
        if response.lower() == 'y':
            if not install_dependencies(missing):
                print("\nНе удалось установить зависимости.")
                print("Попробуйте установить вручную:")
                print(f"  pip install {' '.join(missing)}")
                sys.exit(1)
        else:
            print("\n❌ Необходимые зависимости не установлены.")
            sys.exit(1)
    
    print()
    print("=" * 60)
    print("Запуск приложения...")
    print("=" * 60)
    print()
    
    # Запуск основного приложения
    try:
        import carvix_app
        carvix_app.main()
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
