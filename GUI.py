import sys
import tkinter as tk
from tkinter import messagebox, simpledialog
import dbbasic as db
from Reservations import ReservationsWindow
from rental_window import RentalWindow
from users_window import UsersWindow
import bcrypt
import sqlite3
import importlib

'''
Moduł GUI.py odpowiada za utworzenie menu głównego aplikacji
i obsługę niektórych opcji tego menu
'''

DATA_BASE = "test7.db"

# Funkcja uruchamiająca GUI
def start_gui():
    root = tk.Tk()
    
    # Połączenie z bazą danych
    db_connection = db.connect(DATA_BASE)  # Tworzenie połączenia do bazy danych
    is_admin = False  # Domyślnie użytkownik nie jest administratorem

    # Tworzenie głównego okna aplikacji
    app = RobotRentalApp(root, db_connection, is_admin)
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
        """Obsługa zdarzenia zamknięcia okna."""
        if messagebox.askokcancel("Quit", "Czy na pewno chcesz zamknąć aplikację?"):
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
   
   
    def update_robot_availability_on_start(conn):
        """
        Jednorazowa aktualizacja dostępności robotów przy uruchomieniu aplikacji.
        :param conn: Obiekt połączenia z bazą danych.
        """
        try:
            cur = conn.cursor()
            # Zapytanie SQL aktualizujące dostępność robotów
            cur.execute("""
                UPDATE Availability
                SET status = 'Available'  -- Ustaw status robota na 'Available' (dostępny)
                WHERE status = 'Unavailable'  -- Rozważamy tylko roboty oznaczone jako 'Unavailable' (niedostępne)
                AND reservation_end_date < DATE('now');  -- Sprawdzamy, czy data zakończenia rezerwacji jest wcześniejsza niż dzisiejsza data
            """)
            conn.commit()  # Zatwierdzenie zmian w bazie danych
            print("Dostępność robotów została zaktualizowana przy starcie aplikacji.")  # Informacja o sukcesie
        except Exception as e:
            # Obsługa błędów, np. problemów z połączeniem do bazy danych
            print(f"Błąd podczas aktualizacji dostępności robotów: {e}")


    def logout(self):
        print("Logging out...")
        self.__del__()
        self.root.destroy()
        import entry
        entry.entry()



    def register_user(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Rejestracja")
        register_window.geometry("400x500")

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
        """
        Wyświetla wszystkie roboty wraz z możliwością zmiany ich dostępności za pomocą menu rozwijanego.
        """
        try:
            # Pobieranie wszystkich robotów i ich statusów dostępności
            cur = self.conn.cursor()
            cur.execute("""
                SELECT Robots.id, Robots.serial_number, Models.name AS model, Models.type, Availability.status 
                FROM Robots 
                INNER JOIN Models ON Robots.model_id = Models.id
                INNER JOIN Availability ON Robots.id = Availability.robot_id
            """)
            robots = cur.fetchall()

            if not robots:
                messagebox.showinfo("Roboty", "Brak robotów w bazie.")
                return

            # Tworzenie okna dialogowego dla robotów
            robots_window = tk.Toplevel(self.root)
            robots_window.title("Lista robotów")
            robots_window.geometry("700x500")

            # Nagłówek listy robotów
            tk.Label(robots_window, text="ID | Numer Seryjny | Model | Typ | Status").pack(pady=10)
            robots_listbox = tk.Listbox(robots_window, width=80)
            robots_listbox.pack(pady=10)

            # Wypełnienie listy robotów
            for r in robots:
                robots_listbox.insert(tk.END, f"ID: {r[0]}, Numer: {r[1]}, Model: {r[2]}, Typ: {r[3]}, Status: {r[4]}")

            # Funkcja zmieniająca status dostępności robota
            def change_availability():
                selected_robot = robots_listbox.curselection()
                if not selected_robot:
                    messagebox.showerror("Błąd", "Proszę wybrać robota.")
                    return

                robot_data = robots[selected_robot[0]]
                robot_id = robot_data[0]
                current_status = robot_data[4]

                # Okno do wyboru nowego statusu
                status_window = tk.Toplevel(robots_window)
                status_window.title(f"Zmień status dla robota ID {robot_id}")
                status_window.geometry("300x150")

                tk.Label(status_window, text=f"Aktualny status: {current_status}").pack(pady=10)
                tk.Label(status_window, text="Wybierz nowy status:").pack(pady=5)

                # Menu rozwijane dla statusów
                status_var = tk.StringVar(status_window)
                status_var.set(current_status)  # Ustawienie obecnego statusu jako domyślnego
                status_menu = tk.OptionMenu(status_window, status_var, "Available", "Unavailable")
                status_menu.pack(pady=5)

                def save_status():
                    new_status = status_var.get()
                    if new_status == current_status:
                        messagebox.showinfo("Informacja", "Status pozostał bez zmian.")
                        status_window.destroy()
                        return

                    try:
                        # Aktualizacja statusu dostępności w bazie danych
                        cur.execute("UPDATE Availability SET status = ? WHERE robot_id = ?", (new_status, robot_id))
                        self.conn.commit()
                        messagebox.showinfo("Sukces", f"Status robota ID {robot_id} został zmieniony na {new_status}.")

                        # Odświeżenie listy robotów
                        robots_listbox.delete(0, tk.END)
                        cur.execute("""
                            SELECT Robots.id, Robots.serial_number, Models.name AS model, Models.type, Availability.status 
                            FROM Robots 
                            INNER JOIN Models ON Robots.model_id = Models.id
                            INNER JOIN Availability ON Robots.id = Availability.robot_id
                        """)
                        updated_robots = cur.fetchall()
                        for r in updated_robots:
                            robots_listbox.insert(tk.END, f"ID: {r[0]}, Numer: {r[1]}, Model: {r[2]}, Typ: {r[3]}, Status: {r[4]}")
                        status_window.destroy()

                    except Exception as e:
                        messagebox.showerror("Błąd", f"Nie udało się zmienić statusu robota: {e}")
                        status_window.destroy()

                # Przycisk do zapisania nowego statusu
                save_button = tk.Button(status_window, text="Zapisz", command=save_status)
                save_button.pack(pady=10)

            # Przycisk do zmiany dostępności
            change_status_button = tk.Button(robots_window, text="Zmień dostępność", command=change_availability)
            change_status_button.pack(pady=10)

            # Przycisk zamykający okno
            close_button = tk.Button(robots_window, text="Zamknij", command=robots_window.destroy)
            close_button.pack(pady=10)

        except sqlite3.Error as e:
            messagebox.showerror("Błąd bazy danych", f"Wystąpił błąd: {e}")

    

    def rent_robot(self):
        RentalWindow(self.root, self.conn,self.is_admin)  # Switch to the rental window



    def manage_reservations(self):
        # Zarządzanie rezerwacjami
        ReservationsWindow(self.root,self.conn,self.is_admin)

    def manage_users(self):
        # Zarządzanie użytkownikami
        UsersWindow(self.root, self.conn,self.is_admin)

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
                if(db.execute(self.conn,"SELECT COUNT(name) FROM models WHERE name = ? ", (new_model,)).fetchone()[0]>0):

                    #id wprowadzonego modelu
                    model_id=db.execute(self.conn,"SELECT id FROM models WHERE name = ?", (new_model,)).fetchone()[0]

                    db.execute(self.conn,"UPDATE Robots SET model_id = ? WHERE id = ?",(model_id,robot_id))

                    messagebox.showinfo("Sukces", "Dane robota zostały zaktualizowane.")
                    edit_window.destroy()  # Zamknięcie okna edycji
                else:
                    #id nowego modelu

                    new_id = db.execute(self.conn,"SELECT COUNT(id) FROM Models").fetchone()[0] + 1

                    db.execute(self.conn,"INSERT INTO models (id, name, type)"
                                         " VALUES(?, ?, ?)",(new_id,new_model,new_type))

                    db.execute(self.conn, "UPDATE Robots SET model_id = ? WHERE id = ?", (new_id,robot_id))

                    messagebox.showinfo("Sukces", "Dane robota zostały zaktualizowane. Dodano nowy model.")
                    edit_window.destroy()  # Zamknięcie okna edycji

            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się zaktualizować danych robota: {e}")

        # Przycisk do zapisywania zmian
        save_button = tk.Button(edit_window, text="Zapisz zmiany", command=save_changes)
        save_button.pack(pady=10)
    def __del__(self):
        if hasattr(self, "conn") and self.conn:
            self.conn.close()  # Zamknięcie połączenia z bazą danych
        #self.conn.close()  # Zamknięcie połączenia z bazą danych

    
