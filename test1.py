import sqlite3
import bcrypt

# Connect to the database
DATA_BASE = "data_base.db"
conn = sqlite3.connect(DATA_BASE)
cur = conn.cursor()

# Hash the admin password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Admin user details
admin_user = {
    "login": "admin",
    "email": "BenDover@example.com",
    "first_name": "Ben",
    "last_name": "Dover",
    "password_hash": hash_password("admin"),
    "role": "admin",
}

# Insert the admin user into the Users table
cur.execute(
    """
    INSERT INTO Users (login, email, first_name, last_name, password_hash, role)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        admin_user["login"],
        admin_user["email"],
        admin_user["first_name"],
        admin_user["last_name"],
        admin_user["password_hash"],
        admin_user["role"],
    ),
)
print("Admin user added successfully.")

# Commit changes and close the connection
conn.commit()
conn.close()
