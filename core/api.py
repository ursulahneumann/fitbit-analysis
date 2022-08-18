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
                
    # Raise for any other error response besides an expired token
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

def check_time_format_wrapper(time: str) -> str:
    """Check times are 'HH:mm' format.

    Args:
        time (str): HH:mm

    Raises:
        ValueError: if time is not acceptable

    Returns:
        str: input time if acceptable
    """
    pattern = re.compile(r"^\d\d:\d\d$")

    if pattern.match(time) is not None:
        return time
    else:
        raise ValueError("time should match 'HH:mm' format")

def check_detail_level_wrapper(detail_level:str, valid_detail_levels: list) -> str:
    """Check that detail levels are in the list of allowed detail levels

    Args:
        detail_level (str): the detail level to be validated
        valid_detail_levels (list): allowed detail levels for that endpoint

    Raises:
        ValueError: if detail_level is not valid

    Returns:
        str: input detail_level if valid
    """
    if detail_level not in valid_detail_levels:
            raise ValueError(f"detail_level {detail_level} should be one of {valid_detail_levels}.")
    return detail_level

def check_period_wrapper(period:str, valid_periods: list) -> str:
    """Check that periods are in the list of allowed periods.

    Args:
        period (str): the period to be validated
        valid_periods (list): allowed periods for that endpoint

    Raises:
        ValueError: if period is not valid

    Returns:
        str: input period if valid
    """
    if period not in valid_periods:
        raise ValueError(f"period '{period}' should be one of {valid_periods}.")
    return period

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

    def by_date_range(self, start_date:str = 'today', end_date:str = 'today') -> dict:
        """Heart rate by date range endpoint.

        Data is intraday when date range spans a single day,
        otherwise is daily summaries when date range is multi-day.

        Args:
            start_date (str, optional): yyyy-MM-dd format date, or 'today'. Defaults to 'today'.
            end_date (str, optional): yyyy-MM-dd format date, or 'today'. Defaults to 'today'.

        Raises:
            ValueError: if date doesn't match expected formats

        Returns:
            dict: from JSON data
        """
        # Validate dates, will raise ValueError
        start_date = check_date_format_wrapper(start_date)
        end_date = check_date_format_wrapper(end_date)

        # API request
        url = constants.API_ROOT
        url += f"/1/user/{self._tokens[constants.SECRETS_USER_ID_KEY]}"
        url += f"/activities/heart/date/{start_date}/{end_date}.json"
        return api_request(url, self._tokens)
        
    def by_date_intraday(
        self,
        date: str = 'today',
        detail_level: str = '1min',
        start_time: str = None,
        end_time: str = None,
        ) -> dict:
        """Heartrate intraday by date.

        For a certain date, get intraday data at given detail_level intervals.
        Optionally restrict to within a period of the day.

        Args:
            date (str, optional): yyyy-MM-dd format date, or 'today'. Defaults to 'today'.
            detail_level (str, optional): one of ['1sec', '1min', '5min', '15min']. Defaults to '1min'.
            start_time (str, optional): 'HH:mm' format. Defaults to None.
            end_time (str, optional): 'HH:mm' format. Defaults to None.

        Raises:
            ValueError: if parameters don't match expected formats

        Returns:
            dict: from JSON data
        """

        # Validate date, raise ValueError
        date = check_date_format_wrapper(date)
        # Validate detail level
        DETAIL_LEVELS = ['1sec', '1min', '5min', '15min']
        detail_level = check_detail_level_wrapper(detail_level, DETAIL_LEVELS)
        # Validate both times or neither provided 
        if (start_time != None) != (end_time != None): # XOR
            raise ValueError("Only one start/end time provided, should be neither or both.")
        # Validate time format
        if start_time != None:
            start_time = check_time_format_wrapper(start_time)
        if end_time != None:
            end_time = check_time_format_wrapper(end_time)
        
        # API request
        url = constants.API_ROOT
        url += f"/1/user/{self._tokens[constants.SECRETS_USER_ID_KEY]}"
        url += f"/activities/heart/date/{date}/1d/{detail_level}"
        if (start_time != None) and (end_time != None):
            url += f"/time/{start_time}/{end_time}"
        url += f".json"
        return api_request(url, self._tokens)


    def by_interval_intraday(
        self,
        start_date: str = 'today',
        end_date: str = 'today',
        detail_level: str = '1min',
        start_time: str = None,
        end_time: str = None,) -> dict:
        """Heart rate intraday by interval.

        Time parameters are optional.

        API endpoint returns inconsistent results depending on the parameters.
        The following table documents the results of different parameter combinations:

        start_date   | end_date     | detail_level | start_time | end_time | result
        ---------------------------------------------------------------------
        'today'      | 'today'      | '1min'       | None       | None     | daily + intraday at 1 min intervals
        'today'      | 'today'      | '1sec'       | None       | None     | invalid 
        '2022-08-14' | '2022-08-14' | '1min        | None       | None     | daily + intraday at 1 min intervals
        '2022-08-14' | '2022-08-14' | '1sec        | None       | None     | generic activity categories
        '2022-08-11' | '2022-08-14' | '1min"       | None       | None     | daily only
        '2022-08-11' | '2022-08-14' | '1sec"       | None       | None     | generic activity categories
        'today'      | 'today'      | '1min'       | '07:00'    | '13:00'  | daily + timeboxed intraday at 1 min intervals
        'today'      | 'today'      | '1sec'       | '07:00'    | '13:00'  | daily + timeboxed intraday at 1 sec intervals
        '2022-08-14' | '2022-08-14' | '1min        | '07:00'    | '13:00'  | daily + timeboxed intraday at 1 min intervals
        '2022-08-14' | '2022-08-14' | '1sec'       | '07:00'    | '13:00'  | daily + timeboxed intraday at 1 sec intervals
        '2022-08-11' | '2022-08-14' | '1min        | '07:00'    | '13:00'  | invalid
        '2022-08-11' | '2022-08-14' | '1sec'       | '07:00'    | '13:00'  | invalid

        Reference:
        https://dev.fitbit.com/build/reference/web-api/heartrate-timeseries/get-heartrate-timeseries-by-date/

        Args:
            start_date (str, optional): yyyy-MM-dd format date, or 'today'. Defaults to 'today'.
            end_date (str, optional): yyyy-MM-dd format date, or 'today'. Defaults to 'today'.
            detail_level (str, optional): '1sec' or '1min'. Defaults to '1min'.
            start_time (str, optional): 'HH:mm' format. Defaults to None.
            end_time (str, optional): 'HH:mm' format. Defaults to None.

        Raises:
            ValueError: For unsupported parameters, or if only one of start/end times provided.

        Returns:
            dict: from JSON data
        """

        # Validate detail level
        DETAIL_LEVELS = ['1sec', '1min']
        detail_level = check_detail_level_wrapper(detail_level, DETAIL_LEVELS)

        # Validate date
        start_date = check_date_format_wrapper(start_date)
        end_date = check_date_format_wrapper(end_date)

        # Validate that if time parameters are used, both start/end times must be provided
        if (start_time != None) != (end_time != None): # XOR
            raise ValueError("Only one start/end time provided, should be neither or both.")
        # Validate time format
        if start_time != None:
            start_time = check_time_format_wrapper(start_time)
        if end_time != None:
            end_time = check_time_format_wrapper(end_time)

        # API request
        url = constants.API_ROOT
        url += f"/1/user/{self._tokens[constants.SECRETS_USER_ID_KEY]}"
        url += f"/activities/heart/date/{start_date}/{end_date}/{detail_level}"
        if (start_time != None) and (end_time != None):
            url += f"/time/{start_time}/{end_time}"
        url += f".json"
        return api_request(url, self._tokens)
