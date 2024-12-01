import tkinter as tk
from tkinter import messagebox, simpledialog
import dbbasic as db

# Funkcja uruchamiająca GUI
def start_gui():
    root = tk.Tk()
    app = RobotRentalApp(root)
    root.mainloop()

# Klasa GUI
class RobotRentalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Rental Agency")
        self.root.geometry("600x400")
        self.conn = db.connect("test1.db")  # Połączenie z bazą danych
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

        self.manage_users_button = tk.Button(
            self.root, text="Zarządzaj użytkownikami", command=self.manage_users
        )
        self.manage_users_button.pack(pady=10)

    def display_robot_types(self):
        # Pobieranie typów robotów z bazy danych
        robot_types = db.get_robot_types(self.conn)
        if robot_types:
            messagebox.showinfo("Typy robotów", "\n".join(robot_types))
        else:
            messagebox.showinfo("Typy robotów", "Brak danych o typach robotów w bazie.")

    def show_available_robots(self):
        # Pobieranie dostępnych robotów
        cur = self.conn.cursor()
        cur.execute("SELECT robot_id, model, type FROM Robots")
        robots = cur.fetchall()
        if robots:
            robot_list = "\n".join([f"ID: {r[0]}, Model: {r[1]}, Typ: {r[2]}" for r in robots])
            messagebox.showinfo("Dostępne roboty", robot_list)
        else:
            messagebox.showinfo("Dostępne roboty", "Brak dostępnych robotów w bazie.")

    def rent_robot(self):
        # Proces wypożyczenia robota
        cur = self.conn.cursor()
        cur.execute("SELECT robot_id, model, type FROM Robots WHERE robot_id NOT IN (SELECT robot_id FROM Reservations)")
        available_robots = cur.fetchall()

        if available_robots:
            # Wybierz robota
            robot_list = "\n".join([f"{r[0]}: {r[1]} ({r[2]})" for r in available_robots])
            robot_id = simpledialog.askinteger(
                "Wypożycz robota", f"Wybierz ID robota do wypożyczenia:\n\n{robot_list}"
            )

            # Jeśli robot został wybrany
            if robot_id:
                # Pobierz dane klienta
                customer_name = simpledialog.askstring("Dane klienta", "Podaj imię klienta:")
                customer_last_name = simpledialog.askstring("Dane klienta", "Podaj nazwisko klienta:")

                if customer_name and customer_last_name:
                    # Wstaw dane do tabeli Rezerwacje
                    try:
                        cur.execute(
                            "INSERT INTO Reservations (customer_first_name, customer_last_name, robot_id, payment_status, start_date, end_date, income) "
                            "VALUES (?, ?, ?, 'unpaid', DATE('now'), DATE('now', '+7 day'), 1000)",
                            (customer_name, customer_last_name, robot_id),
                        )
                        self.conn.commit()
                        messagebox.showinfo("Wypożyczanie robota", "Robot został wypożyczony!")
                    except Exception as e:
                        messagebox.showerror("Błąd", f"Nie udało się wypożyczyć robota: {e}")
        else:
            messagebox.showinfo("Wypożyczanie robota", "Brak dostępnych robotów.")

    def manage_reservations(self):
        # Zarządzanie rezerwacjami
        messagebox.showinfo("Zarządzaj rezerwacjami", "brak.")

    def manage_users(self):
        # Zarządzanie użytkownikami
        messagebox.showinfo("Zarządzaj użytkownikami", "brak.")

    def __del__(self):
        self.conn.close()  # Zamknięcie połączenia z bazą danych
