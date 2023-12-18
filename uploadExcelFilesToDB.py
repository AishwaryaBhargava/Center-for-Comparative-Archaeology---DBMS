# upload.py
import os
import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:UPITTdb73@localhost/archeological_db'  # Update with your MySQL credentials
db = SQLAlchemy(app)

class ExcelTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(255), unique=True, nullable=False)

def upload_excel_to_mysql(file_path):
    table_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"Uploading {file_path} to table {table_name}...")

    # Check if the table already exists
    existing_table = ExcelTable.query.filter_by(table_name=table_name).first()
    
    if existing_table:
        # Drop the existing table
        db.session.execute(f"DROP TABLE {table_name}")
        db.session.commit()
        print(f"Existing table {table_name} dropped.")

    # Read the Excel file and upload data to the database
    df = pd.read_excel(file_path)
    
    # Use if_exists parameter to replace the table if it exists
    df.to_sql(table_name, db.engine, index=False, if_exists='replace')
    
    print(f"Upload successful for {file_path} to table {table_name}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        for file in os.listdir('upload'):
            if file.endswith('.xlsx'):
                upload_excel_to_mysql(os.path.join('upload', file))

        # Check if tables are created successfully
        existing_tables = db.session.query(ExcelTable).all()
        print("Existing tables in the database:")
        for table in existing_tables:
            print(f"- {table.table_name}")
