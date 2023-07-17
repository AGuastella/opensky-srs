import requests
import pytest

@pytest.mark.parametrize("url", ["https://www.google.com"])
def test_web_connection(url):
    response = requests.get(url)
    assert response.status_code == 200


#https://openskyiu.azurewebsites.net/api/index?