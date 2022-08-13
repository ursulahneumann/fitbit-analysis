import requests
import json
from core.util import load_tokens, refresh_token
from core import constants

def api_request(
    url: str,
    tokens: dict,
    config_file = constants.CONFIG_FILE) -> dict:

    HEADERS = {'Authorization': f"Bearer {tokens[constants.TOKEN_API_ACCESS_TOKEN_KEY]}",
                 'accept':"application/json"}
    
    response = requests.get(url=url, headers=HEADERS)

    # Refresh the tokens if access token expired
    if response.status_code == 401:
        error_type = json.loads(response.content)['errors'][0]['errorType']
        if error_type == "expired_token":
            # Get and save new tokens, the reload them
            refresh_token(config_file)
            tokens = load_tokens(config_file)
            # Get the response again
            response = requests.get(url=url, headers=HEADERS)
                
    # Fall through of the if statements prints and raises for other errors
    try: 
        response.raise_for_status()
    except Exception as e:
        print(f"Status Code: {response.status_code}")
        print(f"Content: ")
        print(f"{response.content}")
        print(f"---")
        raise e

    return json.loads(response.content)

class FitBitAPI:
    def __init__(self, tokens: dict) -> None:
        # Attributes representing api endpoints
        # allow for dot notation access by client code
        self.hr = _HeartRate(tokens)

class _HeartRate:
    def __init__(self, tokens) -> None:
        self._tokens = tokens
    
    def by_date(self, date:str = 'today', period: str = '1d' ) -> dict:
        url = constants.API_ROOT
        url += f"/1/user/{self._tokens[constants.SECRETS_USER_ID_KEY]}"
        url += f"/activities/heart/date/{date}/{period}.json"
        return api_request(url, self._tokens)

