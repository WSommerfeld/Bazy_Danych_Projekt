import tkinter as tk
from tkinter import messagebox


class RentalWindow:
    def __init__(self, root, conn):
       
        self.conn = conn
        self.root = root
        self.root.title("Wypożycz robota")
        
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()

    def create_widgets(self):
        cur = self.conn.cursor()
        cur.execute("SELECT robot_id, model, type FROM Robots WHERE robot_id NOT IN (SELECT robot_id FROM Reservations)")
        self.available_robots = cur.fetchall()

        if not self.available_robots:
            messagebox.showinfo("Wypożyczanie robota", "Brak dostępnych robotów.")
            self.root.destroy()  
            return

       
        tk.Label(self.root, text="Dostępne roboty:").pack(pady=5)
        self.robot_var = tk.StringVar(self.root)
        robot_options = [f"{r[0]}: {r[1]} ({r[2]})" for r in self.available_robots]
        tk.OptionMenu(self.root, self.robot_var, *robot_options).pack(pady=5)

        tk.Label(self.root, text="Imię klienta:").pack(pady=5)
        self.first_name_entry = tk.Entry(self.root)
        self.first_name_entry.pack(pady=5)

        tk.Label(self.root, text="Nazwisko klienta:").pack(pady=5)
        self.last_name_entry = tk.Entry(self.root)
        self.last_name_entry.pack(pady=5)

        tk.Label(self.root, text="Czas trwania wypożyczenia (dni):").pack(pady=5)
        self.rental_duration_entry = tk.Entry(self.root)
        self.rental_duration_entry.pack(pady=5)

        tk.Label(self.root, text="Cena (PLN):").pack(pady=5)
        self.price_entry = tk.Entry(self.root)
        self.price_entry.pack(pady=5)

       
        submit_button = tk.Button(self.root, text="Wypożycz", command=self.submit_rental)
        submit_button.pack(pady=10)

    def submit_rental(self):
        cur = self.conn.cursor()
        robot_id = self.robot_var.get().split(":")[0]
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        rental_duration = self.rental_duration_entry.get()
        price = self.price_entry.get()

        #Walidacja danych
        if not (robot_id and first_name and last_name and rental_duration and price):
            messagebox.showerror("Błąd", "Wszystkie pola muszą być wypełnione.")
            return


        #Walidacja imenia i nazwiska
        if not first_name.isalpha() or not last_name.isalpha():
            messagebox.showerror("Błąd", "Imię i nazwisko muszą zawierać tylko litery.")
            return


        # Walidacja ceny - musi być liczbą dodatnią
        try:
            price = float(price)
            if price <= 0:
                raise ValueError("Cena musi być dodatnia.")
        except ValueError as e:
            messagebox.showerror("Błąd", f"Niepoprawna cena: {e}")
            return

        # Walidacja czasu trwania wypożyczenia - musi być liczbą dodatnią
        try:
            rental_duration = int(rental_duration)
            if rental_duration <= 0:
                raise ValueError("Czas trwania wypożyczenia musi być dodatnią liczbą dni.")
        except ValueError as e:
            messagebox.showerror("Błąd", f"Niepoprawny czas trwania wypożyczenia: {e}")
            return

        try:
            cur.execute(
                "INSERT INTO Reservations (customer_first_name, customer_last_name, robot_id, payment_status, start_date, end_date, income) "
                "VALUES (?, ?, ?, 'unpaid', DATE('now'), DATE('now', ? || ' day'), ?)",
                (first_name, last_name, robot_id, rental_duration, price)
            )
            self.conn.commit()
            messagebox.showinfo("Sukces", "Robot został wypożyczony!")
            self.root.destroy()  
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wypożyczyć robota: {e}")
