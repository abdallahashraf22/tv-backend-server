import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import create_engine



load_dotenv()

host = os.getenv("HOST")
database = os.getenv("DATABASE")
password = os.getenv("MYSQL_PASSWORD")
user = os.getenv("MYSQL_USERNAME")

connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"

engine = create_engine(connection_string)
