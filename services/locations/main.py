import os
import asyncio
import aiomysql
import logging
import time

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

import urllib

load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Single URL: mysql://user:password@host:port/db
MYSQL_URL = os.getenv("MYSQL_URL", "mysql://locations:locations@localhost/locations_database")
parsed = urlparse(MYSQL_URL)
DB_USER = unquote(parsed.username)
DB_PASSWORD = unquote(parsed.password)
DB_HOST = parsed.hostname
DB_PORT = parsed.port or 3306
DB_NAME = parsed.path.lstrip("/")

RETRY_TIMEOUT = 30  # seconds
RETRY_INTERVAL = 0.5  # seconds between attempts


async def startup():
    """Try to connect and create table, retrying for up to 10 seconds."""
    parsed = urllib.parse.urlparse(MYSQL_URL)
    conn_kwargs = {
        "host": parsed.hostname,
        "port": parsed.port or 3306,
        "user": parsed.username,
        "password": parsed.password,
        "db": parsed.path.lstrip("/"),
        "minsize": 1,
        "maxsize": 10,
    }

    deadline = time.monotonic() + 20.0
    last_exc = None

    while time.monotonic() < deadline:
        try:
            pool = await aiomysql.create_pool(**conn_kwargs)
            # ensure table exists
            logger.info("Creating table if it does not exist")
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
    raise RuntimeError(f"Could not connect to MySQL within 10s: {last_exc!r}")


async def shutdown():
    await app.state.pool.close()

async def list_all(request: Request) -> JSONResponse:
    logger.info("Fetching all locations from the database")
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
            await cur.execute(
                "select * from locations order by rand() limit 1;"
            )
            row = await cur.fetchone()
    if not row:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    return JSONResponse(dict(row))

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
    row_dict = dict(row)
    return JSONResponse(row_dict)

routes = [
    Route("/thing", thing, methods=["GET"]),
    Route("/api/locations/random_location", get_random_item, methods=["GET"]),
    Route("/api/locations", list_all, methods=["GET"]),
    Route("/api/locations/{id}", get_item, methods=["GET"]),
]

app = Starlette(debug=False, routes=routes, on_startup=[startup], on_shutdown=[shutdown])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
