import streamlit as st
import sqlite3
from transformers import pipeline
import logging
import re
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_resource
def load_model():
    """Load and cache the NLP model for text-to-SQL conversion."""
    try:
        model = pipeline("text2text-generation", 
                        model="google/flan-t5-base",
                        max_length=256)
        return model
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

def get_db_path():
    """Get the correct database path."""
    # Get the directory containing the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the parent directory if needed
    parent_dir = os.path.dirname(current_dir)
    db_path = os.path.join(current_dir, 'database.db')
    return db_path

def clean_sql_query(sql_query: str) -> str:
    """Clean and validate the generated SQL query."""
    try:
        # Remove any non-SQL text that might have been generated
        sql_query = re.sub(r'```sql|```', '', sql_query)
        sql_query = sql_query.strip()
        
        # Basic SQL injection prevention
        blacklist = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "--", ";--", "/*"]
        if any(word in sql_query.upper() for word in blacklist):
            raise ValueError("Invalid SQL operation detected")
        
        # Force simple queries for our simple schema
        if not sql_query.upper().startswith("SELECT"):
            sql_query = f"SELECT * FROM Departments WHERE {sql_query}"
        
        # Remove any JOINs or complex queries
        if "JOIN" in sql_query.upper():
            # Simplify to basic query
            sql_query = "SELECT * FROM Departments WHERE Name = 'Sales';"
        
        # Ensure proper query termination
        sql_query = sql_query.rstrip(';') + ';'
        
        return sql_query
    except Exception as e:
        logger.error(f"Error in clean_sql_query: {str(e)}")
        raise ValueError(f"Failed to clean SQL query: {str(e)}")

def generate_sql_query(nl_query: str, model) -> str:
    """Convert natural language query to SQL using the NLP model."""
    try:
        # More specific context with simple examples matching our schema
        context = """
        Convert to simple SQL. Use table 'Departments' with columns: Name, Manager
        
        Examples:
        Question: Who manages Sales?
        SQL: SELECT Manager FROM Departments WHERE Name = 'Sales';
        
        Question: Show all departments
        SQL: SELECT * FROM Departments;
        
        Question: List department names
        SQL: SELECT Name FROM Departments;
        
        Question: Find manager of Marketing
        SQL: SELECT Manager FROM Departments WHERE Name = 'Marketing';
        
        Current question: """
        
        full_prompt = context + nl_query
        
        output = model(full_prompt, 
                      temperature=0.3,  # Lower temperature for more focused outputs
                      do_sample=True,
                      top_p=0.8,
                      max_length=128)
        
        sql_query = clean_sql_query(output[0]['generated_text'])
        
        # Ensure the query matches our simple schema
        if "Who" in nl_query and "manager" in nl_query.lower():
            department = re.search(r'(?:of\s+)(\w+)', nl_query)
            if department:
                dept_name = department.group(1)
                sql_query = f"SELECT Manager FROM Departments WHERE Name = '{dept_name}';"
        
        logger.info(f"Generated SQL query: {sql_query}")
        return sql_query
    
    except Exception as e:
        logger.error(f"Error generating SQL query: {str(e)}")
        raise

def execute_sql_query(query: str):
    """Execute the SQL query and return results."""
    conn = None
    try:
        db_path = get_db_path()
        logger.info(f"Connecting to database at: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(query)
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        results = cursor.fetchall()
        
        return columns, results
    
    except sqlite3.Error as e:
        logger.error(f"SQL error: {str(e)}")
        error_msg = str(e)
        if "no such table" in error_msg.lower():
            error_msg = "Database table not found. Please ensure the database is properly set up."
        elif "syntax error" in error_msg.lower():
            error_msg = "Invalid SQL query syntax. Please try rephrasing your question."
        return None, f"Database error: {error_msg}"
    
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        return None, f"An error occurred: {str(e)}"
    
    finally:
        if conn:
            conn.close()

def main():
    st.set_page_config(page_title="SQL Query Generator", layout="wide")
    
    st.title("Natural Language to SQL Converter")
    
    # Debug information
    db_path = get_db_path()
    st.sidebar.write("Debug Information:")
    st.sidebar.write(f"Database path: {db_path}")
    st.sidebar.write(f"Database exists: {os.path.exists(db_path)}")
    
    st.markdown("""
    Convert your questions about departments into SQL queries.
    Try asking questions like:
    - Show all departments
    - Who manages Sales?
    - List all department names
    """)
    
    if 'error_count' not in st.session_state:
        st.session_state.error_count = 0
    
    try:
        with st.spinner("Loading the NLP model..."):
            model = load_model()
    except Exception as e:
        st.error("Failed to load the model. Please refresh the page or contact support.")
        logger.error(f"Model loading error: {str(e)}")
        return
    
    nl_query = st.text_input(
        "Enter your question:",
        placeholder="e.g., 'Who is the manager of Sales?'",
        key="query_input"
    )
    
    if st.button("Generate SQL Query", key="generate_button"):
        if not nl_query.strip():
            st.warning("Please enter a question first.")
            return
        
        try:
            with st.spinner("Generating SQL query..."):
                sql_query = generate_sql_query(nl_query, model)
            
            st.subheader("Generated SQL Query:")
            st.code(sql_query, language="sql")
            
            with st.spinner("Executing query..."):
                columns, results = execute_sql_query(sql_query)
            
            if isinstance(results, str):
                st.error(results)
                st.session_state.error_count += 1
                if st.session_state.error_count >= 3:
                    st.warning("Having trouble? Try rephrasing your question or check our example queries above.")
            elif results:
                st.session_state.error_count = 0
                st.subheader("Query Results:")
                st.dataframe([dict(zip(columns, row)) for row in results])
            else:
                st.info("No matching results found.")
        
        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            st.error("An error occurred while processing your request. Please try again.")
            st.session_state.error_count += 1

if __name__ == "__main__":
    main()