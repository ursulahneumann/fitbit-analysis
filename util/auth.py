from secrets import token_urlsafe
from base64 import urlsafe_b64encode
from hashlib import sha256


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

