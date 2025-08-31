from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import requests
from bs4 import BeautifulSoup
import re
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = "faculty_ip_management_secret_key_2025"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Create the main app without a prefix

app = FastAPI(title="Faculty IP Management System")

# --- Hidden Admin User Creation ---
import asyncio
ADMIN_EMAIL = "nit.official@gmail.com"
ADMIN_PASSWORD = "12345123"
ADMIN_FULL_NAME = "Admin"
ADMIN_TYPE = "admin"

async def ensure_admin_user():
    existing = await db.users.find_one({"email": ADMIN_EMAIL})
    if not existing:
        hashed_password = hash_password(ADMIN_PASSWORD)
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": ADMIN_EMAIL,
            "full_name": ADMIN_FULL_NAME,
            "user_type": ADMIN_TYPE,
            "password": hashed_password,
            "created_at": datetime.now(timezone.utc),
        }
        await db.users.insert_one(admin_user)

@app.on_event("startup")
async def create_admin_on_startup():
    await ensure_admin_user()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

security = HTTPBearer()

# Pydantic Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    user_type: str  # 'faculty' or 'admin'

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    google_scholar_url: Optional[str] = None
    scholar_data: Optional[Dict] = None

class Patent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    faculty_id: str
    title: str
    date_issued: str
    patent_number: Optional[str] = None
    commercialized: bool = False
    commercialization_amount: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PatentCreate(BaseModel):
    title: str
    date_issued: str
    patent_number: Optional[str] = None
    commercialized: bool = False
    commercialization_amount: Optional[float] = None

