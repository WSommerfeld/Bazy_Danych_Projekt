import tkinter as tk
from tkinter import messagebox
import dbbasic as db
import GUI
from login_screen import LoginScreen
from GUI import RobotRentalApp
import entry
import threading

DATA_BASE = "test7.db"

def main():
    db.DataBaseInit(DATA_BASE)

    GUI.start_gui()
    entry.Entry()

if __name__ == "__main__":
    recovery = input("Czy chcesz przywrócić bazę danych z backupu? (tak/nie): ")
    if recovery.lower() == "tak":
        db.disaster_recovery("test7.db")
    else:
        # Uruchomienie wątku backupów
        threading.Thread(target=db.backup_scheduler, args=("test7.db",), daemon=True).start()
        main()