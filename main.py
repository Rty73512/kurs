import tkinter as tk
from tkinter import messagebox
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