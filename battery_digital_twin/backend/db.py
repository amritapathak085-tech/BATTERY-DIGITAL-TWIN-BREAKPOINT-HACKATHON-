import os
from functools import lru_cache
from supabase import Client, create_client
from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    return create_client(_require_env("SUPABASE_URL"), _require_env("SUPABASE_KEY"))


def table(name: str):
    return get_supabase().table(name)
