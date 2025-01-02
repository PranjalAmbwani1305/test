
import openai
from sqlalchemy import create_engine
from llama_index.readers.database import SQLReader
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

openai.api_key = OPENAI_API_KEY

def load_data(query):
    try:
        db_connection = create_engine(DATABASE_URL)
        reader = SQLReader(
            sqlalchemy_engine=db_connection,
            query=query
        )
        documents = reader.load_data()
        index = VectorStoreIndex.from_documents(documents)
        return index
    except Exception as e:
        print(f"An error occurred during data loading: {e}")
        return None

def query_llm(query: str, index):
    if index is None:
        return "No index found, cannot perform query."
    try:
        response = index.query(query)
        return response
    except Exception as e:
        print(f"An error occurred during query: {e}")
        return "An error occurred during query."

if __name__ == "__main__":
    sql_query = "SELECT * FROM your_table LIMIT 10;"
    index = load_data(sql_query)

    if index:
        query_result = query_llm("What are the key insights from the data?", index)
        print(query_result)
    else:
        print("Failed to load data and create index. Cannot perform query.")
