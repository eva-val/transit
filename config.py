from pydantic_settings import BaseSettings, SettingsConfigDict


class config(BaseSettings):
    ONEBUSAWAY_API_KEY: str
    SEATTLE_CENTER: tuple[float, float] = (47.609941, -122.257517)
    ROUTE_IDS: list[str] = ["40_100479", "40_2LINE", "1_100146"]
    UPDATE_INTERVAL: int = 60  # seconds
    DEFAULT_ZOOM: int = 12
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


Config = config()
