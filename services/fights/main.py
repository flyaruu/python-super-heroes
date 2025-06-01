from fastapi import FastAPI, HTTPException, Request, APIRouter
import httpx
import uvicorn
import os
import logging
import uuid
from starlette.responses import JSONResponse, Response


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


app = FastAPI()
client = httpx.AsyncClient()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up HTTP client")


@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()

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
    logger.info("Fetching random hero from external service")
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
    logger.info("Fetching random villain from external service")
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
    logger.info("Fetching random location from external service")
    """Fetch a random fight location from external service."""
    try:
        response = await client.get("http://locations:8000/api/locations/random_location")
        response.raise_for_status()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Error connecting to external service: {exc}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    return response.json()


@fights_router.get("/fights/randomfighters")
async def random_fighters()-> JSONResponse:
    logger.info("Fetching random fighters from external service")
    """Fetch two random fighters from external service."""
    hero = await get_hero()
    villain = await get_villain()
    return JSONResponse({"hero": hero, "villain": villain})

@fights_router.get("/fights/randomlocation")
async def random_location()-> JSONResponse:
    logger.info("Fetching random fight location from external service")
    location = await get_location()

    return JSONResponse(location)

@fights_router.post("/fights")
async def post_fight(request: Request)-> JSONResponse:
    fight_request = await request.json()
    logger.info("Posting new fight")
    hero = fight_request.get("hero")
    villain = fight_request.get("villain")
    hero_level = hero.get("level", 0)
    villain_level = villain.get("level", 0)

    location = fight_request.get("location")
    logger.info(f"Executing fight: {hero['name']} (Level {hero_level}) vs {villain['name']} (Level {villain_level}) at {location['name']}")

    response = {
        "id": str(uuid.uuid4()),  # Generate a unique ID for the fight
        "fight_date": "2023-10-01T12:00:00Z",  # Placeholder for fight date
        "winner_name": hero["name"] if hero_level > villain_level else villain["name"],
        "winner_level": max(hero_level, villain_level),
        "winner_powers": hero.get("powers", "") if hero_level > villain_level else villain.get("powers", ""),
        "winner_picture": hero.get("picture", "") if hero_level > villain_level else villain.get("picture", ""),
        "loser_name": villain["name"] if hero_level > villain_level else hero["name"],
        "loser_level": min(hero_level, villain_level),
        "loser_powers": villain.get("powers", "") if hero_level > villain_level else hero.get("powers", ""),
        "loser_picture": villain.get("picture", "") if hero_level > villain_level else hero.get("picture", ""),
        "winner_team": "heroes" if hero_level > villain_level else "villains",
        "loser_team": "villains" if hero_level > villain_level else "heroes",
        "hero": hero,
        "villain": villain,
        "location": location,
    }

    # Here you would typically process the fight_request and initiate a fight
    return JSONResponse(response, status_code=200)




@fights_router.get("/fights/execute_fight")
async def execute_random_fight()-> JSONResponse:
    logger.info("Executing random fight")
    location = await get_location()
    hero = await get_hero()
    villain = await get_villain()
    hero_level = hero.get("level", 0)
    villain_level = villain.get("level", 0)
    logger.info(f"Executing fight: {hero['name']} (Level {hero_level}) vs {villain['name']} (Level {villain_level}) at {location['name']}")

    response = {
        "id": str(uuid.uuid4()),  # Generate a unique ID for the fight
        "fight_date": "2023-10-01T12:00:00Z",  # Placeholder for fight date
        "winner_name": hero["name"] if hero_level > villain_level else villain["name"],
        "winner_level": max(hero_level, villain_level),
        "winner_powers": hero.get("powers", "") if hero_level > villain_level else villain.get("powers", ""),
        "winner_picture": hero.get("picture", "") if hero_level > villain_level else villain.get("picture", ""),
        "loser_name": villain["name"] if hero_level > villain_level else hero["name"],
        "loser_level": min(hero_level, villain_level),
        "loser_powers": villain.get("powers", "") if hero_level > villain_level else hero.get("powers", ""),
        "loser_picture": villain.get("picture", "") if hero_level > villain_level else hero.get("picture", ""),
        "winner_team": "heroes" if hero_level > villain_level else "villains",
        "loser_team": "villains" if hero_level > villain_level else "heroes",
        "hero": hero,
        "villain": villain,
        "location": location,
    }


    # response = {
    #     "hero": hero,
    #     "villain": villain,
    #     "location": location
    # }
    # if hero_level > villain_level:
    #     winner = "hero"
    # else:
    #     winner = "villain"
    # return {"winner": winner}
    return JSONResponse(response, status_code=200)

    # return {"hero": hero, "villain": villain, "location": location}

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
