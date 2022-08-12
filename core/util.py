import toml
import constants
import auth

def load_tokens(config_file_path: str) -> dict:
    """Load tokens from a secrets file specified by the config file.

    Args:
        config_file_path (str): location of project wide config file

    Returns:
        dict: containing user id, access token, and refresh token
    """
    config = toml.load(config_file_path)
    secrets = toml.load(config[constants.CONFIG_SECRETS_FILE_KEY])
    fields = [constants.SECRETS_USER_ID_KEY,
              constants.SECRETS_ACCESS_TOKEN_KEY,
              constants.SECRETS_REFRESH_TOKEN_KEY]
    return {key:secrets[key] for key in fields}

def refresh_token(config_file_path: str) -> None:
    """Get a new access/token pair and save it.

    Args:
        config_file_path (str): location of project wide config file
    """
    # Load current tokens
    config = toml.load(config_file_path)
    secrets = toml.load(config[constants.CONFIG_SECRETS_FILE_KEY])

    # Make refresh request
    data = auth.request_new_token_pair(
        client_id = secrets[constants.SECRETS_CLIENT_ID_KEY],
        client_secret = secrets[constants.SECRETS_CLIENT_SECRETS_KEY],
        refresh_token = secrets[constants.SECRETS_REFRESH_TOKEN_KEY]
    )

    # Swap tokens
    secrets[constants.SECRETS_ACCESS_TOKEN_KEY] = data[constants.TOKEN_API_ACCESS_TOKEN_KEY]
    secrets[constants.SECRETS_REFRESH_TOKEN_KEY] = data[constants.TOKEN_API_REFRESH_TOKEN_KEY]

    # Save new tokens by overwriting secrets file
    toml.dump(secrets, config[constants.CONFIG_SECRETS_FILE_KEY])