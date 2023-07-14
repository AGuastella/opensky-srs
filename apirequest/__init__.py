# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
from requests.auth import HTTPBasicAuth
import json
import requests
def main(nome: str) -> dict:
    r = requests.get('https://opensky-network.org/api/states/all?lamin=36.619987291&lomin=6.7499552751&lamax=47.1153931748&lomax=18.4802470232')#,auth = HTTPBasicAuth('g1g1', 'dkKIskisiKIKI£443'))
    #auth = HTTPBasicAuth('genelonopensky', 'dkKIskisiKIKI£443'))
    result=r.json()
    print("xwjxopjxj")
    print(result['time'])
    print(type(result['states']))    
    return result
