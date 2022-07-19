import util.auth as auth

MOCK_CODE_CHALLENGE = '-4cf-Mzo_qg9-uq0F4QwWhRh4AjcAqNx7SbYVsdmyQM'
MOCK_CLIENT_ID ='ABC123' # i.e. app id
# Spaces are not necessary to convert, as webbrowser.open()
# will convert.
MOCK_AUTH_URL = (f"https://www.fitbit.com/oauth2/authorize?"
                 f"client_id={MOCK_CLIENT_ID}"
                 f"&response_type=code"
                 f"&code_challenge={MOCK_CODE_CHALLENGE}"
                 f"&code_challenge_method=S256"
                 f"&scope=weight location settings profile nutrition"
                 f" activity sleep heartrate social")


def test_make_code_challenge():
    # See step 1 of 
    # https://dev.fitbit.com/build/reference/web-api/developer-guide/authorization/

    assert auth.make_code_challenge('01234567890123456789012345678901234567890123456789') \
        == '-4cf-Mzo_qg9-uq0F4QwWhRh4AjcAqNx7SbYVsdmyQM'

def test_make_auth_api_url():
    # See step 2 of 
    # https://dev.fitbit.com/build/reference/web-api/developer-guide/authorization/
    

    assert auth.make_auth_api_url(
        client_id = MOCK_CLIENT_ID,
        scope = "weight location settings profile nutrition activity sleep heartrate social",
        code_challenge = MOCK_CODE_CHALLENGE
    ) == MOCK_AUTH_URL