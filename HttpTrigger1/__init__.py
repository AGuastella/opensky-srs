import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:

    with open("/etc/odbcinst.ini") as o:
        text = ''.join(o.readlines())

    return func.HttpResponse(text)