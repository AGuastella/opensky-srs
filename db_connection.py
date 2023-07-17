import pytest
import pyodbc
import pandas as pd
from utility.query_statement import query as q

server = 'openskysrs.database.windows.net'
database = 'openskydb'
username = 'CloudSA2b425ff0'
password = 'colajanni<3'   
driver= '{ODBC Driver 17 for SQL Server}'

@pytest.mark.parametrize("url", ["https://www.google.com"])
def test_web_connection(url):
    
    with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
           data = pd.read_sql(q.select_active_flights,conn).values.tolist()
    
    if data[0] is not None:
          assert True
    else: 
          assert False


#https://openskyiu.azurewebsites.net/api/index?

