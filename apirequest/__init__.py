# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import random
import json
import time
import requests
from requests.auth import HTTPBasicAuth

from utility.credential import openskycredential as oc


class none_result(Exception):
    pass

def main(nome: str) -> dict:
    now = int(time.time())

    while(True):     
        try:
            # ROTAZIONE CREDENZIALI !!!
            rand = random.randint(0, len(oc.opensky_credential)-1)

            # RICHIESTA CON CREDENZIALI, A ROTAZIONE
            #r = requests.get('https://opensky-network.org/api/states/all?lamin=36.619987291&lomin=6.7499552751&lamax=47.1153931748&lomax=18.4802470232', auth = HTTPBasicAuth(oc.opensky_credential[rand][0], oc.opensky_credential[rand][1]))
            
            # RICHIESTA CON CREDENZIALI SINGOLE
            #r = requests.get('https://opensky-network.org/api/states/all?lamin=36.619987291&lomin=6.7499552751&lamax=47.1153931748&lomax=18.4802470232', auth = HTTPBasicAuth('g1g1', 'dkKIskisiKIKI£443'))

            # RICHIESTA SENZA CREDENZIALI
            r = requests.get('https://opensky-network.org/api/states/all?lamin=36.619987291&lomin=6.7499552751&lamax=47.1153931748&lomax=18.4802470232')

            if r is None: 
                raise none_result
            
            if r.status_code == 200:
                # Stampa non necessaria per messaggio ottenuto correttamente
                #print(f'{now} - [n°{rand}][{r.status_code}] OK!')
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
    #print("xwjxopjxj")
    #print(result['time'])
    #print(type(result['states']))    
    
    return result
