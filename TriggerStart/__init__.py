# This function an HTTP starter function for Durable Functions.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable activity function (default name is "Hello")
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt
 
import logging
import datetime
import azure.functions as func
import azure.durable_functions as df

async def main(mytimer: func.TimerRequest, starter: str)-> None:
    client = df.DurableOrchestrationClient(starter)
    instance_id = await client.start_new("Orchestrator", None, None)

    logging.info(f"Started orchestration with ID = '{instance_id}'.")
   