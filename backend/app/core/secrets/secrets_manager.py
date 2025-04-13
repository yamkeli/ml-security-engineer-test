import boto3
from botocore.exceptions import ClientError
from ast import literal_eval


def get_db_secrets() -> dict:
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name="ap-southeast-5")

    secret_name = "contact_app_server/rds_contact_db"

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        secret = literal_eval(get_secret_value_response["SecretString"])

        return {
            "username": secret["username"],
            "password": secret["password"],
            "host": secret["host"],
            "port": secret["port"],
            "db": secret["dbname"],
        }

    except ClientError as e:
        raise e
    except Exception as e:
        raise e


def get_jwt_key() -> str:
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name="ap-southeast-5")

    secret_name = "contact_app_server/jwt_key"
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        secret = literal_eval(get_secret_value_response["SecretString"])

        return secret["jwt_key"]

    except ClientError as e:
        raise e
    except Exception as e:
        raise e