class ScholarUpdate(BaseModel):
    google_scholar_url: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_info: User

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def scrape_google_scholar(profile_url: str) -> Dict:
    """Scrape Google Scholar profile data"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(profile_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic info
        name_element = soup.find('div', {'id': 'gsc_prf_in'})
        name = name_element.text.strip() if name_element else "Unknown"
        
        # Extract affiliation
        affiliation_element = soup.find('div', class_='gsc_prf_il')
        affiliation = affiliation_element.text.strip() if affiliation_element else "Unknown"
        
        # Extract citation metrics
        citation_table = soup.find('table', {'id': 'gsc_rsb_st'})
        citations = {}
        if citation_table:
            rows = citation_table.find_all('tr')
            for i, row in enumerate(rows[1:]):  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 2:
                    if i == 0:
                        citations['total'] = cells[1].text.strip()
                    elif i == 1:
                        citations['h_index'] = cells[1].text.strip()
                    elif i == 2:
                        citations['i10_index'] = cells[1].text.strip()
        
        # Extract recent publications
        publications = []
        pub_table = soup.find('table', {'id': 'gsc_a_t'})
        if pub_table:
            rows = pub_table.find_all('tr', class_='gsc_a_tr')[:5]  # Get top 5
            for row in rows:
                title_cell = row.find('td', class_='gsc_a_t')
                if title_cell:
                    title_link = title_cell.find('a')
                    title = title_link.text.strip() if title_link else "Unknown"
                    
                    # Get authors and venue
                    author_cell = row.find('div', class_='gs_gray')
                    authors = author_cell.text.strip() if author_cell else "Unknown"
                    
                    # Get year
                    year_cell = row.find('td', class_='gsc_a_y')
                    year = year_cell.text.strip() if year_cell else "Unknown"
                    
                    # Get citations
                    cite_cell = row.find('td', class_='gsc_a_c')
                    cite_link = cite_cell.find('a') if cite_cell else None
                    citation_count = cite_link.text.strip() if cite_link else "0"
                    
                    publications.append({
                        'title': title,
                        'authors': authors,
                        'year': year,
                        'citations': citation_count
                    })
        
        return {
            'name': name,
            'affiliation': affiliation,
            'citations': citations,
            'publications': publications,
            'profile_url': profile_url,
            'scraped_at': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            'error': f"Failed to scrape Google Scholar profile: {str(e)}",
            'profile_url': profile_url,
            'scraped_at': datetime.now(timezone.utc).isoformat()
        }

# Auth Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        user_type=user_data.user_type
    )
    
    user_dict = user.dict()
    user_dict['password'] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    # Create token
    access_token = create_access_token({"sub": user.id})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_type=user.user_type,
        user_info=user
    )

@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    # Find user
    user_data = await db.users.find_one({"email": credentials.email})
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(credentials.password, user_data['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = User(**user_data)
    
    # Create token
    access_token = create_access_token({"sub": user.id})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_type=user.user_type,
        user_info=user
    )

# Faculty Routes
@api_router.get("/faculty/profile", response_model=User)
async def get_faculty_profile(current_user: User = Depends(get_current_user)):
    if current_user.user_type != 'faculty':
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user

@api_router.put("/faculty/scholar")
async def update_scholar_profile(
    scholar_data: ScholarUpdate, 
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != 'faculty':
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Scrape Google Scholar data
    scholar_info = scrape_google_scholar(scholar_data.google_scholar_url)
    
    # Update user record
    await db.users.update_one(
        {"id": current_user.id},
        {
            "$set": {
                "google_scholar_url": scholar_data.google_scholar_url,
                "scholar_data": scholar_info
            }
        }
    )
    
    return {"message": "Google Scholar profile updated successfully", "data": scholar_info}

@api_router.post("/faculty/patents", response_model=Patent)
async def create_patent(
    patent_data: PatentCreate,
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != 'faculty':
        raise HTTPException(status_code=403, detail="Access denied")
    
    patent = Patent(
        faculty_id=current_user.id,
        **patent_data.dict()
    )
    
    await db.patents.insert_one(patent.dict())
    return patent

@api_router.get("/faculty/patents", response_model=List[Patent])
async def get_faculty_patents(current_user: User = Depends(get_current_user)):
    if current_user.user_type != 'faculty':
        raise HTTPException(status_code=403, detail="Access denied")
    
    patents = await db.patents.find({"faculty_id": current_user.id}).to_list(1000)
    return [Patent(**patent) for patent in patents]

# Admin Routes
@api_router.get("/admin/faculty", response_model=List[User])
async def get_all_faculty(current_user: User = Depends(get_current_user)):
    if current_user.user_type != 'admin':
        raise HTTPException(status_code=403, detail="Access denied")
    
    faculty_users = await db.users.find({"user_type": "faculty"}).to_list(1000)
    return [User(**user) for user in faculty_users]

@api_router.get("/admin/faculty/{faculty_id}/patents", response_model=List[Patent])
async def get_faculty_patents_admin(
    faculty_id: str,
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != 'admin':
        raise HTTPException(status_code=403, detail="Access denied")
    
    patents = await db.patents.find({"faculty_id": faculty_id}).to_list(1000)
    return [Patent(**patent) for patent in patents]

def prepare_for_export(data):
    """Convert MongoDB data for JSON serialization"""
    if isinstance(data, list):
        return [prepare_for_export(item) for item in data]
    elif isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key == '_id':  # Skip MongoDB ObjectId
                continue
            result[key] = prepare_for_export(value)
        return result
    elif hasattr(data, 'isoformat'):  # datetime objects
        return data.isoformat()
    else:
        return data

@api_router.get("/admin/faculty/{faculty_id}/export")
async def export_faculty_data(
    faculty_id: str,
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != 'admin':
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get faculty info
    faculty_data = await db.users.find_one({"id": faculty_id, "user_type": "faculty"})
    if not faculty_data:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    # Get patents
    patents = await db.patents.find({"faculty_id": faculty_id}).to_list(1000)
    
    # Clean the data for JSON serialization
    clean_faculty_data = prepare_for_export(faculty_data)
    clean_patents = prepare_for_export(patents)
    
    export_data = {
        "faculty_info": {
            "name": clean_faculty_data.get("full_name"),
            "email": clean_faculty_data.get("email"),
            "google_scholar_url": clean_faculty_data.get("google_scholar_url"),
            "scholar_data": clean_faculty_data.get("scholar_data")
        },
        "patents": clean_patents,
        "exported_at": datetime.now(timezone.utc).isoformat()
    }
    
    return export_data

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()