import toml
from urllib.parse import quote

# Add path to packages for import
import os
import sys
script_dir = os.path.dirname(__file__)
core_dir = os.path.join(script_dir, '..', 'core')
sys.path.append(core_dir)

from constants import *
from auth import *

# Read in config file.
with open(CONFIG_FILE) as f:
    config = toml.load(f)

# Read in secrets using secrets file location in config.toml
with open(config[CONFIG_SECRETS_FILE_KEY]) as f:
    secrets = toml.load(f)

# Scope is a space separated string
scope = quote(config[CONFIG_SCOPE_KEY])
# The app id and client secret registered with Fitbit developer portal
client_id = secrets[SECRETS_CLIENT_ID_KEY]
client_secret = secrets[SECRETS_CLIENT_SECRETS_KEY]

# Five step authorization flow as per:
# https://dev.fitbit.com/build/reference/web-api/developer-guide/authorization/
# Auth Flow Step 1: make code verifier and challenge.
code_verifier = make_code_verifier()
code_challenge = make_code_challenge(code_verifier)

# Auth Flow Step 2 and 3: request and receive authorization code.
# This will prompt for a login and authorization in webbrowser.
# On completion, it will return the user to localhost,
# with a query string parameter containing the code challenge.
retrieve_auth_code(client_id, scope, code_challenge)

# Prompts the user before proceeding
auth_code = input(" Paste code challenge from URL query string.\n"
                    " e.g. between 'code=' and '#_=_' in\n"
                    " \n       \"https://myapp.com/callback?code=d62d6f5bdc13df79d9a5f#_=_\"\n"
                    " : "
)

# Save the auth code
secrets[SECRETS_AUTH_CODE_KEY] = auth_code
with open(config[CONFIG_SECRETS_FILE_KEY], 'w') as f:
    toml.dump(secrets, f)

# Auth Flow Step 4 and 5: exchange auth code for access/refresh tokens.
tokens_dict = exchange_code_for_tokens(
    client_id,
    client_secret,
    auth_code,
    code_verifier
)

# Save the tokens and user id
secrets[SECRETS_ACCESS_TOKEN_KEY] = tokens_dict[TOKEN_API_ACCESS_TOKEN_KEY]
secrets[SECRETS_REFRESH_TOKEN_KEY] = tokens_dict[TOKEN_API_REFRESH_TOKEN_KEY]
secrets[SECRETS_USER_ID_KEY] = tokens_dict[TOKEN_API_USER_ID_KEY]
with open(config[CONFIG_SECRETS_FILE_KEY], 'w') as f:
    toml.dump(secrets, f)

# Print success message
print("Successful acquired access and refresh tokens!")
