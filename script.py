import streamlit as st
import psycopg2
from transformers import pipeline

# PostgreSQL connection details
DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "12345"

# Connect to PostgreSQL
def connect_to_postgresql():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to PostgreSQL: {e}")
        return None

# Execute SQL query in PostgreSQL
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
        st.error(f"Error executing query: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# Analyze SQL query using Mixtral
def analyze_query_with_mixtral(query):
    try:
        # Get the Hugging Face API key from Streamlit secrets
        huggingface_api_key = st.secrets["api_keys"]["huggingface"]
        mixtral_model = "mistralai/Mixtral-8x7B-Instruct-v0.1"  # Replace with actual model ID if needed
        analyzer = pipeline("text2text-generation", model=mixtral_model, use_auth_token=huggingface_api_key)
        explanation = analyzer(f"Analyze and explain the following SQL query:\n\n{query}")
        return explanation[0]['generated_text']
    except Exception as e:
        st.error(f"Error with Hugging Face model: {e}")
        return None

# Streamlit App
def main():
    st.title("AI-Driven SQL Query Analyzer")
    st.write("Enter an SQL query to execute and analyze.")

    # Input for SQL query
    query = st.text_area("SQL Query", placeholder="Write your SQL query here...")

    if st.button("Analyze Query"):
        if not query.strip():
            st.warning("Please enter a valid SQL query.")
        else:
            # Execute query
            st.subheader("Execution Results")
            results = execute_sql_query(query)
            if results:
                st.write(results)
            else:
                st.write("No results returned or query failed.")

            # Analyze query
            st.subheader("Query Analysis")
            explanation = analyze_query_with_mixtral(query)
            if explanation:
                st.success("Query Analysis Completed:")
                st.write(explanation)

if __name__ == "__main__":
    main()
