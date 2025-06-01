import os
import asyncio
import asyncpg
import time
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://superman:superman@heroes-db:5432/heroes_database")
RETRY_TIMEOUT = 10  # seconds
RETRY_INTERVAL = 0.5  # seconds between attempts

async def startup():
    start_time = asyncio.get_event_loop().time()
    while True:
        try:
            app.state.pool = await asyncpg.create_pool(
                DATABASE_URL, min_size=10, max_size=50
            )
            # Ensure table exists
            async with app.state.pool.acquire() as conn:
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS items (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT
                    );
                    """
                )
            break  # successful connection
        except (asyncpg.CannotConnectNowError, OSError) as e:
            now = asyncio.get_event_loop().time()
            if now - start_time >= RETRY_TIMEOUT:
                raise RuntimeError(f"Could not connect to database within {RETRY_TIMEOUT} seconds") from e
            await asyncio.sleep(RETRY_INTERVAL)

async def shutdown():
    await app.state.pool.close()


async def list_all(request: Request) -> JSONResponse:
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch("select * from Hero")
        result = []
        for row in rows:
            row_dict = dict(row)
            if "othername" in row_dict:
                row_dict["otherName"] = row_dict.pop("othername")
            result.append(row_dict)
    return JSONResponse(result)

async def get_random_item(request: Request) -> JSONResponse:
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "select * from Hero order by random() limit 1"
        )
    if not row:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    # row.rename("othername", "otherName") 
    # row["otherName"] = row.pop("othername", None)  # remove 'otherName' and add 'othername'
    return JSONResponse(dict(row))

async def get_item(request: Request) -> JSONResponse:
    item_id = int(request.path_params["id"])
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "select * from Hero where id=$1",
            item_id
        )
    if not row:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    row_dict = dict(row)
    if "othername" in row_dict:
        row_dict["otherName"] = row_dict.pop("othername")
    return JSONResponse(row_dict)

routes = [
    Route("/api/heroes/random_hero", get_random_item, methods=["GET"]),
    Route("/api/heroes", list_all, methods=["GET"]),
    Route("/api/heroes/{id}", get_item, methods=["GET"]),
]

app = Starlette(debug=False, routes=routes, on_startup=[startup], on_shutdown=[shutdown])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
