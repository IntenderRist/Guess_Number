import os
import sqlite3
from pathlib import Path

def reset_database(db_name):
    """Сбрасывает указанную базу данных"""
    db_path = Path(db_name)
    
    if db_path.exists():
        try:
            # Попытка удалить файл базы данных
            os.remove(db_name)
            print(f"✅ База данных {db_name} успешно удалена")
        except Exception as e:
            print(f"❌ Ошибка при удалении {db_name}: {str(e)}")
    else:
        print(f"ℹ️ Файл {db_name} не найден")

def reset_records_only():
    """Сбрасывает только таблицы рекордов, сохраняя данные пользователей"""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Удаляем записи из таблиц рекордов
        cursor.execute('DELETE FROM records')
        cursor.execute('DELETE FROM bulls_cows_records')
        
        # Сбрасываем автоинкремент
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="records" OR name="bulls_cows_records"')
        
        conn.commit()
        conn.close()
        print("✅ Таблицы рекордов успешно очищены")
    except Exception as e:
        print(f"❌ Ошибка при очистке таблиц рекордов: {str(e)}")

if __name__ == "__main__":
    print("Выберите действие:")
    print("1. Полный сброс всех баз данных")
    print("2. Сброс только таблиц рекордов")
    
    choice = input("Введите номер действия (1 или 2): ").strip()
    
    if choice == "1":
        print("🚨 ВНИМАНИЕ: Это действие полностью удалит все базы данных! 🚨")
        confirm = input("Вы уверены? (y/n): ").strip().lower()
        if confirm == 'y':
            reset_database('users.db')
            print("🔥 Сброс баз данных завершен")
        else:
            print("❎ Отмена операции")
    elif choice == "2":
        print("🚨 ВНИМАНИЕ: Это действие удалит все рекорды, но сохранит данные пользователей! 🚨")
        confirm = input("Вы уверены? (y/n): ").strip().lower()
        if confirm == 'y':
            reset_records_only()
            print("🔥 Сброс рекордов завершен")
        else:
            print("❎ Отмена операции")
    else:
        print("❌ Неверный выбор")