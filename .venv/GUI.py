import tkinter as tk
from tkinter import messagebox, simpledialog
import dbbasic as db
from rental_window import RentalWindow
import bcrypt
import sqlite3
import importlib

DATA_BASE = "test7.db"

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
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.create_widgets()

    # Zamykanie okna (nie działa nadal do końca)
    def close(self):
        print("close")
        self.__del__()
        self.root.destroy()

    def create_widgets(self):
        # Menu główne
        self.robot_types_button = tk.Button(
            self.root, text="Wyświetl typy robotów", command=self.display_robot_types
        )
        self.robot_types_button.pack(pady=10)

        self.available_robots_button = tk.Button(
            self.root, text="Pokaż wszystkie roboty", command=self.show_available_robots
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

        #przycisk wylogowania
        self.logout_button = tk.Button(self.root, text="Wyloguj się", command=self.logout
        )
        self.logout_button.pack(pady=10)


    def logout(self):
        print("Logging out...")
        self.__del__()
        self.root.destroy()
        import entry
        entry.entry()



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
                ID=db.execute(self.conn,"SELECT MAX(id) FROM USERS").fetchone()[0]+1
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
        RentalWindow(self.root, self.conn,self.is_admin)  # Switch to the rental window



    def manage_reservations(self):
        # Zarządzanie rezerwacjami
        #trzeba ustalić ostatecznie zmiany z availability i cenami i można rzeźbić
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
                #zmiany ~Lasak
                #aktualne działanie: jeśli wpiszemy model, który już istnieje w bazie, pole typ robota
                #zostanie zignorowane i robot o zadanym id dostanie model_id które już istnieje w bazie
                #oraz typ odpowiadający temu model_id
                #w przypadku braku nazwy modelu w bazie, do tabeli models zostanie dodany nowy
                #model o zadanym typie (w ograniczeniu industrial, household, garden)

                #model jest w bazie
                if(db.execute(self.conn,"SELECT COUNT(name) FROM models WHERE name = '"+new_model+"'").fetchone()[0]>0):
                    print("stary")
                    #id wprowadzonego modelu
                    model_id=db.execute(self.conn,"SELECT id FROM models WHERE name = '"+new_model+"'").fetchone()[0]

                    db.execute(self.conn,"UPDATE Robots SET model_id = '"+str(model_id)+"' WHERE id = '"+str(robot_id)+"'")

                    messagebox.showinfo("Sukces", "Dane robota zostały zaktualizowane.")
                    edit_window.destroy()  # Zamknięcie okna edycji
                else:
                    #id nowego modelu
                    print("nowy")
                    new_id = db.execute(self.conn,"SELECT COUNT(id) FROM Models").fetchone()[0] + 1

                    db.execute(self.conn,"INSERT INTO models (id, name, type)"
                                         " VALUES("+str(new_id)+", '"+str(new_model)+"', '"+str(new_type)+"')")

                    db.execute(self.conn, "UPDATE Robots SET model_id = '"+str(new_id)+"' WHERE id = '"+str(robot_id)+"'")

                    messagebox.showinfo("Sukces", "Dane robota zostały zaktualizowane. Dodano nowy model.")
                    edit_window.destroy()  # Zamknięcie okna edycji

            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się zaktualizować danych robota: {e}")

        # Przycisk do zapisywania zmian
        save_button = tk.Button(edit_window, text="Zapisz zmiany", command=save_changes)
        save_button.pack(pady=10)
    def __del__(self):
        self.conn.close()  # Zamknięcie połączenia z bazą danych
