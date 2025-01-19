import tkinter
import tkinter as tk
from tkinter import messagebox
import tkcalendar as tkcal
import datetime
import dbbasic as db
import GUI


class ReservationsWindow:
    def __init__(self, root, conn, is_admin):
        self.conn = conn
        self.root = root
        self.is_admin = is_admin
        self.root.title("Rezerwacjami")

        # zmiana wielkosci okna
        self.root.geometry("750x400")
        for widget in self.root.winfo_children():
            widget.destroy()

        self.create_widgets()

    def create_widgets(self):
        cur = self.conn.cursor()

        cur.execute("SELECT  Customers.first_name, Customers.last_name, Customers.email, Customers.telephone,"
    " Models.name, Reservations.start_date, Reservations.end_date, Reservations.payment_status,"
    " (julianday(Reservations.end_date) - julianday(Reservations.start_date))*Availability.price as Price, Reservations.id FROM Customers"
    " INNER JOIN Reservations ON Reservations.customer_id = Customers.id"
    " INNER JOIN Robots ON Reservations.robot_id = Robots.id"
    " INNER JOIN Models ON Robots.model_id = Models.id"
    " INNER JOIN Availability ON Robots.id = Availability.robot_id")
        self.res = cur.fetchall()

        if not self.res:
            messagebox.showinfo("Zarządzaj rezerwacjami", "Brak rezerwacji")
            self.back()
            return

        back_button = tk.Button(self.root, text="Wróć", command=self.back)
        back_button.pack(pady=5)

        tk.Label(self.root, text="Rezerwacje: ").pack(pady=5)
        self.res_var = tk.StringVar(self.root)
        res_options = [f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]} zł| :{r[9]}" for r in self.res]
        self.res_menu=tk.OptionMenu(self.root, self.res_var, *res_options)
        self.res_menu.place(x=50,y=70)

        paid_button = tk.Button(self.root, text="Zapłacone", command=self.setpaid)
        paid_button.place(x=235,y=300)

        failed_button = tk.Button(self.root, text="Błąd płatności", command=self.setfailed)
        failed_button.place(x=310,y=300)

        del_button = tk.Button(self.root, text="Usuń rezerwację", command=self.deleteReservation)
        del_button.place(x=410,y=300)


    #Cofnięcie się do głównego menu
    def back(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        root=self.root
        GUI.RobotRentalApp(root, self.conn, self.is_admin)
        root.mainloop()


    def refresh(self, id):
        cur = self.conn.cursor()

        cur.execute("SELECT  Customers.first_name, Customers.last_name, Customers.email, Customers.telephone,"
                    " Models.name, Reservations.start_date, Reservations.end_date, Reservations.payment_status,"
                    " (julianday(Reservations.end_date) - julianday(Reservations.start_date))*Availability.price as Price, Reservations.id FROM Customers"
                    " INNER JOIN Reservations ON Reservations.customer_id = Customers.id"
                    " INNER JOIN Robots ON Reservations.robot_id = Robots.id"
                    " INNER JOIN Models ON Robots.model_id = Models.id"
                    " INNER JOIN Availability ON Robots.id = Availability.robot_id")
        self.res = cur.fetchall()

        res_options = [f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]} zł| :{r[9]}" for r in self.res]
        self.res_var.set(res_options[id] if res_options else "Brak Rezerwacji")
        menu = self.res_menu["menu"]
        menu.delete(0, "end")
        for option in res_options:
            menu.add_command(label=option, command=lambda value=option: self.res_var.set(value))


    def setpaid(self):

        idx=0
        for i in self.res:
            idx=idx+1
            if i[0]==int(self.res_var.get().split(":")[1]):
                break
        idx = idx - 1


        id=self.res_var.get().split(":")[1]
        db.execute(self.conn, "UPDATE Reservations SET payment_status='Paid' WHERE id="+id)

        self.refresh(idx)

    def setfailed(self):

        idx = 0
        for i in self.res:
            idx = idx + 1
            if i[0] == int(self.res_var.get().split(":")[1]):
                break
        idx = idx - 1

        id = self.res_var.get().split(":")[1]
        db.execute(self.conn, "UPDATE Reservations SET payment_status='Failed' WHERE id=" + id)

        self.refresh(idx)
    
    def deleteReservation(self):
    # Pobranie ID wybranej rezerwacji z menu rozwijanego
        selected_reservation = self.res_var.get()
        if not selected_reservation:
            messagebox.showerror("Błąd", "Nie wybrano żadnej rezerwacji.")
            return

        # Wyodrębnienie ID rezerwacji
        reservation_id = selected_reservation.split(":")[1]

        # Pobranie ID robota powiązanego z rezerwacją
        cur = self.conn.cursor()
        cur.execute(
            "SELECT robot_id FROM Reservations WHERE id = ?", (reservation_id,)
        )
        robot_id_row = cur.fetchone()

        if not robot_id_row:
            messagebox.showerror("Błąd", "Nie udało się pobrać ID robota dla rezerwacji.")
            return

        robot_id = robot_id_row[0]

        # Rozpoczęcie transakcji: aktualizacja tabeli Availability i usunięcie rezerwacji
        try:
            # Aktualizacja statusu robota na "Available" (dostępny)
            cur.execute(
                "UPDATE Availability SET status = 'Available' WHERE robot_id = ?", (robot_id,)
            )
            # Usunięcie rezerwacji z tabeli Reservations
            cur.execute(
                "DELETE FROM Reservations WHERE id = ?", (reservation_id,)
            )
            self.conn.commit()  # Zatwierdzenie zmian w bazie danych
            messagebox.showinfo("Sukces", "Rezerwacja została usunięta, a robot jest ponownie dostępny.")
        except Exception as e:
            self.conn.rollback()  # Cofnięcie transakcji w przypadku błędu
            messagebox.showerror("Błąd", f"Nie udało się usunąć rezerwacji: {e}")
            return

        # Odświeżenie menu rozwijanego, aby odzwierciedlić zmiany
        self.refresh(0)


        