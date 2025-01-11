import tkinter as tk
from tkinter import messagebox


class LoginScreen:
    def __init__(self, root):
        # Konfiguracja głównego okna
        self.root = root
        self.root.title("Ekran logowania")
        self.root.geometry("300x200")
        
        # Etykieta i pole dla nazwy użytkownika
        self.username_label = tk.Label(root, text="Nazwa użytkownika:")
        self.username_label.pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)
        
        # Etykieta i pole dla hasła
        self.password_label = tk.Label(root, text="Hasło:")
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)
        
        # Przycisk logowania
        self.login_button = tk.Button(root, text="Zaloguj", command=self.check_login)
        self.login_button.pack(pady=10)

    def check_login(self):
        # Pobieranie wprowadzonych danych
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        #tu przeniesiona będzie walidacja czy admin czy user


