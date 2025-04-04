# README

## Natural Language to SQL Converter

This project is a Streamlit-based web application that converts natural language queries into SQL statements and executes them on a predefined SQLite database. It utilizes the `google/flan-t5-base` model from Hugging Face for text-to-SQL conversion.

### Features
- Converts natural language queries into SQL queries.
- Executes SQL queries on an SQLite database.
- Provides results in a user-friendly table format.
- Includes safeguards for SQL query validation and error handling.

### Model Used
The project uses the `google/flan-t5-base` model from Hugging Face's Transformers library for converting natural language to SQL queries. This model is pre-trained for various text-to-text generation tasks, making it suitable for generating SQL queries from plain English input.

### Prerequisites
Before running the application, ensure you have the following installed:
- Python 3.8 or higher
- Virtual environment tool (optional but recommended)

### Installation and Setup
1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Set up a virtual environment (optional):**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the SQLite database:**
   Run the `setup_db.py` script to create the `database.db` file and populate it with sample data.
   ```bash
   python setup_db.py
   ```

### How to Run Locally
1. **Start the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

2. **Access the application:**
   Open your web browser and go to `http://localhost:8501`.

3. **Interacting with the application:**
   - Enter a natural language query in the text input field (e.g., "Who manages Sales?").
   - Click on the "Generate SQL Query" button to see the SQL query and its results.

### Example Queries
- Show all departments
- Who manages Sales?
- List all department names

### Project Structure
- **app.py:** Main Streamlit application script.
- **setup_db.py:** Script to set up and initialize the SQLite database.
- **requirements.txt:** Contains all required Python packages.
- **database.db:** SQLite database file (auto-generated by `setup_db.py`).
- **README.md:** Documentation file (this file).

### Troubleshooting
- **Database errors:** Ensure the `database.db` file exists and is in the correct directory.
- **Model loading errors:** Verify your internet connection and ensure the `transformers` library is installed.
- **Memory issues:** Reduce package usage or consider using a larger local system if running out of memory.

### Notes
This application is designed to work with a specific schema (the `Departments` table with `Name` and `Manager` columns). For different schemas, modifications to the code may be required.

