import tkinter
import tkinter as tk
from tkinter import messagebox
import tkcalendar as tkcal
import datetime
import dbbasic as db


class RentalWindow:
    def __init__(self, root, conn,is_admin):
       
        self.conn = conn
        self.root = root
        self.is_admin = is_admin
        self.root.title("Wypożycz robota")
        #zmiana wielkosci okna
        self.root.geometry("550x600")
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()

    def create_widgets(self):
        cur = self.conn.cursor()
        #zmiany~Lasak
        cur.execute("SELECT Robots.id, Models.name, Models.type FROM Robots"
            " INNER JOIN Models ON Robots.model_id=Models.id"
            " WHERE Robots.id NOT IN (SELECT robot_id FROM Reservations WHERE"
            " '2025-01-01' BETWEEN start_date AND end_date)")
        self.available_robots = cur.fetchall()

        if not self.available_robots:
            messagebox.showinfo("Wypożyczanie robota", "Brak dostępnych robotów.")
            self.back()
            return

        #powrót
        back_button = tk.Button(self.root, text="Wróć", command=self.back)
        back_button.place(x=30, y=20)

        tk.Label(self.root, text="Dostępne roboty:").place(x=30, y=80)
        self.robot_var = tk.StringVar(self.root)
        robot_options = [f"{r[0]}: {r[1]} ({r[2]})" for r in self.available_robots]
        self.robot_menu=tk.OptionMenu(self.root, self.robot_var, *robot_options)
        self.robot_menu.place(x=30, y=120)

        tk.Label(self.root, text="Imię klienta:").place(x=30, y=180)
        self.first_name_entry = tk.Entry(self.root)
        self.first_name_entry.place(x=30, y=220)

        tk.Label(self.root, text="Nazwisko klienta:").place(x=30, y=280)
        self.last_name_entry = tk.Entry(self.root)
        self.last_name_entry.place(x=30, y=320)

        tk.Label(self.root, text="Nr telefonu:").place(x=30, y=380)
        self.phone_entry= tk.Entry(self.root)
        self.phone_entry.place(x=30, y=420)

        tk.Label(self.root, text="Adres email:").place(x=30, y=480)
        self.email_entry= tk.Entry(self.root)
        self.email_entry.place(x=30, y = 520)

        tk.Label(self.root, text="Data wypożyczenia:").place(x=250, y=20)
        self.cal = tkcal.Calendar(self.root, selectmode='day',
                       year=2025, month=1,
                       day=1)

        self.cal.place(x=250, y=50)

        tk.Label(self.root, text="Czas trwania wypożyczenia (dni):").place(x=250, y=280)
        self.rental_duration_entry = tk.Entry(self.root)
        self.rental_duration_entry.place(x=250, y=320)

        date_button = tk.Button(self.root, text="Sprawdź dostępność w zadanym terminie", command=self.datecheck)
        date_button.place(x=250, y=370)

        price_button = tk.Button(self.root, text="Sprawdź cenę", command=self.pricecheck)
        price_button.place(x=320, y=400)



        self.price_label = tk.Label(self.root,text="Cena(PLN): \n 0")
        self.price_label.place(x=330, y=430)



       
        submit_button = tk.Button(self.root, text="Wypożycz", command=self.submit_rental)
        submit_button.place(x=330, y=480)


    def pricecheck(self):
        duration = self.rental_duration_entry.get()
        robot_id = self.robot_var.get().split(":")[0]

        if(robot_id==""):
            return;

        price=0
        try:
            price = db.execute(self.conn,"SELECT PRICE FROM AVAILABILITY WHERE"
                                     " robot_id = "+str(robot_id)+"").fetchone()[0]*int(duration)
        except AttributeError:
            price=0


        price_var = "Cena(PLN): \n" + str(price)
        self.price_label["text"] = price_var

    def datecheck(self):
        cur = self.conn.cursor()
        duration=self.rental_duration_entry.get()
        cur_date=self.cal.get_date()
        cur_date = datetime.datetime.strptime(cur_date, '%m/%d/%y')
        cur_date=datetime.date.strftime(cur_date, "%Y-%m-%d")

        cur.execute("SELECT Robots.id, Models.name, Models.type FROM Robots"
            " INNER JOIN Models ON Robots.model_id=Models.id"
            " WHERE  (Robots.id IN (SELECT robot_id FROM Reservations WHERE "
            " end_date < '"+str(cur_date)+"' OR DATE('"+str(cur_date)+"', '"+str(duration)+" day')<start_date)"
            "OR Robots.id NOT IN (SELECT robot_id FROM Reservations)) AND Robots.id IN"
              " (SELECT robot_id FROM Availability WHERE status = 'Available' AND end_date>DATE('"+str(cur_date)+"', '"+str(duration)+" day') )")
        self.available_robots = cur.fetchall()

        #próba odświeżenia
        robot_options = [f"{r[0]}: {r[1]} ({r[2]})" for r in self.available_robots]
        self.robot_var.set(robot_options[0] if robot_options else "Brak dostępnych robotów")
        menu = self.robot_menu["menu"]
        menu.delete(0, "end")
        for option in robot_options:
            menu.add_command(label=option, command=lambda value=option: self.robot_var.set(value))


    #Cofnięcie się do głównego menu
    def back(self):
        import GUI
        for widget in self.root.winfo_children():
            widget.destroy()
        root=self.root
        GUI.RobotRentalApp(root, self.conn, self.is_admin)
        root.mainloop()

    def submit_rental(self):
        cur = self.conn.cursor()
        robot_id = self.robot_var.get().split(":")[0]
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        phone = self.phone_entry.get()
        email=self.email_entry.get()
        rental_duration = self.rental_duration_entry.get()

        start_date=self.cal.get_date()
        start_date = datetime.datetime.strptime(start_date, '%m/%d/%y')
        start_date=datetime.date.strftime(start_date, "%Y-%m-%d")


        #Walidacja danych
        if not (robot_id and first_name and last_name and rental_duration ):
            messagebox.showerror("Błąd", "Wszystkie pola muszą być wypełnione.")
            return


        #Walidacja imenia i nazwiska
        if not first_name.isalpha() or not last_name.isalpha():
            messagebox.showerror("Błąd", "Imię i nazwisko muszą zawierać tylko litery.")
            return


        # Walidacja ceny - musi być liczbą dodatnią


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
            if(db.execute(self.conn,"SELECT MAX(id) FROM CUSTOMERS WHERE telephone = '"+str(phone)+"'").fetchone()[0]==1):

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
            try:
                reservation_id=db.execute(self.conn,"SELECT MAX(id) FROM RESERVATIONS").fetchone()[0]+1
            except:
                reservation_id=1

            db.execute(self.conn,"INSERT INTO RESERVATIONS"
                       "(id,customer_id,robot_id,payment_status, start_date, end_date) VALUES "
                        "("+str(reservation_id)+","+str(customer_id)+","+str(robot_id)+","
                         " 'Pending', '"+str(start_date)+"', DATE('"+str(start_date)+"', '+"+str(rental_duration)+" day'))")




            messagebox.showinfo("Sukces", "Robot został wypożyczony!")
            #tymczasowy mechanizm powrotu (nie wiem jak lepiej to zrobić)
            #
            self.back()



        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wypożyczyć robota: {e}")
