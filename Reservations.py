import tkinter
import tkinter as tk
from tkinter import messagebox
import tkcalendar as tkcal
import datetime
import dbbasic as db


class ReservationsWindow:
    def __init__(self, root, conn, is_admin):
        self.conn = conn
        self.root = root
        self.is_admin = is_admin
        self.root.title("Rezerwacjami")

        # zmiana wielkosci okna
        self.root.geometry("750x600")
        for widget in self.root.winfo_children():
            widget.destroy()

        self.create_widgets()

    def create_widgets(self):
        cur = self.conn.cursor()

        cur.execute("SELECT  Customers.first_name, Customers.last_name, Customers.email, Customers.telephone,"
    " Models.name, Reservations.start_date, Reservations.end_date, Reservations.payment_status,"
    " (julianday(Reservations.end_date) - julianday(Reservations.start_date))*Availability.price as Price FROM Customers"
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
        res_options = [f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]} |" for r in self.res]
        self.res_menu=tk.OptionMenu(self.root, self.res_var, *res_options)
        self.res_menu.place(x=30,y=50)



    #Cofnięcie się do głównego menu
    def back(self):
        import GUI
        for widget in self.root.winfo_children():
            widget.destroy()
        root=self.root
        GUI.RobotRentalApp(root, self.conn, self.is_admin)
        root.mainloop()

