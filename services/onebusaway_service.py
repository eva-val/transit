from typing import List
from onebusaway import AsyncOnebusawaySDK
from models import VehiclePosition


class OneBusAwayService:
    def __init__(self, api_key: str):
        self.client = AsyncOnebusawaySDK(api_key=api_key)

    async def fetch_trips_for_route(self, route_id: str) -> List[VehiclePosition]:
        trips = await self.client.trips_for_route.list(route_id=route_id)
        vehicles: List[VehiclePosition] = []

        for trip in trips.data.list:
            status = trip.status
            if status.position and status.status not in {"default", "DUPLICATED"}:
                vehicles.append(
                    VehiclePosition(
                        vehicle_id=status.vehicle_id,
                        lat=status.position.lat,
                        lon=status.position.lon,
                        timestamp=status.last_update_time,
                        status=status.status,
                        phase=status.phase,
                        schedule_deviation=status.schedule_deviation,
                    )
                )
        return vehicles

    async def get_route_shapes(self, route_id: str) -> List[str]:
        route_data = await self.client.stops_for_route.list(route_id=route_id)
        return [polyline.points for polyline in route_data.data.entry.polylines]
