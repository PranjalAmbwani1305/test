import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import pinecone

# Accessing secrets from Streamlit's secrets management
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
PINECONE_ENV = st.secrets["PINECONE_ENV"]

# Initialize Pinecone client
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

# Streamlit connection for PostgreSQL
conn = st.experimental_connection("postgresql", type="sql")

# Streamlit input and output
st.title("AI-Driven SQL Query Analyzer")

# Text input for SQL query
sql_query = st.text_area("Enter your SQL Query", "SELECT * FROM your_table LIMIT 10;")

# Placeholder function for generating embeddings
def get_embeddings(doc):
    # Replace this with actual embedding generation logic
    return [0.1] * 768  # Dummy 768-dimensional vector

# Load data and index it in Pinecone
def load_data_and_index(query, conn):
    try:
        # Fetch data from the database
        with conn.session as session:
            df = pd.read_sql(query, session.connection())

        if df.empty:
            st.error("The SQL query returned no data.")
            return None

        # Convert the dataframe to a list of dictionaries
        documents = df.to_dict(orient="records")

        # Create a Pinecone index or connect to an existing one
        index_name = "your-index-name"  # Define your Pinecone index name
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(index_name, dimension=768)  # Assuming 768 for embeddings

        index = pinecone.Index(index_name)

        # Convert documents to embeddings and upsert them
        for i, doc in enumerate(documents):
            embedding = get_embeddings(doc)  # Replace with actual embeddings
            index.upsert([(str(i), embedding, doc)])

        st.success("Data successfully loaded and indexed in Pinecone.")
        return index
    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        return None

# Query Pinecone index
def query_pinecone(query, index):
    try:
        # Generate an embedding for the query
        query_embedding = get_embeddings(query)  # Replace with actual embedding generation logic

        # Perform a similarity search
        result = index.query(query_embedding, top_k=5, include_metadata=True)
        return result
    except Exception as e:
        st.error(f"An error occurred during query: {e}")
        return None

# Button to trigger loading of data and querying
if st.button("Analyze Data"):
    pinecone_index = load_data_and_index(sql_query, conn)

    if pinecone_index:
        query_result = query_pinecone("What are the key insights from the data?", pinecone_index)
        st.subheader("Query Result")
        st.write(query_result)
    else:
        st.error("Failed to load data and create index. Cannot perform query.")
