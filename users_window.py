import tkinter
import tkinter as tk
from tkinter import messagebox
import dbbasic as db

'''
Moduł users_window.py odpowiada za przełączanie między
menu głównym, a menu zarządzania kontami użytkowników
'''

class UsersWindow:
    def __init__(self, root, conn, is_admin):
        self.conn = conn
        self.root = root
        self.is_admin = is_admin
        self.root.title("Zarządzaj użytkownikami")

        # zmiana wielkosci okna
        self.root.geometry("600x600")
        for widget in self.root.winfo_children():
            widget.destroy()

        self.create_widgets()

    def create_widgets(self):
        cur = self.conn.cursor()

        cur.execute("SELECT id, first_name, last_name, role FROM users")
        self.users = cur.fetchall()

        if not self.users:
            messagebox.showinfo("Zarządzaj użytkownikami", "Brak użytkowników")
            self.back()
            return

        back_button = tk.Button(self.root, text="Wróć", command=self.back)
        back_button.pack(pady=5)

        tk.Label(self.root, text="Użytkownicy: ").pack(pady=5)
        self.users_var = tk.StringVar(self.root)
        users_options = [f"{r[0]}: {r[1]} {r[2]} | Uprawnienia: {r[3]}" for r in self.users]
        self.users_menu=tk.OptionMenu(self.root, self.users_var, *users_options)
        self.users_menu.pack(pady=5)

        user_button = tk.Button(self.root, text="Nadaj uprawnienia użytkownika", command=self.setuser)
        user_button.pack(pady=5)

        admin_button = tk.Button(self.root, text="Nadaj uprawnienia administratora", command=self.setadmin)
        admin_button.pack(pady=5)

        del_button = tk.Button(self.root, text="Usuń użytkownika", command=self.delete)
        del_button.pack(pady=10)

    #Cofnięcie się do głównego menu
    def back(self):
        import GUI
        for widget in self.root.winfo_children():
            widget.destroy()
        root=self.root
        GUI.RobotRentalApp(root, self.conn, self.is_admin)
        root.mainloop()

    #nadanie praw użytkownika
    def setuser(self):
        id=0
        for i in self.users:
            id=id+1
            if i[0]==int(self.users_var.get().split(":")[0]):
                break;
        id = id - 1

        db.execute(self.conn, "UPDATE users SET role = 'user' WHERE "
                              "id =" +str(self.users_var.get().split(":")[0])+" ")
        self.refresh(id)

    def setadmin(self):
        id = 0
        for i in self.users:
            id = id + 1
            if i[0] == int(self.users_var.get().split(":")[0]):
                break;
        id = id - 1
        db.execute(self.conn, "UPDATE users SET role = 'admin' WHERE "
                              "id =" + str(self.users_var.get().split(":")[0]) + " ")
        self.refresh(id)

    def delete(self):
        id = 0
        for i in self.users:
            id = id + 1
            if i[0] == int(self.users_var.get().split(":")[0]):
                break;

        id=id-2

        try:
            users_options = [f"{r[0]}: {r[1]} {r[2]} | Uprawnienia: {r[3]}" for r in self.users]
            x = users_options[id]
        except TypeError:
            id=0
        print(id)
        if(tkinter.messagebox.askokcancel(title="Usuwanie użytkownika", message = "Czy na pewno"
            " chcesz usunąć użytkownika "+str(self.users_var.get().split("|")[0])+" ?")):
            print("usuwam")
        else:
            print("nie usuwam")
        db.execute(self.conn, "DELETE FROM users WHERE "
                              "id =" + str(self.users_var.get().split(":")[0]) + " ")
        self.refresh(id)


    def refresh(self,id):
        cur = self.conn.cursor()
        cur.execute("SELECT id, first_name, last_name, role FROM users")
        self.users = cur.fetchall()

        users_options = [f"{r[0]}: {r[1]} {r[2]} | Uprawnienia: {r[3]}" for r in self.users]
        self.users_var.set(users_options[id] if users_options else "Brak użytkowników")
        menu = self.users_menu["menu"]
        menu.delete(0, "end")
        for option in users_options:
            menu.add_command(label=option, command=lambda value=option: self.users_var.set(value))