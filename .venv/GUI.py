import tkinter as tk
from tkinter import messagebox, simpledialog
import dbbasic as db
from rental_window import RentalWindow
import bcrypt
import sqlite3

DATA_BASE = "test6.db"

# Funkcja uruchamiająca GUI
def start_gui():
    root = tk.Tk()
    app = RobotRentalApp(root)
    root.mainloop()


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())



def check_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)  # Porównanie hasła


# Klasa GUI
class RobotRentalApp:
    def __init__(self, root,db_connection, is_admin):
        self.root = root
        self.conn = db_connection
        self.is_admin = is_admin  # Informacja o roli użytkownika
        self.root.title("Robot Rental Agency")
        self.root.geometry("600x400")
        self.conn = db.connect(DATA_BASE)  # Połączenie z bazą danych
        self.create_widgets()

    def create_widgets(self):
        # Menu główne
        self.robot_types_button = tk.Button(
            self.root, text="Wyświetl typy robotów", command=self.display_robot_types
        )
        self.robot_types_button.pack(pady=10)

        self.available_robots_button = tk.Button(
            self.root, text="Pokaż dostępne roboty", command=self.show_available_robots
        )
        self.available_robots_button.pack(pady=10)

        self.rent_robot_button = tk.Button(
            self.root, text="Wypożycz robota", command=self.rent_robot
        )
        self.rent_robot_button.pack(pady=10)

        self.manage_reservations_button = tk.Button(
            self.root, text="Zarządzaj rezerwacjami", command=self.manage_reservations
        )
        self.manage_reservations_button.pack(pady=10)

        # Przycisk logowania
        self.login_button = tk.Button(self.root, text="Zaloguj się", command=self.login)
        self.login_button.pack(pady=10)

        self.entry_button = tk.Button(self.root, text = "Zarejestruj się", command = self.register_user)
        self.entry_button.pack(pady=10)

         # Funkcje tylko dla administratorów
        if self.is_admin:
            self.manage_users_button = tk.Button(
                self.root, text="Zarządzaj użytkownikami", command=self.manage_users
            )
            self.manage_users_button.pack(pady=10)

            self.edit_robot_button = tk.Button(
                self.root, text="Edytuj robota", command=self.edit_robot
            )
            self.edit_robot_button.pack(pady=10)

    def register_user(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Rejestracja")

        tk.Label(register_window, text="Login: ").pack(pady=10)
        login_entry = tk.Entry(register_window)
        login_entry.pack(pady=10)

        tk.Label(register_window, text="Email: ").pack(pady=10)
        email_entry = tk.Entry(register_window)
        email_entry.pack(pady=10)

        tk.Label(register_window, text="Imię: ").pack(pady=10)
        first_name_entry = tk.Entry(register_window)
        first_name_entry.pack(pady=10)

        tk.Label(register_window, text="Nazwisko: ").pack(pady=10)
        last_name_entry = tk.Entry(register_window)
        last_name_entry.pack(pady=10)

        tk.Label(register_window, text="Hasło: ").pack(pady=10)
        password_entry = tk.Entry(register_window, show="*")  # Ukrywa hasło
        password_entry.pack(pady=10)

        def register():
            login = login_entry.get()
            email=email_entry.get()
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            password = password_entry.get()

            if not login or not password:
                messagebox.showerror("Błąd", "Proszę podać login i hasło.")
                return

            # Haszowanie hasła przed zapisaniem w bazie
            hashed_password = hash_password(password)

            role = "user"

            # Dodajemy użytkownika do bazy danych
            cur = self.conn.cursor()
            try:
                # Wstawiamy dane użytkownika do bazy
                ID=db.execute(self.conn,"SELECT COUNT(id) FROM USERS").fetchone()[0]+1
                cur.execute(
                    "INSERT INTO Users (id,login, email, first_name, last_name, password_hash, role) VALUES ("
                    "?, ?, ?, ?, ?, ?, ?)",
                    (ID, login, email, first_name, last_name, hashed_password, role)
                )

                self.conn.commit()
                messagebox.showinfo("Sukces", "Użytkownik został zarejestrowany!")
                register_window.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Błąd", "Użytkownik o tym loginie już istnieje.")
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

        register_button = tk.Button(register_window, text="Zarejestruj", command=register)
        register_button.pack(pady=10)

    def login(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Logowanie")

        tk.Label(login_window, text = "Login: ").pack(pady=10)
        login_entry = tk.Entry(login_window)
        login_entry.pack(pady=10)

        tk.Label(login_window, text = "Haslo: ").pack(pady=10)
        password_entry = tk.Entry(login_window)
        password_entry.pack(pady=10)

        def authenticate():
            login = login_entry.get()
            password = password_entry.get()

            if not login or not password:
                messagebox.showerror("Błąd", "Proszę podać login i hasło.")
                return

            # Sprawdzamy w bazie, czy użytkownik istnieje i czy hasło jest poprawne
            cur = self.conn.cursor()
            cur.execute("SELECT password_hash, role FROM Users WHERE login = ?", (login,))
            user = cur.fetchone()


            if user:
                stored_password_hash = user[0]
                role = user[1]

                # Porównanie hasła
                if check_password(stored_password_hash, password):
                    messagebox.showinfo("Sukces", f"Zalogowano jako {role}.")
                    login_window.destroy()

                    if role == "admin":
                        self.admin_role = True  # Ustawiamy flagę, że użytkownik ma uprawnienia administratora
                    else:
                        self.admin_role = False  # Zwykły użytkownik

                    return
                else:
                    messagebox.showerror("Błąd", "Niepoprawne hasło.")
            else:
                messagebox.showerror("Błąd", "Użytkownik o podanym loginie nie istnieje.")

        login_button = tk.Button(login_window, text="Zaloguj", command=authenticate)
        login_button.pack(pady=10)



    def display_robot_types(self):
        try:
            cur = self.conn.cursor()
            
            
            cur.execute("SELECT DISTINCT type FROM Models")
            robot_types = cur.fetchall()
            
        
            if robot_types:
                types_list = [row[0] for row in robot_types]
                messagebox.showinfo("Typy robotów", "\n".join(types_list))
            else:
                messagebox.showinfo("Typy robotów", "Brak danych o typach robotów w bazie.")
        except sqlite3.Error as e:
        
            messagebox.showerror("Błąd bazy danych", f"Wystąpił błąd: {e}")

    def show_available_robots(self):
        # Pobieranie dostępnych robotów
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT Robots.id, Robots.serial_number, Models.name AS model, Models.type 
            FROM Robots 
            INNER JOIN Models ON Robots.model_id = Models.id
            """
        )


        robots = cur.fetchall()
        if robots:
            robot_list = "\n".join([f"ID: {r[0]}, Model: {r[1]}, Typ: {r[2]}" for r in robots])
            messagebox.showinfo("Dostępne roboty", robot_list)
        else:
            messagebox.showinfo("Dostępne roboty", "Brak dostępnych robotów w bazie.")
    
    

    def rent_robot(self):
        RentalWindow(self.root, self.conn)  # Switch to the rental window



    def manage_reservations(self):
        # Zarządzanie rezerwacjami
        messagebox.showinfo("Zarządzaj rezerwacjami", "brak.")

    def manage_users(self):
        # Zarządzanie użytkownikami
        messagebox.showinfo("Zarządzaj użytkownikami", "brak.")

    def edit_robot(self):
        # Sprawdzamy, czy użytkownik ma rolę admin
        if not getattr(self, "is_admin", False):
            messagebox.showerror("Brak uprawnień", "Tylko administratorzy mogą edytować roboty.")
            return


        # Pytamy użytkownika o ID robota do edycji
        robot_id = simpledialog.askinteger("Edycja robota", "Podaj ID robota do edycji:")
        if not robot_id:
            messagebox.showerror("Błąd", "Musisz podać ID robota.")
            return

        # Pobieramy dane robota z bazy danych
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT Robots.id, Models.name AS model_name, Models.type 
            FROM Robots 
            INNER JOIN Models ON Robots.model_id = Models.id 
            WHERE Robots.id = ?
            """,
            (robot_id,)
        )

        robot = cur.fetchone()

        if not robot:
            messagebox.showerror("Błąd", "Robot o podanym ID nie istnieje.")
            return

        # Tworzymy okno do edycji robota
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edycja robota {robot_id}")

        # Wstawiamy dane robota do pól
        tk.Label(edit_window, text="Model:").pack(pady=5)
        model_entry = tk.Entry(edit_window)
        model_entry.insert(0, robot[1])
        model_entry.pack(pady=5)

        tk.Label(edit_window, text="Typ:").pack(pady=5)
        type_entry = tk.Entry(edit_window)
        type_entry.insert(0, robot[2])
        type_entry.pack(pady=5)

        # Funkcja do zapisania edytowanych danych
        def save_changes():
            new_model = model_entry.get()
            new_type = type_entry.get()

            if not new_model or not new_type:
                messagebox.showerror("Błąd", "Wszystkie pola muszą być wypełnione.")
                return

            # Walidacja modelu i typu (tylko litery i cyfry)
            if not new_model.isalnum() or not new_type.isalnum():
                messagebox.showerror("Błąd", "Model i typ muszą zawierać tylko litery i cyfry.")
                return

            try:
                # Zapisujemy zmiany w bazie danych
                cur.execute("UPDATE Robots SET model = ?, type = ? WHERE robot_id = ?", (new_model, new_type, robot_id))
                self.conn.commit()
                messagebox.showinfo("Sukces", "Dane robota zostały zaktualizowane.")
                edit_window.destroy()  # Zamknięcie okna edycji
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się zaktualizować danych robota: {e}")

        # Przycisk do zapisywania zmian
        save_button = tk.Button(edit_window, text="Zapisz zmiany", command=save_changes)
        save_button.pack(pady=10)
    def __del__(self):
        self.conn.close()  # Zamknięcie połączenia z bazą danych
