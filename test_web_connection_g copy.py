import requests
import pytest
import pyodbc

@pytest.mark.parametrize("url", ["https://onsky.azurewebsites.net/api/flightlist?"])
def test_web_connection(url):
    response = requests.get(url)


    assert response.status_code == 200


#https://openskyiu.azurewebsites.net/api/index?
