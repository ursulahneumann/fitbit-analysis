from secrets import token_urlsafe
from base64 import urlsafe_b64encode, b64encode, b64decode
from hashlib import sha256
import webbrowser
import requests
import json

TOKEN_ENDPOINT = "https://api.fitbit.com/oauth2/token"


def make_code_verifier(bytes_of_randomness:int = 64) -> str:
    """Generate an OAuth2 PKCE code verifier, i.e. 43-128 char crypto-safe random str."""
    return token_urlsafe(bytes_of_randomness)

def make_code_challenge(code_verifier:str) -> str:
    """Generate an OAuth2 code challenge from a code verifier."""
    # Set up the hashing func
    hasher = sha256()
    hasher.update(code_verifier.encode())
    # Base64 encode the digest, get the string, strip trailing padding.
    return urlsafe_b64encode(hasher.digest()).decode().replace('=', '')

def make_auth_api_url(
    client_id:str,
    scope:str,    
    code_challenge:str,
    code_challenge_method:str = 'S256',
    response_type:str = 'code') -> str:
    """Make url for authorization endpoint.

    Args:
        client_id (str): Id received during app registration.
        scope (str): Space separated str e.g. 'weight heartrate sleep'.
        code_challenge (str): OAuth2 PKCE code challenge.
        code_challenge_method (str, optional): Only 'S256' is currently supported.
        response_type (str, optional): Only 'code' is currently supported.

    Returns:
        str: A URL.
    """
    return (f"https://www.fitbit.com/oauth2/authorize?"
            f"client_id={client_id}"
            f"&response_type={response_type}"
            f"&code_challenge={code_challenge}"
            f"&code_challenge_method={code_challenge_method}"
            f"&scope={scope}"
    )

def retrieve_auth_code(
    client_id:str,
    scope:str,    
    code_challenge:str) -> None:
    """Retrieve the authorization code.

    Args:
        client_id (str): Id received during app registration.
        scope (str): Space separated str e.g. 'weight heartrate sleep'.
        code_challenge (str): OAuth2 PKCE code challenge.
    """
    url = make_auth_api_url(client_id, scope, code_challenge)
    # Webbrowser open converts spaces in scope string to %20.
    webbrowser.open(url)

def exchange_code_for_tokens(
    client_id:str,
    client_secret: str,
    authorization_code:str, 
    code_verifier:str, 
    grant_type="authorization_code",
    api_endpoint=TOKEN_ENDPOINT) -> dict:
    """Exchange user-specific authorization code for access and refresh tokens.

    Args:
        client_id (str): Id received during app registration.
        client_secret (str): Secret received during app registration.
        authorization_code (str): Previously received user authorization code.
        code_verifier (str): Previously generated code verifier.
        grant_type (str, optional): Only "authorization_code" is currently supported.
        api_endpoint (_type_, optional): Currently default endpoint at 
            https://api.fitbit.com/oauth2/token.

    Returns:
        dict: Converted JSON response containing access/refresh tokens.
    """
    r = requests.post(
        url=api_endpoint,
        headers={
            'Authorization':
            'Basic ' + b64encode((client_id + ':' + client_secret).encode()).decode()},
        data={
            'client_id':client_id,
            'code':authorization_code,
            'code_verifier':code_verifier,
            'grant_type':grant_type,
        })

    # Raise if something went wrong with the request
    try:
        r.raise_for_status()
    except Exception as e:
        print('\n\n')
        print("Response content for error at bottom:")
        print()
        print(r.content)
        raise e
    return json.loads(r.text)
    