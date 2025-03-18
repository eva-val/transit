from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from services.onebusaway_service import OneBusAwayService
from services.map_service import MapService
from config import Config
from contextlib import asynccontextmanager

# Global state
latest_map_html = ""
last_update = datetime.now()
oba_service = OneBusAwayService(Config.ONEBUSAWAY_API_KEY)
map_service = MapService()


async def fetch_all_vehicles_and_shapes():
    """Fetch all vehicles and shapes for configured routes"""
    vehicles = []
    shapes = []

    for route_id in Config.ROUTE_IDS:
        route_vehicles = await oba_service.fetch_trips_for_route(route_id)
        route_shapes = await oba_service.get_route_shapes(route_id)
        vehicles.extend(route_vehicles)
        shapes.extend(route_shapes)

    return vehicles, shapes


async def update_map():
    """Background task to update the map periodically"""
    global latest_map_html, last_update

    vehicles, shapes = await fetch_all_vehicles_and_shapes()
    folium_map = map_service.create_map(vehicles, shapes)
    latest_map_html = map_service.create_html_container(folium_map._repr_html_())
    last_update = datetime.now()

    print(f"\nUpdated map at {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Found {len(vehicles)} active vehicles")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Initialize the map
    await update_map()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/status")
async def get_status():
    """Get the status of the map updates"""
    return {"last_update": last_update.isoformat(), "status": "active"}


@app.get("/", response_class=HTMLResponse)
async def get_map():
    """Serve the full HTML page with map and refresh functionality"""
    return latest_map_html.replace(
        'style="position:relative;width:100%;height:0;padding-bottom:60%;',
        'style="width:100%;height:0;padding-bottom:60%;',
    )


@app.get("/map-data", response_class=HTMLResponse)
async def get_map_data():
    """Endpoint that returns just the map HTML for updates"""
    vehicles, shapes = await fetch_all_vehicles_and_shapes()
    folium_map = map_service.create_map(vehicles, shapes)
    return folium_map._repr_html_().replace(
        'style="position:relative;width:100%;height:0;padding-bottom:60%;',
        'style="width:100%;height:0;padding-bottom:60%;',
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
