import sqlite3

# Establish a connection to the database
connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# Create the 'notices' table
# This table will store the ID, title, and filename of each notice
cursor.execute('''
    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        filename TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create the 'users' table for admin login
# For this example, we'll insert a default admin user.
# In a real-world application, use a more secure password hashing method.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Create the 'gallery' table for storing gallery images
cursor.execute('''
    CREATE TABLE IF NOT EXISTS gallery (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        filename TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Check if the admin user already exists before inserting
cursor.execute("SELECT * FROM users WHERE username = ?", ('admin',))
if cursor.fetchone() is None:
    # IMPORTANT: In a production environment, you MUST hash passwords.
    # Example: from werkzeug.security import generate_password_hash
    # hashed_pw = generate_password_hash('admin_password', method='pbkdf2:sha256')
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'password')) # Use a strong password!

# Commit changes and close the connection
connection.commit()
connection.close()

print("Database initialized successfully with 'notices' and 'users' tables.")
print("Default admin user created with username: 'admin' and password: 'password'")
