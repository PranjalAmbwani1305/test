import psycopg2
from transformers import pipeline
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

# Load Hugging Face API key (optional if you're using a private model)
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY", "your_api_key_here")

# PostgreSQL connection details
db_host = 'localhost'
db_name = 'postgres'
db_user = 'postgres'
db_password = '12345'

# Connect to PostgreSQL
def connect_to_postgresql():
    try:
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

# Function to execute SQL query in PostgreSQL
def execute_sql_query(query):
    conn = connect_to_postgresql()
    if conn is None:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()
        return results
    except Exception as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# Function to analyze the query using Mixtral from Hugging Face
def analyze_query_with_mixtral(query):
    try:
        # Load the Mixtral model from Hugging Face
        mixtral_model = "mistralai/Mixtral-8x7B-Instruct-v0.1"  # Replace with actual model ID if needed
        analyzer = pipeline("text2text-generation", model=mixtral_model, use_auth_token=huggingface_api_key)

        # Generate the analysis for the SQL query
        explanation = analyzer(f"Analyze and explain the following SQL query:\n\n{query}")
        
        return explanation[0]['generated_text']
    
    except Exception as e:
        print(f"Error with Hugging Face model: {e}")
        return None

# Main function to process SQL query
def process_sql_query(query):
    print(f"Executing Query: {query}")
    result = execute_sql_query(query)
    if result is not None:
        print("Query Result:", result)
    
    explanation = analyze_query_with_mixtral(query)
    if explanation:
        print("Mixtral Analysis:", explanation)

if __name__ == "__main__":
    query = input("Enter SQL query for analysis: ")
    process_sql_query(query)
