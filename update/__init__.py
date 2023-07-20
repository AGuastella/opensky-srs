import datetime
import logging
import azure.functions as func
import random
import json
import time
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import pyodbc
from utility.italianairspace import italianairspace as it
from utility.query_statement import query as q
import os

server = 'openskysrs.database.windows.net'
database = 'openskydb'
driver= '{ODBC Driver 17 for SQL Server}'

from utility.credential import openskycredential as oc
from utility.italianairspace import italianairspace as it



class none_result(Exception):
    pass

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
            logging.info('The timer is past due!')

    try:
        username=os.getenv('Dbuser')
        password=os.getenv('Dbpass')

        now = int(time.time())

        bbox = it.italian_bbox

        while(True):     
            try:
                print("INIZIO UPDATE")
                # ROTAZIONE CREDENZIALI !!!
                rand = random.randint(0, len(oc.opensky_credential)-1)

                # RICHIESTA CON CREDENZIALI, A ROTAZIONE
                r = requests.get(f'https://opensky-network.org/api/states/all?{bbox}', auth = HTTPBasicAuth(oc.opensky_credential[rand][0], oc.opensky_credential[rand][1]))
                
                # RICHIESTA CON CREDENZIALI SINGOLE
                #r = requests.get('https://opensky-network.org/api/states/all?{bbox}', auth = HTTPBasicAuth('g1g1', 'dkKIskisiKIKI£443'))

                # RICHIESTA SENZA CREDENZIALI
                #r = requests.get('https://opensky-network.org/api/states/all?{bbox}')

                if r is None: 
                    raise none_result
                
                if r.status_code == 200:
                    # Stampa non necessaria per messaggio ottenuto correttamente
                    print(f'{now} - [n°{rand}][{r.status_code}] OK!')
                    break
                elif r.status_code == 429: 
                    print(f'{now} - [n°{rand}][{r.status_code}]{r.text}')

            except none_result:
                print(f'{now} - [n°{rand}][{r.status_code}]{r.text}   !')

            except:
                print(f'{now} - [n°{rand}]ERROR                       !!!')
            
            # In caso si voglia rallentare un po' le domande che vengono inviate in caso di fallimento
            #time.sleep(1)

        result=r.json()
        
        df = pd.DataFrame(result)
        #print(df)
        list_of_lists = df.apply(lambda row: [int(time.time())] + row['states'], axis=1).tolist()

        #on_air = [l for l in list_of_lists if not l[9] and it.is_in_italian_airspace(l[7], l[6])]
        #on_ground = [[l[1]] for l in list_of_lists if l[9] and it.is_in_italian_airspace(l[7], l[6])]
        
        on_air = [l for l in list_of_lists if not l[9]]
        on_ground = [[l[1]] for l in list_of_lists if l[9]]
    
        with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password, autocommit=True) as conn:
            with conn.cursor() as cursor:
                cursor.fast_executemany = True
                
                try:
                    # MERGE+INSERT: update delle info dei voli ATTIVI
                    cursor.executemany(q.sql_merge, on_air)
                    cursor.commit()
                except:
                    print('MERGE NON ANDATA A BUON FINE')
                    print(on_air)
                

                if len(on_ground) > 0:
                    # UPDATE voli attivi. Un volo diventa non attivo se:
                    # - passa allo stato unground
                    # - 
                    try:
                        cursor.executemany(q.sql_update_to_landed, on_ground)
                        cursor.commit()
                    except:
                        print('Aggiornamento atterrati non andato a buon fine')
                        print(on_air)

                try:
                    cursor.execute(q.sql_update_to_inactive)
                    cursor.commit()
                except:
                    print('Aggiornamento usciti dallo spazio aereo non andato a buon fine')
                    print(on_air)


            conn.commit()
            print("INSERIMENTO FINITO")
    except:
        print("Impossibile reperire credenziali di accesso al db dal vault")
        
    logging.info('Python timer trigger function ran at %s', utc_timestamp)
