# backend/utils/auth.py
from fastapi import Request, HTTPException
from supabase import create_client
import os

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # This must be server-side only
supabase = create_client(supabase_url, supabase_key)

async def get_user_id_from_api_key(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]

    res = supabase.table("api_keys").select("user_id").eq("key", token).single().execute()
    if res.data is None:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return res.data["user_id"]
