import requests
import pytest

@pytest.mark.parametrize("url", ["https://openskyiu.azurewebsites.net/api/index?"])
def test_web_connection(url):
    response = requests.get(url)
    assert response.status_code == 200


