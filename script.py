import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import pinecone

# Accessing secrets from Streamlit's secrets management
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
PINECONE_ENV = st.secrets["PINECONE_ENV"]

conn = st.connection("postgresql", type="sql")

# Initialize Pinecone client using the recommended method
pinecone_client = pinecone.Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

# Streamlit input and output
st.title("AI-Driven SQL Query Analyzer")

# Text input for SQL query
sql_query = st.text_area("Enter your SQL Query", "SELECT * FROM your_table LIMIT 10;")

def load_data(query):
    try:
        # Convert the dataframe to a list of dictionaries for processing
        documents = to_dict(orient="records")  # List of records (dictionaries)

        # Create a Pinecone index or connect to an existing one
        index_name = "your-index-name"  # Define your Pinecone index name
        if index_name not in pinecone_client.list_indexes():
            pinecone_client.create_index(index_name, dimension=768)  # Assuming 768 for embeddings
        index = pinecone_client.Index(index_name)

        # Convert documents to embeddings (this can be done using any model of your choice)
        embeddings = [get_embeddings(doc) for doc in documents]

        # Upsert data into Pinecone index
        for i, embedding in enumerate(embeddings):
            index.upsert([(str(i), embedding)])

        return index
    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        return None

def get_embeddings(doc):
    # This is a placeholder function, replace with actual model embedding logic
    return [0.1] * 768  # Dummy 768-dimensional vector, replace with actual embeddings

def query_pinecone(query: str, index):
    if index is None:
        return "No index found, cannot perform query."
    try:
        # Generate an embedding for the query
        query_embedding = get_embeddings(query)  # You would need to generate this embedding from a model

        # Perform a similarity search against the Pinecone index
        result = index.query([query_embedding], top_k=5, include_values=True)
        return result
    except Exception as e:
        st.error(f"An error occurred during query: {e}")
        return "An error occurred during query."

# Button to trigger loading of data and querying
if st.button("Analyze Data"):
    index = load_data(sql_query)

    if index:
        query_result = query_pinecone("What are the key insights from the data?", index)
        st.subheader("Query Result")
        st.write(query_result)
    else:
        st.error("Failed to load data and create index. Cannot perform query.")
