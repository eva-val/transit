import folium
from folium import plugins
from typing import List
from models import VehiclePosition
from config import Config


class MapService:
    @staticmethod
    def create_vehicle_popup(vehicle: VehiclePosition) -> str:
        return f"""
        <div style="font-family: Arial; font-size: 12px;">
            <b>Vehicle ID:</b> {vehicle.vehicle_id}<br>
            <b>Status:</b> {vehicle.status}<br>
            <b>Phase:</b> {vehicle.phase}<br>
            <b>Schedule:</b> {vehicle.schedule_status[0]}<br>
            <b>Last Update:</b> {vehicle.last_update_time}
        </div>
        """

    @staticmethod
    def create_map(vehicles: List[VehiclePosition], points: List[str]) -> folium.Map:
        m = folium.Map(
            location=Config.SEATTLE_CENTER,
            zoom_start=Config.DEFAULT_ZOOM,
            tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        )

        # Add route lines
        for point in points:
            plugins.PolyLineFromEncoded(encoded=point).add_to(m)

        # Add vehicle markers
        for vehicle in vehicles:
            status_text, color = vehicle.schedule_status
            popup_html = MapService.create_vehicle_popup(vehicle)

            folium.Marker(
                location=[vehicle.lat, vehicle.lon],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=color, icon="train", prefix="fa"),
                tooltip=f"Train {vehicle.vehicle_id}",
            ).add_to(m)

        return m

    @staticmethod
    def create_html_container(map_html: str) -> str:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sound Transit Train Tracker</title>
            <script>
                let updating = false;

                async function updateMap() {{
                    if (updating) return;
                    updating = true;

                    try {{
                        const response = await fetch('/map-data');
                        if (response.ok) {{
                            const mapHtml = await response.text();
                            document.getElementById('map-container').innerHTML = mapHtml;
                        }}
                    }} catch (error) {{
                        console.error('Error updating map:', error);
                    }} finally {{
                        updating = false;
                    }}
                }}

                function startCountdown(duration) {{
                    let timer = duration;
                    const countdownElement = document.getElementById('countdown');

                    function updateCounter() {{
                        if (timer <= 0) {{
                            updateMap();
                            timer = duration;
                        }}
                        countdownElement.innerHTML = 'Next update in: ' + timer + ' seconds';
                        timer--;
                        setTimeout(updateCounter, 1000);
                    }}

                    updateCounter();
                }}

                document.addEventListener('DOMContentLoaded', function() {{
                    startCountdown({Config.UPDATE_INTERVAL});
                }});
            </script>
            <style>
                #countdown {{
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: white;
                    padding: 10px;
                    border: 1px solid black;
                    border-radius: 5px;
                    z-index: 1000;
                    font-family: Arial, sans-serif;
                }}
                #map-container {{
                    width: 100%;
                    height: 100%;
                }}
            </style>
        </head>
        <body>
            <div id="countdown">Next update in: {Config.UPDATE_INTERVAL} seconds</div>
            <div id="map-container">
                {map_html}
            </div>
        </body>
        </html>
        """
