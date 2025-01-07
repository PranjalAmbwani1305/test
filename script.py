import openai
import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import os

# Accessing secrets from Streamlit's secrets management
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
DATABASE_URL = st.secrets["DATABASE_URL"]


# Set API keys
openai.api_key = OPENAI_API_KEY

connection_string = f'postgresql://postgrea:12345@10.12.32.71:5432/silver_data'

# Create engine
engine = create_engine(connection_string)


# Streamlit input and output
st.title("AI-Driven SQL Query Analyzer")

# Text input for SQL query
sql_query = st.text_area("Enter your SQL Query", "SELECT * FROM your_table LIMIT 10;")

# Function to load data and index it into Pinecone
def load_data(query):
    try:
        # Create an engine and load data using pandas
        db_connection = create_engine(DATABASE_URL)
        df = pd.read_sql(query, db_connection)

        # Convert the dataframe to a list of dictionaries for processing
        documents = df.to_dict(orient="records")  # List of records (dictionaries)

        
        # Convert documents into vectors using OpenAI's embedding API (example)
        vectors = []
        for doc in documents:
            text = str(doc)  # You can customize the text representation here
            embedding = openai.Embedding.create(input=text, model="text-embedding-ada-002")["data"][0]["embedding"]
            vectors.append((str(doc), embedding))  # Use document ID or another unique identifier

        # Upsert vectors into Pinecone
        index.upsert(vectors)

        return index

    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        return None

# Function to query the index with a given query
def query_llm(query: str, index):
    if index is None:
        return "No index found, cannot perform query."
    try:
        # Convert the query into a vector using OpenAI's embedding API
        embedding = openai.Embedding.create(input=query, model="text-embedding-ada-002")["data"][0]["embedding"]

    

        # Process the result
        return result

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
