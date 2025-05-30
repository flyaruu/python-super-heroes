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

async def startup():
    time.sleep(3)
    app.state.pool = await asyncpg.create_pool(DATABASE_URL, min_size=10, max_size=50)
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            """
                SELECT *
                FROM pg_catalog.pg_tables
                WHERE schemaname != 'pg_catalog' AND
                    schemaname != 'information_schema';
            """
        )
async def shutdown():
    await app.state.pool.close()


async def list_all(request: Request) -> JSONResponse:
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch("select * from Hero")
        result = [dict(row) for row in rows]
    return JSONResponse(result)

async def get_random_item(request: Request) -> JSONResponse:
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "select * from Hero order by random() limit 1"
        )
    if not row:
        return JSONResponse({"detail": "Not found"}, status_code=404)
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
    return JSONResponse(dict(row))

routes = [
    Route("/api/heroes", list_all, methods=["GET"]),
    Route("/api/heroes/random_hero", get_item, methods=["GET"]),
    Route("/api/heroes/{id}", get_item, methods=["GET"]),
]

app = Starlette(debug=False, routes=routes, on_startup=[startup], on_shutdown=[shutdown])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
