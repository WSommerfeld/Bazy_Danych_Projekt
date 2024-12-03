import tkinter as tk
from tkinter import messagebox, simpledialog
import dbbasic as db
from rental_window import RentalWindow




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
        RentalWindow(self.root, self.conn)  # Switch to the rental window



    def manage_reservations(self):
        # Zarządzanie rezerwacjami
        messagebox.showinfo("Zarządzaj rezerwacjami", "brak.")

    def manage_users(self):
        # Zarządzanie użytkownikami
        messagebox.showinfo("Zarządzaj użytkownikami", "brak.")

    def __del__(self):
        self.conn.close()  # Zamknięcie połączenia z bazą danych
