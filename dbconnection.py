import os
import sys
import pandas as pd
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine
import json

nv_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
load_dotenv(dotenv_path=nv_path)

class dbactivities:
    def __init__(self):
        self.host = os.environ['HOST'] 
        self.port = os.environ['PORT']
        self.database = os.environ['DB']
        self.username = os.environ['USER']
        self.password = os.environ['PASSWORD']
        try:
            connection_string = f'mysql+pymysql://{self.username}:{self.password}@{self.host}/{self.database}'

            self.engine = create_engine(connection_string)
            print(f'Connection String :: {connection_string}')
        except Exception as e:
            print(f'Unable to establish a connection because of the below reason\n{e}')
            sys.exit(1)
        self.tables = []
        self.columns = []
        self.datatypes = []
        


    def get_databases(self):
        query = """
        SELECT SCHEMA_NAME
        FROM INFORMATION_SCHEMA.SCHEMATA
        WHERE SCHEMA_NAME NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys');
        """
        with self.engine.connect() as connection:
            result = connection.execute(query)
            dbs = [row['SCHEMA_NAME'] for row in result]
        print(dbs)
        return dbs
    
    def switch_db(self,db):
        self.database = db
        try:
            connection_string = f'mysql+pymysql://{self.username}:{self.password}@{self.host}/{self.database}'

            # Create the SQLAlchemy engine
            self.engine = create_engine(connection_string, pool_pre_ping=True)
            print(f'Connection String :: {connection_string}')
        except Exception as e:
            print(f'Unable to establish a connection because of the below reason\n{e}')
            sys.exit(1)

    def get_tables(self,database):
        # SQL query to fetch all table names from the database
        query = f"""
        SELECT TABLE_NAME, TABLE_ROWS, ENGINE, TABLE_COMMENT
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = '{database}' AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME;

        """
        # Execute the query using the engine
        with self.engine.connect() as connection:
            result = connection.execute(query)


            # dbtables = [f'{row[0]}.{row[1]}.{row[2]}' for row in result if 'BASE TABLE'==row[3]] # fetch all the tables
            dbtables = [f'{row[0]}.{row[1]}.{row[2]}' for row in result if ''==row[3]]
            self.tables = dbtables 
        print("**********************************")
        print(dbtables)
        print("**********************************")

        return dbtables 

 
    

    def get_columns(self, table):
        query = f"""
            SELECT TABLE_NAME,COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            where TABLE_NAME='{table}'
        """
        df=pd.read_sql_query(query,self.engine)
        tblcolumns = df['COLUMN_NAME'].values # fetch all the columns
        tbltype = df['DATA_TYPE'].values
        self.columns = tblcolumns
        self.datatypes = tbltype
        return tblcolumns, tbltype
    
    def query_outputs(self, query):
        df = pd.read_sql(query, self.engine)
        def is_overflow(value):
            try:
                json.dumps(value)
                return False
            except:
                return True
        def convert_overflow_values(df):
            for col in df.columns:
                for i in df.index:
                    if is_overflow(df.loc[i, col]):
                        df.loc[i, col] = str(df.loc[i, col])
        convert_overflow_values(df)
        return df.to_json(date_format='iso') #default_handler=str
    

    def index(self):
        json_data = {}
        tables = self.get_tables(self.database)
        databases = self.get_databases()
        for table in tables:
            schema = table.split('.')[2]
            table = table.split('.')[0]
            columns, datatypes = self.get_columns(table)
            json_data[table] = []
            json_data[table].append({'schema':schema, 'name':','.join(columns),'dtypes':','.join(datatypes),'selected':True})
        print(json_data)
        return json_data