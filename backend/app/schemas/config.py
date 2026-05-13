from pydantic import BaseModel


class ConfigRequest(BaseModel):
    github_token: str | None = None
    github_webhook_secret: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_deployment: str | None = None
    azure_api_version: str | None = None
    azure_embedding_deployment: str | None = None


class ConfigResponse(BaseModel):
    github_token: str | None = None
    github_webhook_secret: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_deployment: str | None = None
    azure_api_version: str | None = None
    azure_embedding_deployment: str | None = None
    webhook_url: str | None = None
