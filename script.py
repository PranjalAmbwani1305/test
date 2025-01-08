import openai
import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import os

# Accessing secrets from Streamlit's secrets management
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

host = st.secrets["postgresql"]["host"]
port = st.secrets["postgresql"]["port"]
user = st.secrets["postgresql"]["user"]
password = st.secrets["postgresql"]["password"]
dbname = st.secrets["postgresql"]["dbname"]

# Set API keys
openai.api_key = OPENAI_API_KEY

# Correct connection string for SQLAlchemy
connection_string = f'postgresql://{user}:{password}@{host}:{port}/{dbname}'

# Create SQLAlchemy engine
engine = create_engine(connection_string)

# Streamlit input and output
st.title("AI-Driven SQL Query Analyzer")

# Text input for SQL query
sql_query = st.text_area("Enter your SQL Query", "SELECT * FROM your_table LIMIT 10;")

# Function to load data from the database
def load_data(query):
    try:
        # Using SQLAlchemy engine to load data into pandas dataframe
        df = pd.read_sql(query, engine)

        # Convert the dataframe to a list of dictionaries for processing
        documents = df.to_dict(orient="records")  # List of records (dictionaries)

        # Convert documents into vectors using OpenAI's embedding API
        vectors = []
        for doc in documents:
            text = str(doc)  # You can customize the text representation here
            embedding = openai.Embedding.create(input=text, model="text-embedding-ada-002")["data"][0]["embedding"]
            vectors.append((str(doc), embedding))  # Use document ID or another unique identifier

        # You should be initializing the Pinecone index here to upsert vectors
        # index.upsert(vectors)

        return vectors  # Return vectors instead of Pinecone index for now

    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        return None

# Function to query the index (for now, just using OpenAI's embeddings)
def query_llm(query: str, vectors):
    if vectors is None:
        return "No index found, cannot perform query."
    
    try:
        # Convert the query into a vector using OpenAI's embedding API
        embedding = openai.Embedding.create(input=query, model="text-embedding-ada-002")["data"][0]["embedding"]

        # Process the result (for now just returning a placeholder result)
        return "Results of the query (currently dummy result)"
    
    except Exception as e:
        st.error(f"An error occurred during query: {e}")
        return "An error occurred during query."

# Button to trigger loading of data and querying
if st.button("Analyze Data"):
    vectors = load_data(sql_query)

    if vectors:
        query_result = query_llm("What are the key insights from the data?", vectors)
        st.subheader("Query Result")
        st.write(query_result)
    else:
        st.error("Failed to load data. Cannot perform query.")
