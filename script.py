import openai
import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
from llama_index import VectorStoreIndex


# Set up the API key and database URL from environment variables
OPENAI_API_KEY = st.secrets("OPENAI_API_KEY")
DATABASE_URL = st.secrets("DATABASE_URL")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

openai.api_key = OPENAI_API_KEY

# Streamlit input and output
st.title("AI-Driven SQL Query Analyzer")

# Text input for SQL query
sql_query = st.text_area("Enter your SQL Query", "SELECT * FROM your_table LIMIT 10;")

def load_data(query):
    try:
        # Create an engine and load data using pandas
        db_connection = create_engine(DATABASE_URL)
        df = pd.read_sql(query, db_connection)
        
        # Convert the dataframe to a list of dictionaries for processing
        documents = df.to_dict(orient="records")  # List of records (dictionaries)
        
        # Create an index from the documents
        index = VectorStoreIndex.from_documents(documents)
        return index
    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        return None

def query_llm(query: str, index):
    if index is None:
        return "No index found, cannot perform query."
    try:
        # Perform the query against the index
        response = index.query(query)
        return response
    except Exception as e:
        st.error(f"An error occurred during query: {e}")
        return "An error occurred during query."

# Button to trigger loading of data and querying
if st.button("Analyze Data"):
    index = load_data(sql_query)

    if index:
        query_result = query_llm("What are the key insights from the data?", index)
        st.subheader("Query Result")
        st.write(query_result)
    else:
        st.error("Failed to load data and create index. Cannot perform query.")

