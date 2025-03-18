from datetime import datetime
from pydantic import BaseModel


class VehiclePosition(BaseModel):
    vehicle_id: str
    lat: float
    lon: float
    timestamp: int
    status: str
    phase: str
    schedule_deviation: int

    @property
    def schedule_status(self) -> tuple[str, str]:
        """Returns (status_text, color) tuple based on schedule deviation"""
        schedule_mins = self.schedule_deviation / 60
        if schedule_mins > 0:
            return f"{abs(schedule_mins):.0f} mins late", "red"
        elif schedule_mins < 0:
            return f"{abs(schedule_mins):.0f} mins early", "green"
        return "on time", "blue"

    @property
    def last_update_time(self) -> str:
        """Returns formatted last update time"""
        return datetime.fromtimestamp(self.timestamp / 1000).strftime("%H:%M:%S")
