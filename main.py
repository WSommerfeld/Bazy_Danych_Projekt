import entry
import dbbasic as db
import threading

def main():

    entry.entry()

if __name__ == "__main__":

    recovery = input("Czy chcesz przywrócić bazę danych z backupu? (tak/nie): ")
    if recovery.lower() == "tak":
        db.disaster_recovery("test7.db")
    else:
        # Uruchomienie wątku backupów
        threading.Thread(target=db.backup_scheduler, args=("test7.db",), daemon=True).start()

    main()