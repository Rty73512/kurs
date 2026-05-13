import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import pyperclip
import secrets
import string


from crypto import CryptoManager

class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("PasswordManager")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
       
        # Переменные
        self.current_user = None
        self.master_password = None
        self.passwords = {}
        self.data_file = "passwords.enc"
        self.crypto = CryptoManager()
        
        # Цветовая схема
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'entry_bg': '#3c3f41',
            'button_bg': '#4a90d9',
            'button_fg': '#ffffff',
            'tree_bg': '#3c3f41',
            'tree_fg': '#ffffff',
            'tree_selected': '#4a90d9'
        }
        
        # Настройка стилей
        self.setup_styles()
        
        # Создание GUI
        self.show_login_screen()
    
    def setup_styles(self):
        """Настройка стилей ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка цветов для разных элементов
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', 
                       background=self.colors['button_bg'], 
                       foreground=self.colors['button_fg'],
                       borderwidth=1,
                       focusthickness=3,
                       focuscolor='none')
        style.map('TButton',
                 background=[('active', '#3a7bc8')])
        
        style.configure('Treeview', 
                       background=self.colors['tree_bg'],
                       foreground=self.colors['tree_fg'],
                       fieldbackground=self.colors['tree_bg'])
        style.map('Treeview',
                 background=[('selected', self.colors['tree_selected'])])
        
        style.configure('TEntry', 
                       fieldbackground=self.colors['entry_bg'],
                       foreground=self.colors['fg'])
        
        # Стиль для заголовков
        style.configure('Header.TLabel', 
                       font=('Arial', 24, 'bold'),
                       padding=(0, 20))
        
        # Стиль для подзаголовков
        style.configure('SubHeader.TLabel', 
                       font=('Arial', 12),
                       padding=(0, 10))
    
    def show_login_screen(self):
        """Экран входа/регистрации"""
        self.clear_window()
        
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding=(50, 30))
        main_frame.pack(expand=True, fill='both')
        
        # Заголовок
        header = ttk.Label(main_frame, text="", style='Header.TLabel')
        header.pack()
        
        subtitle = ttk.Label(main_frame, text="Вход", style='SubHeader.TLabel')
        subtitle.pack()
        
        # Фрейм для ввода
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=30)
        
        # Мастер-пароль
        ttk.Label(input_frame, text="Введите мастер-пароль:", font=('Arial', 11)).pack(anchor='w')
        self.master_password_var = tk.StringVar()
        master_password_entry = ttk.Entry(input_frame, textvariable=self.master_password_var, show="●", width=40,font=('Arial', 11))
        master_password_entry.pack(pady=(5, 20))
        
        # Подтверждение пароля (только для регистрации)
        ttk.Label(input_frame, text="Подтвердите пароль:", font=('Arial', 11)).pack(anchor='w')
        self.confirm_password_var = tk.StringVar()
        confirm_password_entry = ttk.Entry(input_frame,
                                          textvariable=self.confirm_password_var,
                                          show="●", 
                                          width=40,
                                          font=('Arial', 11))
        confirm_password_entry.pack(pady=(5, 20))
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(pady=20)
        
        # Кнопки входа и регистрации
        login_button = ttk.Button(button_frame, 
                                  text="Войти", 
                                  command=self.login,
                                  width=15)
        login_button.pack(side='left', padx=5)
        
        register_button = ttk.Button(button_frame, 
                                     text="Регистрация", 
                                     command=self.register,
                                     width=15)
        register_button.pack(side='left', padx=5)
        
        # Информация
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(pady=20)
        
        info_text = """
        Рекомендации по созданию мастер-пароля:
        .....
        .........
        .......
        """
        
        ttk.Label(info_frame, text=info_text, font=('Arial', 9), 
                 justify='left').pack()
    
    def show_main_screen(self):
        """Главный экран менеджера паролей"""
        self.clear_window()
        
        # Главный контейнер с отступами
        main_frame = ttk.Frame(self.root, padding=(20, 15))
        main_frame.pack(expand=True, fill='both')
        
        # Верхняя панель с заголовком и кнопками управления
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', pady=(0, 15))
        
        # Заголовок слева
        header = ttk.Label(top_frame, text="🔐 Ваши пароли", 
                          font=('Arial', 20, 'bold'))
        header.pack(side='left')
        
        # Кнопки управления справа
        control_frame = ttk.Frame(top_frame)
        control_frame.pack(side='right')
        
        # Кнопка выхода
        logout_button = ttk.Button(control_frame, 
                                   text="Выйти", 
                                   command=self.logout,
                                   width=12)
        logout_button.pack(side='right', padx=(10, 0))
        
        # Кнопка смены мастер-пароля
        change_password_button = ttk.Button(control_frame, 
                                           text="Сменить пароль", 
                                           command=self.change_master_password,
                                           width=15)
        change_password_button.pack(side='right', padx=5)
        
        # Кнопки действий
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill='x', pady=(0, 15))
        
        # Создание кнопок действий
        actions = [
            ("➕ Добавить", self.add_password, '#27ae60'),
            ("🔍 Поиск", self.search_password, '#e67e22'),
            ("📋 Копировать", self.copy_password, '#3498db'),
            ("✏️ Изменить", self.edit_password, '#f39c12'),
            ("🗑️ Удалить", self.delete_password, '#e74c3c'),
            ("🎲 Генератор", self.generate_password_window, '#9b59b6')
        ]
        
        for text, command, _ in actions:
            btn = ttk.Button(action_frame, text=text, command=command, width=12)
            btn.pack(side='left', padx=3)
        
        # Поисковая строка
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(search_frame, text="🔍 Поиск:").pack(side='left', padx=(0, 10))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, 
                                textvariable=self.search_var,
                                width=40,
                                font=('Arial', 10))
        search_entry.pack(side='left', fill='x', expand=True)
        
        # Таблица с паролями
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(expand=True, fill='both')
        
        # Создание Treeview с прокруткой
        self.tree = ttk.Treeview(tree_frame, 
                                 columns=('service', 'username', 'password', 'notes'),
                                 show='headings',
                                 selectmode='browse')
        
        # Настройка заголовков
        self.tree.heading('service', text='Сервис', command=lambda: self.sort_tree('service', False))
        self.tree.heading('username', text='Логин', command=lambda: self.sort_tree('username', False))
        self.tree.heading('password', text='Пароль', command=lambda: self.sort_tree('password', False))
        self.tree.heading('notes', text='Заметки', command=lambda: self.sort_tree('notes', False))
        
        # Настройка ширины колонок
        self.tree.column('service', width=200, minwidth=100)
        self.tree.column('username', width=150, minwidth=80)
        self.tree.column('password', width=150, minwidth=80)
        self.tree.column('notes', width=250, minwidth=100)
        
        # Добавление прокрутки
        scrollbar_y = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Размещение элементов
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        # Настройка весов для ресайза
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(main_frame, 
                              textvariable=self.status_var,
                              relief='sunken',
                              padding=(5, 2))
        status_bar.pack(fill='x', pady=(10, 0))
        
        # Двойной клик для копирования
        self.tree.bind('<Double-Button-1>', lambda e: self.copy_password())
        
        # Обновление списка
        self.refresh_password_list()
    
    def clear_window(self):
        """Очистка окна от всех виджетов"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def login(self):
        """Вход в систему"""
        master_password = self.master_password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        if not master_password or not confirm_password:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        if master_password != confirm_password:
            messagebox.showerror("Ошибка", "Пароли не совпадают!")
            return
        
        # Проверка пароля через крипто-модуль
        if self.crypto.verify_master_password(master_password):
            self.master_password = master_password
            self.crypto.initialize_fernet()
            self.load_data()
            messagebox.showinfo("Успех", "Вход выполнен успешно!")
            self.show_main_screen()
        else:
            messagebox.showerror("Ошибка", "Неверный мастер-пароль!")
        
    
    def register(self):
        """Регистрация нового пользователя"""
        master_password = self.master_password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        if not master_password or not confirm_password:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        if master_password != confirm_password:
            messagebox.showerror("Ошибка", "Пароли не совпадают!")
            return
        
        # Проверка сложности пароля
        strength = self.crypto.check_password_strength(master_password)
        if strength['score'] < 3:
            if not messagebox.askyesno("Предупреждение", 
                                    f"Пароль слишком слабый ({strength['strength']}).\n"
                                    f"{chr(10).join(strength['feedback'])}\n\n"
                                    "Всё равно продолжить?"):
                return
        
        if len(master_password) < 8:
            messagebox.showwarning("Предупреждение", 
                                "Рекомендуется использовать пароль длиной не менее 8 символов")
        
        # Проверка на существование данных
        if os.path.exists(self.data_file) or os.path.exists(self.crypto.salt_file):
            if not messagebox.askyesno("Внимание", 
                                    "Данные уже существуют. Создать новые?\n"
                                    "Старые данные будут потеряны!"):
                return
        
        # Создание нового мастер-ключа через crypto модуль
        self.master_password = master_password
        self.crypto.create_master_key(master_password)
        self.crypto.initialize_fernet()
        
        # Инициализация пустых данных
        self.passwords = {}
        self.save_data()
        
        messagebox.showinfo("Успех", "Регистрация выполнена успешно!")
        self.show_main_screen()
    
    def create_new_data(self):
        """Создание новых данных"""
        # Генерация ключа
        key = Fernet.generate_key()
        self.fernet = Fernet(key)
        
        # Сохранение ключа
        with open(self.key_file, 'wb') as key_file:
            key_file.write(key)
        
        # Создание пустого файла данных
        self.passwords = {}
        self.save_data()
    
    def save_data(self):
        """Сохранение данных с шифрованием"""
        try:
            if self.crypto.fernet is None:
                raise ValueError("Шифрование не инициализировано")
            
            # Шифрование всех данных
            encrypted_data = self.crypto.encrypt_data(self.passwords)
            
            # Сохранение в файл
            with open(self.data_file, 'wb') as f:
                f.write(encrypted_data)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения данных: {str(e)}")

    def load_data(self):
        """Загрузка данных с расшифровкой"""
        try:
            if not os.path.exists(self.data_file):
                self.passwords = {}
                return
            
            if self.crypto.fernet is None:
                raise ValueError("Шифрование не инициализировано")
            
            # Чтение зашифрованных данных
            with open(self.data_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Расшифровка
            self.passwords = self.crypto.decrypt_data(encrypted_data)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {str(e)}")
            self.passwords = {}
    
    def logout(self):
        """Выход из системы"""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.current_user = None
            self.master_password = None
            self.fernet = None
            self.passwords = {}
            self.show_login_screen()
    
    def add_password(self):
        """Добавление нового пароля"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить пароль")
        dialog.geometry("500x450")
        dialog.resizable(False, False)
        
        # Центрирование окна
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Стили для диалога
        dialog.configure(bg=self.colors['bg'])
        
        # Фрейм для формы
        form_frame = ttk.Frame(dialog, padding=(30, 20))
        form_frame.pack(expand=True, fill='both')
        
        # Поля ввода
        fields = [
            ("Сервис:", "service"),
            ("Логин:", "username"),
            ("Пароль:", "password"),
            ("URL:", "url"),
            ("Заметки:", "notes")
        ]
        
        entries = {}
        
        for label_text, field_name in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill='x', pady=8)
            
            label = ttk.Label(frame, text=label_text, width=10, font=('Arial', 10))
            label.pack(side='left')
            
            entry = ttk.Entry(frame, font=('Arial', 10))
            entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
            entries[field_name] = entry
        
        # Кнопка генерации пароля
        gen_button = ttk.Button(form_frame, 
                               text="🎲 Сгенерировать пароль",
                               command=lambda: self.generate_password_dialog(entries['password']))
        gen_button.pack(pady=10)
        
        # Кнопки сохранения и отмены
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(pady=20)
        
        save_button = ttk.Button(button_frame, 
                                text="Сохранить", 
                                command=lambda: self.save_new_password(entries, dialog))
        save_button.pack(side='left', padx=5)
        
        cancel_button = ttk.Button(button_frame, 
                                  text="Отмена", 
                                  command=dialog.destroy)
        cancel_button.pack(side='left', padx=5)
    
    def save_new_password(self, entries, dialog):
        """Сохранение нового пароля"""
        service = entries['service'].get()
        username = entries['username'].get()
        password = entries['password'].get()
        url = entries['url'].get()
        notes = entries['notes'].get()
        
        if not service or not username or not password:
            messagebox.showerror("Ошибка", "Заполните обязательные поля (сервис, логин, пароль)!")
            return
        
        if service in self.passwords:
            if not messagebox.askyesno("Предупреждение", 
                                      f"Пароль для {service} уже существует. Обновить?"):
                return
        
        # Сохранение данных
        self.passwords[service] = {
            'username': username,
            'password': password,
            'url': url,
            'notes': notes
        }
        
        self.save_data()
        messagebox.showinfo("Успех", f"Пароль для {service} сохранен!")
        dialog.destroy()
        self.refresh_password_list()
    
    def generate_password_dialog(self, entry_widget):
        """Генерация пароля в диалоге"""
        password = self.generate_password()
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, password)
    
    def generate_password(self):
        """Генерация надежного пароля с использованием крипто-модуля"""
        return self.crypto.generate_secure_password(
            length=20,
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_special=True
        )
    
    def generate_password_window(self):
        """Окно генератора паролей"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Генератор паролей")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['bg'])
        
        frame = ttk.Frame(dialog, padding=(20, 15))
        frame.pack(expand=True, fill='both')
        
        ttk.Label(frame, text="Сгенерированный пароль:", font=('Arial', 11)).pack()
        
        password_var = tk.StringVar()
        password_entry = ttk.Entry(frame, 
                                   textvariable=password_var,
                                   font=('Arial', 14),
                                   justify='center')
        password_entry.pack(pady=20, fill='x')
        
        def generate_new():
            password = self.generate_password()
            password_var.set(password)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        gen_button = ttk.Button(button_frame, 
                                text="Сгенерировать", 
                                command=generate_new)
        gen_button.pack(side='left', padx=5)
        
        copy_button = ttk.Button(button_frame, 
                                text="Копировать", 
                                command=lambda: pyperclip.copy(password_var.get()))
        copy_button.pack(side='left', padx=5)
        
        # Сразу генерируем первый пароль
        generate_new()
    
    def search_password(self):
        """Поиск пароля"""
        self.search_var.set("")
        # Фокусируемся на первом элементе после поиска
        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children[0])
            self.tree.focus(children[0])
    
    def on_search_change(self, *args):
        """Обработка изменения поискового запроса"""
        search_term = self.search_var.get().lower()
        
        # Очистка списка
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Фильтрация и отображение
        for service, data in self.passwords.items():
            if (search_term in service.lower() or 
                search_term in data['username'].lower() or 
                search_term in data.get('url', '').lower()):
                self.tree.insert('', 'end', values=(
                    service,
                    data['username'],
                    '********',
                    data.get('notes', '')
                ))
    
    def copy_password(self):
        """Копирование пароля в буфер обмена"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите пароль для копирования")
            return
        
        item = self.tree.item(selected[0])
        service = item['values'][0]
        
        if service in self.passwords:
            password = self.passwords[service]['password']
            pyperclip.copy(password)
            self.status_var.set(f"Пароль для {service} скопирован в буфер обмена")
            self.root.after(3000, lambda: self.status_var.set("Готов к работе"))
    
    def edit_password(self):
        """Редактирование пароля"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите пароль для редактирования")
            return
        
        item = self.tree.item(selected[0])
        service = item['values'][0]
        
        if service not in self.passwords:
            return
        
        data = self.passwords[service]
        
        # Создаем диалог редактирования
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Редактировать пароль - {service}")
        dialog.geometry("500x450")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['bg'])
        
        form_frame = ttk.Frame(dialog, padding=(30, 20))
        form_frame.pack(expand=True, fill='both')
        
        fields = [
            ("Сервис:", "service", service),
            ("Логин:", "username", data['username']),
            ("Пароль:", "password", data['password']),
            ("URL:", "url", data.get('url', '')),
            ("Заметки:", "notes", data.get('notes', ''))
        ]
        
        entries = {}
        
        for label_text, field_name, value in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill='x', pady=8)
            
            label = ttk.Label(frame, text=label_text, width=10, font=('Arial', 10))
            label.pack(side='left')
            
            entry = ttk.Entry(frame, font=('Arial', 10))
            entry.insert(0, value)
            entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
            entries[field_name] = entry
        
        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(pady=20)
        
        def save_changes():
            new_service = entries['service'].get()
            new_data = {
                'username': entries['username'].get(),
                'password': entries['password'].get(),
                'url': entries['url'].get(),
                'notes': entries['notes'].get()
            }
            
            if not new_service or not new_data['username'] or not new_data['password']:
                messagebox.showerror("Ошибка", "Заполните обязательные поля!")
                return
            
            # Удаляем старую запись если изменилось имя сервиса
            if new_service != service:
                del self.passwords[service]
            
            self.passwords[new_service] = new_data
            self.save_data()
            
            messagebox.showinfo("Успех", "Пароль обновлен!")
            dialog.destroy()
            self.refresh_password_list()
        
        save_button = ttk.Button(button_frame, text="Сохранить", command=save_changes)
        save_button.pack(side='left', padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Отмена", command=dialog.destroy)
        cancel_button.pack(side='left', padx=5)
    
    def delete_password(self):
        """Удаление пароля"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите пароль для удаления")
            return
        
        item = self.tree.item(selected[0])
        service = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить пароль для {service}?"):
            if service in self.passwords:
                del self.passwords[service]
                self.save_data()
                self.status_var.set(f"Пароль для {service} удален")
                self.refresh_password_list()
    
    def change_master_password(self):
        """Смена мастер-пароля"""
        old_password = simpledialog.askstring("Смена пароля", 
                                              "Введите старый мастер-пароль:",
                                              show='●')
        
        if old_password != self.master_password:
            messagebox.showerror("Ошибка", "Неверный мастер-пароль!")
            return
        
        new_password = simpledialog.askstring("Смена пароля", 
                                              "Введите новый мастер-пароль:",
                                              show='●')
        
        if not new_password:
            return
        
        confirm_password = simpledialog.askstring("Смена пароля", 
                                                  "Подтвердите новый пароль:",
                                                  show='●')
        
        if new_password != confirm_password:
            messagebox.showerror("Ошибка", "Пароли не совпадают!")
            return
        
        if len(new_password) < 8:
            messagebox.showwarning("Предупреждение", 
                                 "Рекомендуется использовать пароль длиной не менее 8 символов")
        
        self.master_password = new_password
        messagebox.showinfo("Успех", "Мастер-пароль изменен!")
    
    def sort_tree(self, col, reverse):
        """Сортировка по колонке"""
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        items.sort(reverse=reverse)
        
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Переключаем направление сортировки
        self.tree.heading(col, command=lambda: self.sort_tree(col, not reverse))
    
    def refresh_password_list(self):
        """Обновление списка паролей"""
        # Очистка текущего списка
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление данных
        for service, data in self.passwords.items():
            self.tree.insert('', 'end', values=(
                service,
                data['username'],
                '********',
                data.get('notes', '')
            ))
