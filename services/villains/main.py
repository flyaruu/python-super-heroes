import os
import asyncio
import asyncpg
import random
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.gzip import GZipMiddleware
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://superman:superman@villains-db:5432/villains_database")
RETRY_TIMEOUT = 10  # seconds
RETRY_INTERVAL = 0.5  # seconds between attempts

# Cache for MAX(id) to reduce database queries - refreshed every 5 minutes
_max_id_cache = {"value": None, "timestamp": 0}
_CACHE_TTL = 300  # 5 minutes

async def startup():
    start_time = asyncio.get_event_loop().time()
    while True:
        try:
            # Reduced connection pool for lower memory footprint
            app.state.pool = await asyncpg.create_pool(
                DATABASE_URL, min_size=2, max_size=20
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
        rows = await conn.fetch("select * from Villain")
        # Eliminate redundant dict conversion - asyncpg records work directly with JSONResponse
        result = []
        for row in rows:
            if "othername" in row:
                # Only convert when field mapping is needed
                row_dict = dict(row)
                row_dict["otherName"] = row_dict.pop("othername")
                result.append(row_dict)
            else:
                result.append(dict(row))
    return JSONResponse(result)

async def get_random_item(request: Request) -> JSONResponse:
    async with app.state.pool.acquire() as conn:
        # Use cached MAX(id) to reduce database load
        import time
        current_time = time.time()
        if _max_id_cache["value"] is None or current_time - _max_id_cache["timestamp"] > _CACHE_TTL:
            max_id_row = await conn.fetchrow("SELECT MAX(id) as max_id FROM Villain")
            max_id = max_id_row['max_id'] if max_id_row and max_id_row['max_id'] else 1
            _max_id_cache["value"] = max_id
            _max_id_cache["timestamp"] = current_time
        else:
            max_id = _max_id_cache["value"]
        
        # Use random offset with LIMIT 1 - more efficient than ORDER BY RANDOM()
        random_id = random.randint(1, max_id)
        row = await conn.fetchrow(
            "SELECT * FROM Villain WHERE id >= $1 LIMIT 1",
            random_id
        )
        
        # Fallback if no result (sparse IDs)
        if not row:
            row = await conn.fetchrow("SELECT * FROM Villain ORDER BY id LIMIT 1")
    
    if not row:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    return JSONResponse(dict(row))

async def get_item(request: Request) -> JSONResponse:
    item_id = int(request.path_params["id"])
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "select * from Villain where id=$1",
            item_id
        )
    if not row:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    
    # Only convert when field mapping is needed
    if "othername" in row:
        row_dict = dict(row)
        row_dict["otherName"] = row_dict.pop("othername")
        return JSONResponse(row_dict)
    return JSONResponse(dict(row))

routes = [
    Route("/api/villains/random_villain", get_random_item, methods=["GET"]),
    Route("/api/villains", list_all, methods=["GET"]),
    Route("/api/villains/{id}", get_item, methods=["GET"]),
]

# Add gzip compression middleware to reduce network I/O
middleware = [
    Middleware(GZipMiddleware, minimum_size=500)
]

app = Starlette(
    debug=False, 
    routes=routes, 
    middleware=middleware,
    on_startup=[startup], 
    on_shutdown=[shutdown]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
