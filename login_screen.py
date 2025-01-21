import tkinter as tk
from tkinter import messagebox
import bcrypt
import sys



"""

HASLA I LOGINY

login: johndoe, password: password1,
login: janedoe, password: password2,
login: smithj, password: password3,
login: x, password: x
login: Jan03, password: 12345
login: AnnaN, password: 12345

"""

'''
Moduł login_screen.py odpowiada za utworzenie
i obsługę okna logowania
'''


class LoginScreen:
    def __init__(self, root,db_connection, on_login_success):
        
        self.root = root
        self.db_connection = db_connection  # Główne połączenie do bazy danych
        self.on_login_success = on_login_success  # Funkcja wywoływana po pomyślnym logowaniu
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        
        
        
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

    def close(self):
        """Obsługa zdarzenia zamknięcia okna."""

        try:
            # Zamknięcie połączenia z bazą danych, jeśli istnieje
            if hasattr(self, "conn") and self.conn:
                self.conn.close()
                print("Połączenie z bazą danych zostało zamknięte.")
        except Exception as e:
            print(f"Błąd podczas zamykania połączenia z bazą danych: {e}")

        # Zamknięcie okna aplikacji
        self.root.destroy()

        # Wymuszone zakończenie programu, aby upewnić się, że proces został zakończony
        sys.exit(0)

    def check_login(self):
        # Pobranie danych z pól
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Błąd", "Proszę podać login i hasło.")
            return

        # Sprawdzanie użytkownika w bazie danych
        cur = self.db_connection.cursor()
        cur.execute("SELECT password_hash, role FROM Users WHERE login = ?", (username,))
        user = cur.fetchone()

        
        # Sprawdzenie czy istnieje
        if user:
            stored_password_hash, role = user # Rozpakowywanie danych
            
            if isinstance(stored_password_hash, str):
                stored_password_hash = stored_password_hash.encode("utf-8")



            # Weryfikacja hasła
            if bcrypt.checkpw(password.encode("utf-8"), stored_password_hash):
                messagebox.showinfo("Sukces", f"Zalogowano jako {role}.")

                self.root.withdraw()  # Zamknięcie okna logowania
                self.on_login_success(role)  # Przekazanie roli do głównego programu
                

            else:
                messagebox.showerror("Błąd", "Niepoprawne hasło.")
        else:
            messagebox.showerror("Błąd", "Użytkownik o podanym loginie nie istnieje.")
    
  
