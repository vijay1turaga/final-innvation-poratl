import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import bcrypt
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

async def create_admin_user(email: str, full_name: str, password: str):
    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        print(f"User with email {email} already exists.")
        return

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "full_name": full_name,
        "user_type": "admin",
        "password": hashed_password,
        "created_at": datetime.now(timezone.utc)
    }
    await db.users.insert_one(user)
    print(f"Admin user {email} created successfully.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python create_admin_user.py <email> <full_name> <password>")
        sys.exit(1)
    email = sys.argv[1]
    full_name = sys.argv[2]
    password = sys.argv[3]
    asyncio.run(create_admin_user(email, full_name, password))
