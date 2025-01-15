import streamlit as st
import psycopg2
from transformers import pipeline

# PostgreSQL connection details from Streamlit secrets
db_host = st.secrets["DB_HOST"]
db_name = st.secrets["DB_NAME"]
db_user = st.secrets["DB_USER"]
db_password = st.secrets["DB_PASSWORD"]

# Hugging Face API key from Streamlit secrets
huggingface_api_key = st.secrets["HUGGINGFACE_API_KEY"]

# Function to connect to PostgreSQL
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
        st.error(f"Error connecting to PostgreSQL: {e}")
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
        st.error(f"Error executing query: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# Function to analyze the query using Hugging Face Mixtral model
def analyze_query_with_mixtral(query):
    try:
        # Load Hugging Face pipeline with Mixtral model
        mixtral_model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
        analyzer = pipeline("text2text-generation", model=mixtral_model, use_auth_token=huggingface_api_key)
        explanation = analyzer(f"Analyze and explain the following SQL query:\n\n{query}")
        return explanation[0]['generated_text']
    except Exception as e:
        st.error(f"Error with Hugging Face model: {e}")
        return None

# Streamlit app
def main():
    st.title("AI-Driven SQL Query Analyzer")
    st.write("Analyze your SQL queries and get results with detailed explanations using AI.")

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
