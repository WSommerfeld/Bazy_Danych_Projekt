import tkinter as tk
from tkinter import messagebox

import dbbasic as db


class RentalWindow:
    def __init__(self, root, conn):
       
        self.conn = conn
        self.root = root
        self.root.title("Wypożycz robota")
        #zmiana wielkosci okna
        self.root.geometry("600x600")
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()

    def create_widgets(self):
        cur = self.conn.cursor()
        #zmiany~Lasak
        #zmieniłem zapytanie tak żeby robiło właściwie to samo, przy nowej bazie
        #dodatkowo sprawdza czy aktualna data jest w okresie rezerwacji jakiegoś
        #robota i wtedy oznacza go jako niedostępnego
        cur.execute("SELECT Robots.id, Models.name, Models.type FROM Robots"
            " INNER JOIN Models ON Robots.model_id=Models.id"
            " WHERE Robots.id NOT IN (SELECT robot_id FROM Reservations WHERE"
            " CURRENT_DATE BETWEEN start_date AND end_date)")
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

        tk.Label(self.root, text="Nr telefonu:").pack(pady=5)
        self.phone_entry= tk.Entry(self.root)
        self.phone_entry.pack(pady=5)

        tk.Label(self.root, text="Adres email:").pack(pady=5)
        self.email_entry= tk.Entry(self.root)
        self.email_entry.pack(pady=5)

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
        phone = self.phone_entry.get()
        email=self.email_entry.get()
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
            #zmiany~Lasak
            customer_id=0
            #klient już coś wypożyczał
            if(db.execute(self.conn,"SELECT COUNT(id) FROM CUSTOMERS WHERE telephone = '"+str(phone)+"'").fetchone()[0]==1):

                customer_id=db.execute(self.conn,"SELECT id FROM CUSTOMERS WHERE telephone = '"+str(phone)+"'").fetchone()[0]

            #pierwsze wypożyczenie
            else:
                customer_id=db.execute(self.conn,"SELECT COUNT(telephone) FROM CUSTOMERS").fetchone()[0]+1
                db.execute(self.conn,"INSERT INTO CUSTOMERS (id, email, telephone, first_name, last_name) VALUES "
                                     "('"+str(customer_id)+"', '"+email+"', '"+phone+"'"
                                     ", '"+first_name+"', '"+last_name+"')")

            #wstawienie rezerwacji
            #automatycznie ustawia status platnosci na pending
            #data startu ustawiana jako dzisiaj
            #data konca dzisiaj+rental_duration
            reservation_id=db.execute(self.conn,"SELECT COUNT(id) FROM RESERVATIONS").fetchone()[0]+1
            print("rezerwacja")
            print(reservation_id)
            print(customer_id)
            print(robot_id)
            db.execute(self.conn,"INSERT INTO RESERVATIONS"
                       "(id,customer_id,robot_id,payment_status, start_date, end_date) VALUES "
                        "("+str(reservation_id)+","+str(customer_id)+","+str(robot_id)+","
                         " 'Pending', CURRENT_DATE, DATE(CURRENT_DATE, '+"+str(rental_duration)+" day'))")


            messagebox.showinfo("Sukces", "Robot został wypożyczony!")
           
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wypożyczyć robota: {e}")
