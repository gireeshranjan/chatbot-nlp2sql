import sqlite3
import os

def setup_database():
    try:
        # Get the current directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, 'database.db')
        
        print(f"Creating database at: {db_path}")
        
        # Remove existing database if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # Connect to database (creates it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create Departments table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Departments (
            Name TEXT PRIMARY KEY,
            Manager TEXT NOT NULL
        )''')

        # Insert sample data
        sample_data = [
            ('Sales', 'John Smith'),
            ('Marketing', 'Jane Doe'),
            ('Engineering', 'Bob Wilson'),
            ('HR', 'Sarah Johnson'),
            ('Finance', 'Mike Brown')
        ]

        # Insert the sample data
        cursor.executemany('INSERT OR REPLACE INTO Departments (Name, Manager) VALUES (?, ?)', sample_data)

        # Commit changes and close connection
        conn.commit()
        conn.close()
        print("Database created successfully with sample data!")
        
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        raise

if __name__ == "__main__":
    setup_database()