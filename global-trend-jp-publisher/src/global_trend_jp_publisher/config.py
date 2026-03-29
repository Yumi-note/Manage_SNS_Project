from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    rss_feeds: str = Field(default="")
    newsapi_key: str = Field(default="")
    max_items_per_source: int = Field(default=8)
    output_dir: str = Field(default="data/drafts")
    target_language: str = Field(default="ja")
    default_audience: str = Field(default="日本の読者")

    def feed_list(self) -> list[str]:
        return [x.strip() for x in self.rss_feeds.split(",") if x.strip()]
