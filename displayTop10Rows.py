# displayTop10Rows.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:UPITTdb73@localhost/archeological_db'  # Update with your MySQL credentials
db = SQLAlchemy(app)

def get_table_names():
    with app.app_context():
        result = db.session.execute(text("SHOW TABLES"))
        table_names = [row[0] for row in result.fetchall()]
        return table_names

def display_top_10_rows():
    with app.app_context():  # Ensure that we are within the Flask application context
        table_names = get_table_names()
        #table_names = {'database1'}
        if table_names:
            print("Tables present in the database:")
            for table_name in table_names:
                query = f"SELECT * FROM `{table_name}` LIMIT 10"
                result = db.session.execute(text(query))

                # Convert the result to a Pandas DataFrame for easy printing
                df = pd.DataFrame(result.fetchall(), columns=result.keys())

                print(f"Top 10 rows of {table_name} table:")
                print(df)
                print("\n" + "=" * 50 + "\n")
        else:
            print("No tables found in the database.")

if __name__ == '__main__':
    display_top_10_rows()