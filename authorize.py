from util.auth import *
import toml
from urllib.parse import quote


CONFIG_FILE = 'config.toml'
CONFIG_SCOPE_KEY = 'scope'
CONFIG_SECRETS_FILE_KEY = 'secrets_file'
SECRETS_CLIENT_ID_KEY = 'client_id'
SECRETS_CLIENT_SECRETS_KEY = 'client_secret'
SECRETS_AUTH_CODE_KEY = 'auth_code'
SECRETS_ACCESS_TOKEN_KEY = 'access_token'
SECRETS_REFRESH_TOKEN_KEY = 'refresh_token'
TOKEN_API_ACCESS_TOKEN_KEY = 'access_token'
TOKEN_API_REFRESH_TOKEN_KEY = 'refresh_token'

# Read in config file.
with open(CONFIG_FILE) as f:
    config = toml.load(f)

# Read in secrets using secrets file location in config.toml
with open(config[CONFIG_SECRETS_FILE_KEY]) as f:
    secrets = toml.load(f)

# Space separated scope
scope = quote(config[CONFIG_SCOPE_KEY])
# The app id and client secret registered with Fitbit developer portal
client_id = secrets[SECRETS_CLIENT_ID_KEY]
client_secret = secrets[SECRETS_CLIENT_SECRETS_KEY]

# Auth flow step 1: make code verifier and challenge.
code_verifier = make_code_verifier()
code_challenge = make_code_challenge(code_verifier)
# Auth flow step 2 request authorization.
# This will prompt for a login and authorization in webbrowser.
# On completion, it will return the user to localhost,
# with a query string parameter containing the code challenge.
retrieve_auth_code(client_id, scope, code_challenge)

# Prompt for proceed
auth_code = input(" Paste code challenge from URL query string.\n"
                    " e.g. between 'code=' and '#_=_' in\n"
                    " \n       \"https://myapp.com/callback?code=d62d6f5bdc13df79d9a5f#_=_\"\n"
                    " : "
)

# Save the auth code
secrets[SECRETS_AUTH_CODE_KEY] = auth_code
with open(config[CONFIG_SECRETS_FILE_KEY], 'w') as f:
    toml.dump(secrets, f)

# Exchange for access and refresh token
tokens_dict = exchange_code_for_tokens(
    client_id,
    client_secret,
    auth_code,
    code_verifier
)

# Save the tokens
secrets[SECRETS_ACCESS_TOKEN_KEY] = tokens_dict[TOKEN_API_ACCESS_TOKEN_KEY]
secrets[SECRETS_REFRESH_TOKEN_KEY] = tokens_dict[TOKEN_API_REFRESH_TOKEN_KEY]
with open(config[CONFIG_SECRETS_FILE_KEY], 'w') as f:
    toml.dump(secrets, f)
