from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    openai_api_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_public_key: str = ""
    langfuse_host: str = "http://localhost:3000"
    zoho_client_id: str = ""
    zoho_client_secret: str = ""
    zoho_refresh_token: str = ""
    zoho_api_domain: str = "www.zohoapis.in"
    zoho_accounts_domain: str = "accounts.zoho.in"
    zoho_owner: str = ""
    zoho_app_name: str = ""
    openai_model_complex: str = "gpt-4o"
    openai_model_simple: str = "gpt-4o-mini"
    cache_ttl_seconds: int = 300
    anomaly_z_threshold: float = 2.5
    anomaly_iqr_multiplier: float = 1.5
    forecast_min_data_points: int = 3
    smtp_host: str = "smtp.zoho.in"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_addr: str = ""


settings = Settings()
