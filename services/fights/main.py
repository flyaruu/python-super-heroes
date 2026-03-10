from fastapi import FastAPI, HTTPException, Request, APIRouter
import httpx
import uvicorn
import os
import logging
import uuid
import asyncio
from starlette.responses import JSONResponse, Response


# Configure logging - set to WARNING to reduce overhead
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


app = FastAPI()
# Optimized HTTP client with connection pooling and timeouts
client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20,
    ),
    timeout=httpx.Timeout(
        connect=2.0,
        read=5.0,
        write=2.0,
        pool=2.0,
    ),
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up HTTP client")


@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Lightweight health check endpoint for orchestration."""
    return Response("OK", status_code=200, media_type="text/plain")

# Fights router with external service calls
fights_router = APIRouter(prefix="/api")

# @fights_router.get("/randomlocation")
# async def random_location():
#     """Fetch a random fight location from external service."""
#     try:
#         response = await client.get(f"{EXTERNAL_BASE_URL}/randomlocation")
#         response.raise_for_status()
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=502, detail=f"Error connecting to external service: {exc}")
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     return response.json()

async def get_hero():
    """Fetch a random hero from external service."""
    try:
        response = await client.get("http://heroes:8000/api/heroes/random_hero")
        response.raise_for_status()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Error connecting to external service: {exc}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    return response.json()

async def get_villain():
    """Fetch a random villain from external service."""
    try:
        response = await client.get("http://villains:8000/api/villains/random_villain")
        response.raise_for_status()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Error connecting to external service: {exc}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    return response.json()

async def get_location():
    """Fetch a random fight location from external service."""
    try:
        response = await client.get("http://locations:8000/api/locations/random_location")
        response.raise_for_status()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Error connecting to external service: {exc}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    return response.json()


def build_fight_response(hero: dict, villain: dict, location: dict) -> dict:
    """Build fight response dict to avoid duplicate logic."""
    hero_level = hero.get("level", 0)
    villain_level = villain.get("level", 0)
    hero_wins = hero_level > villain_level
    
    winner = hero if hero_wins else villain
    loser = villain if hero_wins else hero
    
    return {
        "id": str(uuid.uuid4()),
        "fight_date": "2023-10-01T12:00:00Z",
        "winner_name": winner["name"],
        "winner_level": winner.get("level", 0),
        "winner_powers": winner.get("powers", ""),
        "winner_picture": winner.get("picture", ""),
        "loser_name": loser["name"],
        "loser_level": loser.get("level", 0),
        "loser_powers": loser.get("powers", ""),
        "loser_picture": loser.get("picture", ""),
        "winner_team": "heroes" if hero_wins else "villains",
        "loser_team": "villains" if hero_wins else "heroes",
        "hero": hero,
        "villain": villain,
        "location": location,
    }


@fights_router.get("/fights/randomfighters")
async def random_fighters()-> JSONResponse:
    """Fetch two random fighters from external service in parallel."""
    hero, villain = await asyncio.gather(get_hero(), get_villain())
    return JSONResponse({"hero": hero, "villain": villain})

@fights_router.get("/fights/randomlocation")
async def random_location()-> JSONResponse:
    """Fetch random fight location from external service."""
    location = await get_location()
    return JSONResponse(location)

@fights_router.post("/fights")
async def post_fight(request: Request)-> JSONResponse:
    fight_request = await request.json()
    hero = fight_request.get("hero")
    villain = fight_request.get("villain")
    location = fight_request.get("location")
    
    response = build_fight_response(hero, villain, location)
    return JSONResponse(response, status_code=200)




@fights_router.get("/fights/execute_fight")
async def execute_random_fight()-> JSONResponse:
    """Execute random fight by fetching all data in parallel."""
    location, hero, villain = await asyncio.gather(
        get_location(),
        get_hero(),
        get_villain()
    )
    
    response = build_fight_response(hero, villain, location)
    return JSONResponse(response, status_code=200)

# @fights_router.get("/")
# async def list_fights():
#     """Fetch a list of fights from external service."""
#     try:
#         response = await client.get(f"{EXTERNAL_BASE_URL}/")
#         response.raise_for_status()
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=502, detail=f"Error connecting to external service: {exc}")
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     return response.json()

# Include the router
app.include_router(fights_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
