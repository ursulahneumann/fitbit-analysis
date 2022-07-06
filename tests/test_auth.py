import util.auth as auth

def test_generate_code_challenge():
    # See step 1 of 
    # https://dev.fitbit.com/build/reference/web-api/developer-guide/authorization/

    assert auth.generate_code_challenge('01234567890123456789012345678901234567890123456789') \
        == '-4cf-Mzo_qg9-uq0F4QwWhRh4AjcAqNx7SbYVsdmyQM'