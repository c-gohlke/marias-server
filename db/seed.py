from .crud import create_user


def seed(session):
    username = "clem"
    pwd = "clem_pwd"
    email = "clem@marias.com"

    create_user(session, pwd, username, email)

    username = "ondrej"
    pwd = "ondrej_pwd"
    email = "ondrej@marias.com"

    create_user(session, pwd, username, email)

    username = "adam"
    pwd = "adam_pwd"
    email = "adam@marias.com"

    create_user(session, pwd, username, email)

    username = "seckin"
    pwd = "seckin_pwd"
    email = "seckin@marias.com"

    create_user(session, pwd, username, email)

    username = "classic"
    pwd = "classic_pwd"
    email = "classic@marias.com"

    create_user(session, pwd, username, email)

    username = "marias"
    pwd = "marias_pwd"
    email = "marias@marias.com"

    create_user(session, pwd, username, email)

    username = "dark"
    pwd = "dark_pwd"
    email = "dark@marias.com"

    create_user(session, pwd, username, email)
