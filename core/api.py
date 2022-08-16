import requests
import json
import re
from core.util import load_tokens, refresh_token
from core import constants

def api_request(
    url: str,
    tokens: dict,
    config_file = constants.CONFIG_FILE) -> dict:
    """Makes an Fitbit API request.

    To be called from within various API endpoint objects.
    Will try to refresh the access token automatically if expired.

    Args:
        url (str): a premade API endpoint url
        tokens (dict): containing access and refresh tokens
        config_file (str, optional): file location of the config file. Defaults to 'config.toml'.

    Raises:
        Exception: any exception from API requesting.

    Returns:
        dict: from JSON data
    """
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
            # Load new token into the header
            HEADERS['Authorization'] = f"Bearer {tokens[constants.TOKEN_API_ACCESS_TOKEN_KEY]}"
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

def check_date_format_wrapper(date: str) -> str:
    """Check dates are 'yyyy-MM-dd' or 'today'.

    Args:
        date (str): yyyy-MM-dd format or 'today'

    Raises:
        ValueError: if date is not acceptable

    Returns:
        str: input date if acceptable
    """
    pattern = re.compile(r"^\d\d\d\d-\d\d-\d\d$")
    
    if pattern.match(date) is not None:
        return date
    elif date == 'today':
        return date
    else:
        raise ValueError("date should match 'yyyy-MM-dd' format, or 'today'")
    

class FitbitAPI:
    def __init__(self, tokens: dict) -> None:
        # Attributes representing api endpoints
        # allow for dot notation access by client code
        self.hr = _HeartRate(tokens)

class _HeartRate:
    def __init__(self, tokens) -> None:
        self._tokens = tokens
    
    def by_date(self, date:str = 'today', period: str = '1d' ) -> dict:
        """Heart rate by date endpoint.

        Gets data for a given period preceding a certain date.
        E.g. '2022-08-15' and '7d' would be from Aug 9 to 15.
        Using period '1d' will get intraday data, all other periods get daily summaries.

        Reference:
        https://dev.fitbit.com/build/reference/web-api/heartrate-timeseries/get-heartrate-timeseries-by-date/

        Args:
            date (str, optional): yyyy-MM-dd format date, or 'today'. Defaults to 'today'.
            period (str, optional): Time period for the data.
                One of ['1d', '7d', '30d', '1w', '1m']. Defaults to '1d'.

        Raises:
            ValueError: if date/period don't match expected formats

        Returns:
            dict: from JSON data
        """
        # Validate period
        VALID_PERIODS = ['1d', '7d', '30d', '1w', '1m']
        if period not in VALID_PERIODS:
            raise ValueError(f"period '{period}' should be one of {VALID_PERIODS}.")

        # Validate date
        date = check_date_format_wrapper(date)

        # API request
        url = constants.API_ROOT
        url += f"/1/user/{self._tokens[constants.SECRETS_USER_ID_KEY]}"
        url += f"/activities/heart/date/{date}/{period}.json"
        return api_request(url, self._tokens)

