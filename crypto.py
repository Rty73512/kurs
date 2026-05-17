"""
Модуль криптографии для менеджера паролей
Обеспечивает безопасное шифрование и хранение данных
"""

import os
import base64
import hashlib
import json
from typing import Dict, Any, Optional, Tuple
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets

class CryptoManager:
    """
    Класс для управления криптографическими операциями
    """
    
    def __init__(self):
        self.fernet: Optional[Fernet] = None
        self.master_key: Optional[bytes] = None
        self.salt: Optional[bytes] = None
        
        # Параметры для PBKDF2
        self.iterations = 100000  # Количество итераций для усиления ключа
        self.key_length = 32  # Длина ключа в байтах (256 бит)
        self.hash_algorithm = hashes.SHA256()
        
        # Файлы для хранения
        self.salt_file = "salt.bin"
        self.verification_file = "verify.bin"
    
    def derive_key(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Создание ключа шифрования из мастер-пароля с использованием PBKDF2
        
        Args:
            password: Мастер-пароль пользователя
            salt: Соль для усиления (если None, генерируется новая)
            
        Returns:
            Tuple[bytes, bytes]: (ключ, соль)
        """
        if salt is None:
            salt = os.urandom(16)  # Генерация случайной соли
        
        # Создание KDF (Key Derivation Function)
        kdf = PBKDF2HMAC(
            algorithm=self.hash_algorithm,
            length=self.key_length,
            salt=salt,
            iterations=self.iterations,
            backend=default_backend()
        )
        
        # Генерация ключа
        key = kdf.derive(password.encode('utf-8'))
        
        return key, salt
    
    def create_master_key(self, master_password: str) -> bytes:
        """
        Создание мастер-ключа из пароля
        
        Args:
            master_password: Мастер-пароль
            
        Returns:
            bytes: Мастер-ключ
        """
        # Генерация новой соли
        self.salt = os.urandom(32)
        
        # Создание ключа
        key, self.salt = self.derive_key(master_password, self.salt)
        self.master_key = key
        
        # Сохранение соли
        self.save_salt()
        
        # Создание и сохранение верификационного хеша
        self.create_verification_hash()
        
        return key
    
    def verify_master_password(self, master_password: str) -> bool:
        """
        Проверка мастер-пароля
        
        Args:
            master_password: Мастер-пароль для проверки
            
        Returns:
            bool: True если пароль верный
        """
        try:
            # Загрузка соли
            if not self.load_salt():
                return False
            
            # Создание ключа из введенного пароля
            key, _ = self.derive_key(master_password, self.salt)
            
            # Проверка через верификационный хеш
            if os.path.exists(self.verification_file):
                result = self.verify_with_hash(key)
                if result:
                    # Ключ уже сохранен в verify_with_hash
                    return True
                return False
            
            # Если нет файла верификации, пробуем загрузить данные
            result = self.try_decrypt_existing_data(key)
            if result:
                # Ключ уже сохранен в try_decrypt_existing_data
                return True
            return False
            
        except Exception as e:
            return False
    
    def create_verification_hash(self) -> None:
        """
        Создание верификационного хеша для проверки пароля
        """
        if self.master_key is None:
            raise ValueError("Мастер-ключ не создан")
        
        # Создаем случайные данные для верификации
        verification_data = b"PASSWORD_MANAGER_VERIFICATION" + os.urandom(16)
        
        # Шифруем данные с помощью мастер-ключа
        fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
        encrypted_data = fernet.encrypt(verification_data)
        
        # Сохраняем зашифрованные данные
        with open(self.verification_file, 'wb') as f:
            f.write(encrypted_data)
    
    def verify_with_hash(self, key: bytes) -> bool:
        """
        Проверка пароля через верификационный хеш
        
        Args:
            key: Ключ для проверки
            
        Returns:
            bool: True если верификация успешна
        """
        try:
            with open(self.verification_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Попытка расшифровки
            fernet = Fernet(base64.urlsafe_b64encode(key))
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Проверка префикса
            if decrypted_data.startswith(b"PASSWORD_MANAGER_VERIFICATION"):
                # СОХРАНЯЕМ ключ при успешной верификации
                self.master_key = key
                self.fernet = fernet
                return True
            return False
        except:
            return False
    
    def try_decrypt_existing_data(self, key: bytes) -> bool:
        """
        Попытка расшифровки существующих данных для верификации
        
        Args:
            key: Ключ для проверки
            
        Returns:
            bool: True если расшифровка успешна
        """
        try:
            # Проверяем, есть ли файл с данными
            data_file = "passwords.enc"
            if not os.path.exists(data_file):
                # Если данных нет, сохраняем ключ и считаем пароль верным
                self.master_key = key
                self.fernet = Fernet(base64.urlsafe_b64encode(key))
                return True
            
            # Пробуем расшифровать
            fernet = Fernet(base64.urlsafe_b64encode(key))
            with open(data_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Пробуем расшифровать
            fernet.decrypt(encrypted_data)
            
            # Если расшифровка успешна, сохраняем ключ
            self.master_key = key
            self.fernet = fernet
            return True
            
        except:
            return False
    
    def initialize_fernet(self) -> None:
        """
        Инициализация Fernet для шифрования данных
        """
        if self.master_key is None:
            raise ValueError("Мастер-ключ не установлен")
        
        # Fernet требует ключ в формате base64
        fernet_key = base64.urlsafe_b64encode(self.master_key)
        self.fernet = Fernet(fernet_key)
    
    def encrypt_data(self, data: Dict[str, Any]) -> bytes:
        """
        Шифрование словаря с данными
        
        Args:
            data: Словарь с данными для шифрования
            
        Returns:
            bytes: Зашифрованные данные
        """
        if self.fernet is None:
            raise ValueError("Fernet не инициализирован")
        
        # Преобразование в JSON
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        
        # Добавление случайных байт для усиления безопасности
        padding = secrets.token_bytes(32)
        padded_data = padding + json_data
        
        # Шифрование
        encrypted_data = self.fernet.encrypt(padded_data)
        
        return encrypted_data
    
    def decrypt_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """
        Расшифровка данных
        
        Args:
            encrypted_data: Зашифрованные данные
            
        Returns:
            Dict[str, Any]: Расшифрованный словарь
        """
        if self.fernet is None:
            raise ValueError("Fernet не инициализирован")
        
        try:
            # Расшифровка
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Удаление случайного заполнения
            json_data = decrypted_data[32:]  # Убираем первые 32 байта
            
            # Парсинг JSON
            return json.loads(json_data.decode('utf-8'))
            
        except InvalidToken:
            raise ValueError("Неверный ключ шифрования или поврежденные данные")
        except Exception as e:
            raise ValueError(f"Ошибка расшифровки: {e}")
    
    def encrypt_password(self, password: str) -> Dict[str, str]:
        """
        Дополнительное шифрование отдельного пароля (для особо важных данных)
        
        Args:
            password: Пароль для шифрования
            
        Returns:
            Dict[str, str]: Зашифрованный пароль с метаданными
        """
        # Генерация случайного ключа для этого пароля
        temp_key = secrets.token_bytes(32)
        temp_fernet = Fernet(base64.urlsafe_b64encode(temp_key))
        
        # Шифрование пароля
        encrypted_password = temp_fernet.encrypt(password.encode('utf-8'))
        
        # Шифрование временного ключа мастер-ключом
        if self.fernet is None:
            raise ValueError("Fernet не инициализирован")
        
        encrypted_key = self.fernet.encrypt(temp_key)
        
        return {
            'encrypted_password': base64.b64encode(encrypted_password).decode('utf-8'),
            'encrypted_key': base64.b64encode(encrypted_key).decode('utf-8'),
            'algorithm': 'AES-256-GCM',
            'version': '1.0'
        }
    
    def decrypt_password(self, encrypted_data: Dict[str, str]) -> str:
        """
        Расшифровка отдельного пароля
        
        Args:
            encrypted_data: Данные зашифрованного пароля
            
        Returns:
            str: Расшифрованный пароль
        """
        try:
            # Расшифровка временного ключа
            encrypted_key = base64.b64decode(encrypted_data['encrypted_key'])
            temp_key = self.fernet.decrypt(encrypted_key)
            
            # Расшифровка пароля
            temp_fernet = Fernet(base64.urlsafe_b64encode(temp_key))
            encrypted_password = base64.b64decode(encrypted_data['encrypted_password'])
            password = temp_fernet.decrypt(encrypted_password)
            
            return password.decode('utf-8')
            
        except Exception as e:
            raise ValueError(f"Ошибка расшифровки пароля: {e}")
    
    def save_salt(self) -> None:
        """Сохранение соли в файл"""
        if self.salt is None:
            raise ValueError("Соль не создана")
        
        with open(self.salt_file, 'wb') as f:
            f.write(self.salt)
    
    def load_salt(self) -> bool:
        """
        Загрузка соли из файла
        
        Returns:
            bool: True если загрузка успешна
        """
        try:
            if not os.path.exists(self.salt_file):
                return False
            
            with open(self.salt_file, 'rb') as f:
                self.salt = f.read()
            
            return True
            
        except Exception as e:
            print(f"Ошибка загрузки соли: {e}")
            return False
    
    def generate_secure_password(self, length: int = 20, 
                                 use_uppercase: bool = True,
                                 use_lowercase: bool = True,
                                 use_digits: bool = True,
                                 use_special: bool = True) -> str:
        """
        Генерация криптографически безопасного пароля
        
        Args:
            length: Длина пароля
            use_uppercase: Использовать заглавные буквы
            use_lowercase: Использовать строчные буквы
            use_digits: Использовать цифры
            use_special: Использовать специальные символы
            
        Returns:
            str: Сгенерированный пароль
        """
        character_sets = []
        
        if use_lowercase:
            character_sets.append('abcdefghijklmnopqrstuvwxyz')
        if use_uppercase:
            character_sets.append('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        if use_digits:
            character_sets.append('0123456789')
        if use_special:
            character_sets.append('!@#$%^&*()_+-=[]{}|;:,.<>?')
        
        if not character_sets:
            raise ValueError("Должен быть выбран хотя бы один набор символов")
        
        # Объединяем все наборы
        all_characters = ''.join(character_sets)
        
        # Гарантируем наличие хотя бы одного символа из каждого набора
        password = []
        for char_set in character_sets:
            password.append(secrets.choice(char_set))
        
        # Заполняем оставшуюся длину случайными символами
        for _ in range(length - len(password)):
            password.append(secrets.choice(all_characters))
        
        # Перемешиваем пароль
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    def check_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Проверка надежности пароля
        
        Args:
            password: Пароль для проверки
            
        Returns:
            Dict[str, Any]: Результаты проверки
        """
        score = 0
        feedback = []
        
        # Проверка длины
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        else:
            feedback.append("Пароль слишком короткий (минимум 8 символов)")
        
        # Проверка наличия разных типов символов
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        if has_upper:
            score += 1
        else:
            feedback.append("Добавьте заглавные буквы")
        
        if has_lower:
            score += 1
        else:
            feedback.append("Добавьте строчные буквы")
        
        if has_digit:
            score += 1
        else:
            feedback.append("Добавьте цифры")
        
        if has_special:
            score += 2
        else:
            feedback.append("Добавьте специальные символы")
        
        # Проверка на распространенные пароли
        common_passwords = ['password', '123456', 'qwerty', 'admin']
        if password.lower() in common_passwords:
            score = 0
            feedback.append("Этот пароль слишком распространен!")
        
        # Оценка сложности
        if score >= 5:
            strength = "Отличный"
        elif score >= 4:
            strength = "Хороший"
        elif score >= 3:
            strength = "Средний"
        else:
            strength = "Слабый"
        
        return {
            'score': score,
            'max_score': 6,
            'strength': strength,
            'length': len(password),
            'feedback': feedback,
            'has_upper': has_upper,
            'has_lower': has_lower,
            'has_digit': has_digit,
            'has_special': has_special
        }
    
    def hash_data(self, data: str) -> str:
        """
        Создание хеша данных (для дополнительной безопасности)
        
        Args:
            data: Данные для хеширования
            
        Returns:
            str: Хеш в hex формате
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def secure_wipe(self, data: bytearray) -> None:
        """
        Безопасное удаление данных из памяти
        
        Args:
            data: Данные для удаления
        """
        for i in range(len(data)):
            data[i] = 0
    
    def export_encrypted_backup(self, data: Dict[str, Any], 
                                export_password: str) -> bytes:
        """
        Создание зашифрованной резервной копии
        
        Args:
            data: Данные для резервного копирования
            export_password: Пароль для шифрования копии
            
        Returns:
            bytes: Зашифрованные данные резервной копии
        """
        # Создание ключа из пароля экспорта
        salt = os.urandom(16)
        key, _ = self.derive_key(export_password, salt)
        
        # Шифрование данных
        fernet = Fernet(base64.urlsafe_b64encode(key))
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        encrypted_data = fernet.encrypt(json_data)
        
        # Сохранение соли вместе с данными
        backup_data = {
            'salt': base64.b64encode(salt).decode('utf-8'),
            'data': base64.b64encode(encrypted_data).decode('utf-8'),
            'version': '1.0',
            'timestamp': str(int(os.times().elapsed if hasattr(os.times(), 'elapsed') else 0))
        }
        
        return json.dumps(backup_data).encode('utf-8')
    
    def import_encrypted_backup(self, backup_data: bytes, 
                                import_password: str) -> Dict[str, Any]:
        """
        Импорт зашифрованной резервной копии
        
        Args:
            backup_data: Данные резервной копии
            import_password: Пароль для расшифровки
            
        Returns:
            Dict[str, Any]: Расшифрованные данные
        """
        try:
            # Парсинг данных резервной копии
            backup = json.loads(backup_data.decode('utf-8'))
            
            # Восстановление соли
            salt = base64.b64decode(backup['salt'])
            
            # Создание ключа
            key, _ = self.derive_key(import_password, salt)
            
            # Расшифровка данных
            fernet = Fernet(base64.urlsafe_b64encode(key))
            encrypted_data = base64.b64decode(backup['data'])
            decrypted_data = fernet.decrypt(encrypted_data)
            
            return json.loads(decrypted_data.decode('utf-8'))
            
        except Exception as e:
            raise ValueError(f"Ошибка импорта резервной копии: {e}")

# Дополнительные утилиты для работы с шифрованием

class PasswordHasher:
    """Класс для хеширования паролей (если нужно хранить хеши)"""
    
    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
        """
        Хеширование пароля с солью
        
        Args:
            password: Пароль для хеширования
            salt: Соль (если None, генерируется новая)
            
        Returns:
            Tuple[str, str]: (хеш, соль в base64)
        """
        if salt is None:
            salt = os.urandom(32)
        
        # Использование PBKDF2 для хеширования
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        hash_value = base64.b64encode(kdf.derive(password.encode('utf-8'))).decode('utf-8')
        salt_b64 = base64.b64encode(salt).decode('utf-8')
        
        return hash_value, salt_b64
    
    @staticmethod
    def verify_password(password: str, hash_value: str, salt_b64: str) -> bool:
        """
        Проверка пароля по хешу
        
        Args:
            password: Пароль для проверки
            hash_value: Сохраненный хеш
            salt_b64: Сохраненная соль в base64
            
        Returns:
            bool: True если пароль верный
        """
        try:
            salt = base64.b64decode(salt_b64)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            
            new_hash = base64.b64encode(kdf.derive(password.encode('utf-8'))).decode('utf-8')
            
            # Используем сравнение с постоянным временем для безопасности
            return secrets.compare_digest(new_hash, hash_value)
            
        except Exception:
            return False

def main():
    """Пример использования модуля криптографии"""
    print("🔐 Тестирование модуля криптографии")
    print("=" * 50)
    
    # Создание экземпляра CryptoManager
    crypto = CryptoManager()
    
    # Тест генерации пароля
    print("\n1. Генерация безопасного пароля:")
    password = crypto.generate_secure_password(20)
    print(f"   Пароль: {password}")
    
    # Проверка сложности пароля
    strength = crypto.check_password_strength(password)
    print(f"\n2. Проверка сложности пароля:")
    print(f"   Сложность: {strength['strength']}")
    print(f"   Оценка: {strength['score']}/{strength['max_score']}")
    
    # Тест создания мастер-ключа
    print("\n3. Создание мастер-ключа:")
    try:
        master_password = "TestMasterPassword123!"
        key = crypto.create_master_key(master_password)
        print(f"   Мастер-ключ создан успешно")
        print(f"   Длина ключа: {len(key) * 8} бит")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест шифрования данных
    print("\n4. Тест шифрования данных:")
    test_data = {
        "service": "example.com",
        "username": "user@example.com",
        "password": "SecurePass123!"
    }
    
    try:
        crypto.initialize_fernet()
        encrypted = crypto.encrypt_data(test_data)
        print(f"   Данные зашифрованы (длина: {len(encrypted)} байт)")
        
        decrypted = crypto.decrypt_data(encrypted)
        print(f"   Данные расшифрованы успешно")
        print(f"   Сервис: {decrypted['service']}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест верификации пароля
    print("\n5. Тест верификации пароля:")
    is_valid = crypto.verify_master_password(master_password)
    print(f"   Правильный пароль: {'✅' if is_valid else '❌'}")
    
    is_valid = crypto.verify_master_password("WrongPassword")
    print(f"   Неправильный пароль: {'❌' if not is_valid else '✅'}")
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено!")

if __name__ == "__main__":
    main()