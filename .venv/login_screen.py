import tkinter as tk
from tkinter import messagebox
import bcrypt

class LoginScreen:
    def __init__(self, root,db_connection, on_login_success):
        
        self.root = root
        self.db_connection = db_connection  # Główne połączenie do bazy danych
        self.on_login_success = on_login_success  # Funkcja wywoływana po pomyślnym logowaniu
        
        
        
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
            
            #Konwersja hasla na bajty aby moc je zweryfikowac
            stored_password_hash = stored_password_hash.encode('utf-8')


            # Weryfikacja hasła
            if bcrypt.checkpw(password.encode("utf-8"), stored_password_hash):
                messagebox.showinfo("Sukces", f"Zalogowano jako {role}.")
                self.on_login_success(role)  # Przekazanie roli do głównego programu
                self.root.destroy()  # Zamknięcie okna logowania
            else:
                messagebox.showerror("Błąd", "Niepoprawne hasło.")
        else:
            messagebox.showerror("Błąd", "Użytkownik o podanym loginie nie istnieje.")


