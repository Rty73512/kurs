"""
Модуль для импорта и экспорта паролей
Поддерживает форматы: CSV, JSON
"""

import csv
import json
import os
from typing import Dict, List, Any
from datetime import datetime

class ImportExport:
    """Класс для импорта и экспорта паролей"""
    
    def __init__(self, passwords: Dict[str, Any]):
        """
        Инициализация
        
        Args:
            passwords: Словарь с паролями
        """
        self.passwords = passwords
    
    def export_to_csv(self, file_path: str) -> bool:
        """
        Экспорт паролей в CSV файл
        
        Args:
            file_path: Путь к файлу для сохранения
            
        Returns:
            bool: True если успешно
        """
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['service', 'username', 'password', 'url', 'notes']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for service, data in self.passwords.items():
                    writer.writerow({
                        'service': service,
                        'username': data.get('username', ''),
                        'password': data.get('password', ''),
                        'url': data.get('url', ''),
                        'notes': data.get('notes', '')
                    })
            return True
        except Exception as e:
            print(f"Ошибка экспорта в CSV: {e}")
            return False
    
    def import_from_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Импорт паролей из CSV файла
        
        Args:
            file_path: Путь к файлу для импорта
            
        Returns:
            Dict: Словарь с импортированными паролями
        """
        imported = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    service = row.get('service', '').strip()
                    if service:
                        imported[service] = {
                            'username': row.get('username', '').strip(),
                            'password': row.get('password', '').strip(),
                            'url': row.get('url', '').strip(),
                            'notes': row.get('notes', '').strip()
                        }
            return imported
        except Exception as e:
            print(f"Ошибка импорта из CSV: {e}")
            return {}
    
    def export_to_json(self, file_path: str) -> bool:
        """
        Экспорт паролей в JSON файл
        
        Args:
            file_path: Путь к файлу для сохранения
            
        Returns:
            bool: True если успешно
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(self.passwords, jsonfile, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка экспорта в JSON: {e}")
            return False
    
    def import_from_json(self, file_path: str) -> Dict[str, Any]:
        """
        Импорт паролей из JSON файла
        
        Args:
            file_path: Путь к файлу для импорта
            
        Returns:
            Dict: Словарь с импортированными паролями
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
                
                # Проверяем структуру данных
                imported = {}
                for service, info in data.items():
                    if isinstance(info, dict):
                        imported[service] = {
                            'username': info.get('username', ''),
                            'password': info.get('password', ''),
                            'url': info.get('url', ''),
                            'notes': info.get('notes', '')
                        }
                return imported
        except Exception as e:
            print(f"Ошибка импорта из JSON: {e}")
            return {}
    
    def import_from_chrome_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Импорт паролей из CSV файла, экспортированного из Google Chrome
        
        Args:
            file_path: Путь к файлу CSV из Chrome
            
        Returns:
            Dict: Словарь с импортированными паролями
        """
        imported = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # Chrome экспортирует с полями: name, url, username, password
                    service = row.get('name', row.get('url', '')).strip()
                    if not service:
                        service = row.get('url', 'Unknown').strip()
                    
                    if service:
                        imported[service] = {
                            'username': row.get('username', '').strip(),
                            'password': row.get('password', '').strip(),
                            'url': row.get('url', '').strip(),
                            'notes': f"Импортировано из Chrome {datetime.now().strftime('%Y-%m-%d')}"
                        }
            return imported
        except Exception as e:
            print(f"Ошибка импорта из Chrome CSV: {e}")
            return {}
    
    def import_from_firefox_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Импорт паролей из CSV файла, экспортированного из Firefox
        
        Args:
            file_path: Путь к файлу CSV из Firefox
            
        Returns:
            Dict: Словарь с импортированными паролями
        """
        imported = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # Firefox может использовать разные форматы
                    service = row.get('hostname', row.get('url', '')).strip()
                    if not service:
                        service = row.get('httpRealm', 'Unknown').strip()
                    
                    if service:
                        imported[service] = {
                            'username': row.get('username', row.get('user', '')).strip(),
                            'password': row.get('password', '').strip(),
                            'url': row.get('url', service).strip(),
                            'notes': f"Импортировано из Firefox {datetime.now().strftime('%Y-%m-%d')}"
                        }
            return imported
        except Exception as e:
            print(f"Ошибка импорта из Firefox CSV: {e}")
            return {}
    
    def import_from_edge_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Импорт паролей из CSV файла, экспортированного из Microsoft Edge
        
        Args:
            file_path: Путь к файлу CSV из Edge
            
        Returns:
            Dict: Словарь с импортированными паролями
        """
        # Edge использует такой же формат как Chrome
        return self.import_from_chrome_csv(file_path)
    
    def detect_format_and_import(self, file_path: str) -> Dict[str, Any]:
        """
        Автоматическое определение формата и импорт
        
        Args:
            file_path: Путь к файлу для импорта
            
        Returns:
            Dict: Словарь с импортированными паролями
        """
        if not os.path.exists(file_path):
            print(f"Файл не найден: {file_path}")
            return {}
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.csv':
                # Пробуем определить источник по заголовкам
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().lower()
                
                if 'name' in first_line and 'url' in first_line:
                    # Похоже на Chrome/Edge формат
                    return self.import_from_chrome_csv(file_path)
                elif 'hostname' in first_line or 'httprealm' in first_line:
                    # Похоже на Firefox формат
                    return self.import_from_firefox_csv(file_path)
                else:
                    # Стандартный CSV
                    return self.import_from_csv(file_path)
                    
            elif file_ext == '.json':
                return self.import_from_json(file_path)
            else:
                print(f"Неподдерживаемый формат файла: {file_ext}")
                return {}
                
        except Exception as e:
            print(f"Ошибка при импорте: {e}")
            return {}
    
    def merge_passwords(self, new_passwords: Dict[str, Any], 
                       overwrite: bool = False) -> tuple:
        """
        Объединение существующих паролей с импортированными
        
        Args:
            new_passwords: Новые пароли для добавления
            overwrite: Перезаписывать ли существующие
            
        Returns:
            tuple: (обновленный словарь, количество добавленных, количество обновленных)
        """
        added = 0
        updated = 0
        
        for service, data in new_passwords.items():
            if service in self.passwords:
                if overwrite:
                    self.passwords[service] = data
                    updated += 1
            else:
                self.passwords[service] = data
                added += 1
        
        return self.passwords, added, updated
    
    def export_to_readable_text(self, file_path: str) -> bool:
        """
        Экспорт паролей в читаемый текстовый файл
        
        Args:
            file_path: Путь к файлу для сохранения
            
        Returns:
            bool: True если успешно
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("ЭКСПОРТ ПАРОЛЕЙ\n")
                f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                for i, (service, data) in enumerate(self.passwords.items(), 1):
                    f.write(f"{i}. {service}\n")
                    f.write(f"   Логин: {data.get('username', '')}\n")
                    f.write(f"   Пароль: {data.get('password', '')}\n")
                    if data.get('url'):
                        f.write(f"   URL: {data.get('url')}\n")
                    if data.get('notes'):
                        f.write(f"   Заметки: {data.get('notes')}\n")
                    f.write("\n")
                
                f.write("=" * 60 + "\n")
                f.write(f"Всего записей: {len(self.passwords)}\n")
            return True
        except Exception as e:
            print(f"Ошибка экспорта в текст: {e}")
            return False


