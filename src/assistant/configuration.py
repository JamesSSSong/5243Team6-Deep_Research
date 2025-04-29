import os
from dataclasses import dataclass, fields
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from dataclasses import dataclass

from enum import Enum


class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the research assistant."""

    max_web_research_loops: int = 1
    local_llm: str = "llama3.2"
    search_api: SearchAPI = SearchAPI.TAVILY  # Default to TAVILY






    # New configuration for YouTube and Email
    youtube_api_key: Optional[str] = os.getenv("YOUTUBE_API_KEY")
    email_recipient: Optional[str] = os.getenv("EMAIL_RECIPIENT")
    smtp_server: Optional[str] = 'smtp.gmail.com'
    smtp_port: Optional[int] = 587
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    tavily_api_key: Optional[str] = os.getenv("TAVILY_API_KEY")
    discord_webhook_url: Optional[str] = os.getenv("DISCORD_WEBHOOK_URL")
    pinecone_api_key: Optional[str] = os.getenv("PINECONE_API_KEY")
    pinecone_environment: Optional[str] = os.getenv("PINECONE_ENVIRONMENT")
    pinecone_index_name: Optional[str] = os.getenv("PINECONE_INDEX_NAME")





    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})