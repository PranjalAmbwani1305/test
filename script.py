import openai
import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import pinecone
import os

# Accessing secrets from Streamlit's secrets management
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
DATABASE_URL = st.secrets["DATABASE_URL"]
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
PINECONE_ENV = st.secrets["PINECONE_ENV"]

# Set API keys
openai.api_key = OPENAI_API_KEY

# Initialize Pinecone environment
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

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

        # Create a Pinecone index (if not already created)
        index_name = "your_index_name"
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(index_name, dimension=1536, metric="cosine")  # Adjust dimensions as needed

        # Connect to the index
        index = pinecone.Index(index_name)

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

        # Query Pinecone for similar vectors
        result = index.query(queries=[embedding], top_k=5, include_metadata=True)

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
