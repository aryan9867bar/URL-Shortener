from fastapi import FastAPI, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import string
from db import get_db
from models import Short, URLRequest
from snowflake import SnowflakeGenerator
from utils import encode_base62
from fastapi.responses import RedirectResponse
from redis_client import redis_client
import asyncio
import uuid
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi.middleware.cors import CORSMiddleware

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔥 allow ALL origins
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)
app.state.limiter = limiter
snowflake_gen = SnowflakeGenerator(1)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/{code}")
@limiter.limit("5/second")
async def get_url(request: Request, code: str, db: AsyncSession = Depends(get_db)):

    lock_key = f"lock:{code}"
    cached_url = redis_client.get(code)
    if cached_url:
        return {
            "message": "Cache HIT",
            "url": cached_url
        }

    lock_value = str(uuid.uuid4())
    lock_acquired = redis_client.set(lock_key, lock_value, nx=True, ex=5)

    if lock_acquired:
        try:
            cached_url = redis_client.get(code)
            if cached_url:
                return {
                    "message": "Cache HIT after lock",
                    "url": cached_url
                }

            result = await db.execute(
                select(Short).where(Short.code == code)
            )
            short = result.scalar_one_or_none()

            if not short:
                return {"error": "Not found"}

            redis_client.set(code, short.url, ex=3600)

            return {
                "message": "Cache MISS (DB fetch, lock owner)",
                "url": short.url
            }

        finally:
            current_val = redis_client.get(lock_key)
            if current_val == lock_value:
                redis_client.delete(lock_key)

    else:
        for _ in range(10):  # retries
            await asyncio.sleep(0.2)  # non-blocking

            cached_url = redis_client.get(code)
            if cached_url:
                return {
                    "message": "Cache HIT after wait",
                    "url": cached_url
                }

        #Fallback
        result = await db.execute(
            select(Short).where(Short.code == code)
        )
        short = result.scalar_one_or_none()

        if not short:
            return {"error": "Not found"}

        return {
            "message": "Fallback DB hit",
            "url": short.url
        }


@app.post("/shorten")
@limiter.limit("1/second")
async def create_short(request: Request, url_req: URLRequest, db: AsyncSession = Depends(get_db)):

    #Check if URL already exists
    result = await db.execute(
        select(Short).where(Short.url == url_req.url)
    )
    existing = result.scalar_one_or_none()

    if existing:
        redis_client.set(existing.code, existing.url)

        return {
            "message": "URL already shortened",
            "code": existing.code,
            "url": existing.url
        }

    #Generate Snowflake ID
    unique_id = next(snowflake_gen)

    #Convert to Base62
    code = encode_base62(unique_id)

    #Insert into DB
    new_short = Short(code=code, url=url_req.url)
    db.add(new_short)
    await db.commit()

    redis_client.set(code, url_req.url)

    return {
        "message": "Short URL created",
        "code": code,
        "url": url_req.url
    }