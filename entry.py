import tkinter as tk
from tkinter import messagebox
import dbbasic as db
from login_screen import LoginScreen
from GUI import RobotRentalApp

DATA_BASE = "test7.db"


def entry():
    # Połączenie bazowe do weryfikacji logowania
    base_connection = db.connect(DATA_BASE)
    def on_login_success(role):
        """
        Funkcja wywoływana po pomyślnym logowaniu.
        Tworzy połączenie dla odpowiedniej roli (admin/pracownik)
        i uruchamia główny interfejs aplikacji.
        """
        # Tworzenie dedykowanego połączenia w zależności od roli użytkownika
        if role == "admin":
            # Połączenie dla administratora
            user_connection = db.connect(DATA_BASE)
            messagebox.showinfo("Połączenie", "Połączono jako administrator.")
        elif role == "user":
            # Połączenie dla pracownika
            user_connection = db.connect(DATA_BASE)
            messagebox.showinfo("Połączenie", "Połączono jako pracownik.")
        else:
            # Obsługa nieznanej roli użytkownika
            messagebox.showerror("Błąd", "Nieznana rola użytkownika.")
            return

        # Uruchomienie głównego GUI z dedykowanym połączeniem i odpowiednią rolą
        root = tk.Tk()

        app = RobotRentalApp(root, user_connection, role == "admin")  # Przekazanie is_admin

        root.mainloop()


    # Uruchomienie ekranu logowania

    login_root = tk.Tk()
    login_screen = LoginScreen(login_root, base_connection, on_login_success)

    login_root.mainloop()



