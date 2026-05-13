import tkinter as tk
from tkinter import messagebox
# from tkinter import ttk, messagebox, simpledialog
# import json
# import os
# import base64
# from cryptography.fernet import Fernet
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
# import pyperclip
# import secrets
# # import string

# from crypto import CryptoManager
from gui import PasswordManager

def main():
    root = tk.Tk()
    app = PasswordManager(root)
    
    # Обработка закрытия окна
    def on_closing():
        if messagebox.askokcancel("Выход", "Уверены что хотите выйти?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()