from secrets import token_urlsafe
from base64 import urlsafe_b64encode
from hashlib import sha256
from urllib.parse import quote as url_quote


def generate_code_verifier(bytes_of_randomness:int = 64) -> str:
    """Generate an OAuth2 PKCE code verifier, i.e. 43-128 char crypto-safe random str."""
    return token_urlsafe(bytes_of_randomness)

def generate_code_challenge(code_verifier:str) -> str:
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
        client_id (str): _description_
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
            f"&scope={url_quote(scope)}"
    )