import os
import asyncio
import aiomysql
import logging
import random
import time
from urllib.parse import urlparse, unquote

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.gzip import GZipMiddleware
from dotenv import load_dotenv

load_dotenv()


# Configure logging - set to WARNING to reduce overhead
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Parse connection URL once at module level
MYSQL_URL = os.getenv("MYSQL_URL", "mysql://locations:locations@localhost/locations_database")
parsed = urlparse(MYSQL_URL)
DB_USER = unquote(parsed.username)
DB_PASSWORD = unquote(parsed.password)
DB_HOST = parsed.hostname
DB_PORT = parsed.port or 3306
DB_NAME = parsed.path.lstrip("/")

RETRY_TIMEOUT = 30  # seconds
RETRY_INTERVAL = 0.5  # seconds between attempts

# Cache for MAX(id) to reduce database queries - refreshed every 5 minutes
_max_id_cache = {"value": None, "timestamp": 0}
_CACHE_TTL = 300  # 5 minutes


async def startup():
    """Try to connect and create table, retrying for up to 20 seconds."""
    # Use pre-parsed connection parameters
    conn_kwargs = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "db": DB_NAME,
        "minsize": 1,
        "maxsize": 10,
    }

    deadline = time.monotonic() + 20.0
    last_exc = None

    while time.monotonic() < deadline:
        try:
            pool = await aiomysql.create_pool(**conn_kwargs)
            # ensure table exists
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        select count(*) from locations;
                    """)
            app.state.pool = pool
            return
        except Exception as e:
            last_exc = e
            await asyncio.sleep(0.5)

    # if we get here, we never connected
    raise RuntimeError(f"Could not connect to MySQL within 20s: {last_exc!r}")


async def shutdown():
    await app.state.pool.close()

async def list_all(request: Request) -> JSONResponse:
    async with app.state.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("select * from Location")
            rows = await cur.fetchall()
    return JSONResponse(rows)

async def thing(request: Request) -> JSONResponse:
    return JSONResponse({"message": "This is a thing"})

async def get_random_item(request: Request) -> JSONResponse:
    async with app.state.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # Use cached MAX(id) to reduce database load
            current_time = time.time()
            if _max_id_cache["value"] is None or current_time - _max_id_cache["timestamp"] > _CACHE_TTL:
                await cur.execute("SELECT MAX(id) as max_id FROM locations")
                max_id_row = await cur.fetchone()
                max_id = max_id_row['max_id'] if max_id_row and max_id_row['max_id'] else 1
                _max_id_cache["value"] = max_id
                _max_id_cache["timestamp"] = current_time
            else:
                max_id = _max_id_cache["value"]
            
            # Use random offset with LIMIT 1 - more efficient than ORDER BY RAND()
            random_id = random.randint(1, max_id)
            await cur.execute(
                "SELECT * FROM locations WHERE id >= %s LIMIT 1",
                (random_id,)
            )
            row = await cur.fetchone()
            
            # Fallback if no result (sparse IDs)
            if not row:
                await cur.execute("SELECT * FROM locations ORDER BY id LIMIT 1")
                row = await cur.fetchone()
    
    if not row:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    # Eliminate redundant dict conversion - DictCursor already returns dict
    return JSONResponse(row)

async def get_item(request: Request) -> JSONResponse:
    item_id = int(request.path_params["id"])
    async with app.state.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
            "select * from Location where id=%s",
                (item_id,),
            )
            row = await cur.fetchone()
    if not row:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    # DictCursor already returns dict - no conversion needed
    return JSONResponse(row)

routes = [
    Route("/thing", thing, methods=["GET"]),
    Route("/api/locations/random_location", get_random_item, methods=["GET"]),
    Route("/api/locations", list_all, methods=["GET"]),
    Route("/api/locations/{id}", get_item, methods=["GET"]),
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
