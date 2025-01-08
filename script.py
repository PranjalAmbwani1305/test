import openai
import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import os
import psycopg2

# Accessing secrets from Streamlit's secrets management
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]


# Set API keys
openai.api_key = OPENAI_API_KEY

# Create the connection string using the credentials
connection_string = f'postgresql://postgres:12345@localhost:5432/silver_data'


# Create SQLAlchemy engine
try:
    engine = create_engine(connection_string)
    # Test connection
    with engine.connect() as conn:
        conn.execute("SELECT 1")  # simple test query
    st.success("Database connection successful!")
except Exception as e:
    st.error(f"Database connection failed: {e}")
    engine = None

# Streamlit input and output
st.title("AI-Driven SQL Query Analyzer")

# Text input for SQL query
sql_query = st.text_area("Enter your SQL Query", "SELECT * FROM your_table LIMIT 10;")

# Function to load data from PostgreSQL database
def load_data(query):
    if engine is None:
        st.error("Database connection is not established.")
        return None

    try:
        # Use SQLAlchemy engine to execute query and load data
        df = pd.read_sql(query, engine)

        # Check if DataFrame is empty
        if df.empty:
            st.warning("Query returned no data.")
            return None

        # Convert the dataframe to a list of dictionaries for processing
        documents = df.to_dict(orient="records")  # List of records (dictionaries)
        st.write(f"Loaded {len(documents)} records.")

        # Convert documents into vectors using OpenAI's embedding API (example)
        vectors = []
        for doc in documents:
            # You can customize the text field(s) used for embedding here
            text = str(doc)  # This is a simple conversion, consider refining it
            embedding = openai.Embedding.create(input=text, model="text-embedding-ada-002")["data"][0]["embedding"]
            vectors.append((str(doc), embedding))  # Use document ID or another unique identifier

        # Return vectors (you can integrate with a vector database like Pinecone here)
        return vectors

    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        return None

# Function to query the index with a given query (optional integration with Pinecone or another service)
def query_llm(query: str, index):
    if index is None:
        return "No index found, cannot perform query."
    
    try:
        # Convert the query into a vector using OpenAI's embedding API
        embedding = openai.Embedding.create(input=query, model="text-embedding-ada-002")["data"][0]["embedding"]
        
        # Placeholder logic for querying your data index
        # This is where you would integrate with your vector database or model to get results
        # For now, we return a mock result
        result = f"Query: {query}\nEmbedding: {embedding[:5]}... (first 5 elements of embedding)"
        
        return result

    except Exception as e:
        st.error(f"An error occurred during query: {e}")
        return "An error occurred during query."

# Button to trigger loading of data and querying
if st.button("Analyze Data"):
    # Load data and generate embeddings
    index = load_data(sql_query)

    if index:
        query_result = query_llm("What are the key insights from the data?", index)
        st.subheader("Query Result")
        st.write(query_result)
    else:
        st.error("Failed to load data and create index. Cannot perform query.")
