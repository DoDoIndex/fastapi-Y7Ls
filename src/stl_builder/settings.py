import os
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    GOOGLE_CLOUD_STORAGE = {
        "type": os.getenv("GOOGLE_STORAGE_type"),
        "project_id": os.getenv("GOOGLE_STORAGE_project_id"),
        "private_key_id": os.getenv("GOOGLE_STORAGE_private_key_id"),
        "private_key": os.getenv("GOOGLE_STORAGE_private_key"),
        "client_email": os.getenv("GOOGLE_STORAGE_client_email"),
        "client_id": os.getenv("GOOGLE_STORAGE_client_id"),
        "auth_uri": os.getenv("GOOGLE_STORAGE_auth_uri"),
        "token_uri": os.getenv("GOOGLE_STORAGE_token_uri"),
        "auth_provider_x509_cert_url": os.getenv(
            "GOOGLE_STORAGE_auth_provider_x509_cert_url"
        ),
        "client_x509_cert_url": os.getenv("GOOGLE_STORAGE_client_x509_cert_url"),
        "universe_domain": os.getenv("GOOGLE_STORAGE_universe_domain"),
    }


settings = Settings()
