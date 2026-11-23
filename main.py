
from fastapi import FastAPI, Request, HTTPException
import httpx
import ipaddress

app = FastAPI(title="IP Geolocation API")


@app.get("/location")
async def get_location(request: Request):
    # Get incoming client's IP address
    ip = request.client.host

    # Validate IP and check whether it is public
    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid IP address")

    if not ip_obj.is_global:
        return {
            "ip": ip,
            "country": None,
            "city": None,
            "message": "Local or private IP cannot be geolocated"
        }

    # Look up IP geolocation
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"https://ipwho.is/{ip}")
            response.raise_for_status()
            data = response.json()

        if not data.get("success"):
            raise HTTPException(
                status_code=502,
                detail="IP geolocation lookup failed"
            )

        return {
            "ip": ip,
            "country": data.get("country"),
            "country_code": data.get("country_code"),
            "city": data.get("city"),
            "region": data.get("region"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
        }

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Geolocation service unavailable"
        )
