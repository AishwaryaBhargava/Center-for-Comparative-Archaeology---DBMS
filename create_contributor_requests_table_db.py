# create_and_show_tables.py

from sqlalchemy import create_engine, inspect, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Define your models
Base = declarative_base()

class Contributor(Base):
    __tablename__ = 'contributor'

    id = Column(Integer, primary_key=True)
    email = Column(String(120), nullable=False, unique=False)
    contributional_dataset_name = Column(String(500), nullable=False)
    requests = relationship('Request', backref='contributor', lazy=True)

class Request(Base):
    __tablename__ = 'request'

    id = Column(Integer, primary_key=True)
    contributor_id = Column(Integer, ForeignKey('contributor.id'), nullable=False)
    file_path = Column(String(255), nullable=False)
    status = Column(String(20), default='pending', nullable=False)

# Create the tables
database_uri = 'mysql+mysqlconnector://root:UPITTdb73@localhost/archeological_db'
engine = create_engine(database_uri)
Base.metadata.create_all(engine)

# Show existing tables
inspector = inspect(engine)
tables = inspector.get_table_names()

# Print the table names and schema
print("Existing tables:")
for table_name in tables:
    print(f"\nTable: {table_name}")
    for column in inspector.get_columns(table_name):
        print(f"Column: {column['name']}, Type: {column['type']}")
