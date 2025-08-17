from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from pymongo import MongoClient
from typing import Optional, List
import os
import hashlib
import jwt
import datetime
from datetime import datetime as dt, timedelta
import uuid

# Environment variables
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

# JWT Secret
JWT_SECRET = "pbr_vits_ai_dept_secret_key_2024"
JWT_ALGORITHM = "HS256"

app = FastAPI(title="Dept-AI Hub - PBR VITS API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
try:
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Collections
    users_collection = db.users
    notices_collection = db.notices
    events_collection = db.events
    timetables_collection = db.timetables
    resources_collection = db.resources
    faculty_collection = db.faculty
    
    print(f"Connected to MongoDB: {MONGO_URL}")
except Exception as e:
    print(f"MongoDB connection error: {e}")

# Security
security = HTTPBearer()

# Pydantic models
class UserLogin(BaseModel):
    roll_no: str
    password: str

class UserCreate(BaseModel):
    roll_no: str
    name: str
    semester: str
    section: str
    role: str = "student"

class Notice(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    category: str
    date: str
    pdf_url: Optional[str] = None

class Event(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    date: str
    location: str
    rsvp_link: Optional[str] = None

class TimetableEntry(BaseModel):
    id: Optional[str] = None
    day: str
    time: str
    subject: str
    faculty: str
    semester: str
    section: str

class Resource(BaseModel):
    id: Optional[str] = None
    title: str
    subject: str
    semester: str
    file_url: str
    uploaded_by: str
    upload_date: str

class Faculty(BaseModel):
    id: Optional[str] = None
    name: str
    designation: str
    email: str
    photo_url: Optional[str] = None
    linkedin: Optional[str] = None

# Helper functions
def create_jwt_token(roll_no: str, role: str) -> str:
    payload = {
        "roll_no": roll_no,
        "role": role,
        "exp": datetime.datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token_data = verify_jwt_token(credentials.credentials)
    user = users_collection.find_one({"roll_no": token_data["roll_no"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Initialize with sample data
@app.on_event("startup")
async def startup_event():
    # Import student data
    import sys
    sys.path.append('/app')
    from student_data import STUDENT_DATA, ADMIN_DATA
    
    # Clear existing users (optional - remove this line if you want to keep existing data)
    # users_collection.delete_many({})
    
    # Create students from STUDENT_DATA
    for roll_no, student_info in STUDENT_DATA.items():
        existing = users_collection.find_one({"roll_no": roll_no})
        if not existing:
            student_data = {
                "roll_no": roll_no,
                "name": student_info["name"],
                "semester": student_info["semester"],
                "section": student_info["section"],
                "role": "student"
            }
            users_collection.insert_one(student_data)
    
    # Create admin from ADMIN_DATA
    for roll_no, admin_info in ADMIN_DATA.items():
        existing = users_collection.find_one({"roll_no": roll_no})
        if not existing:
            admin_data = {
                "roll_no": roll_no,
                "name": admin_info["name"],
                "semester": admin_info.get("semester", ""),
                "section": admin_info.get("section", ""),
                "role": admin_info.get("role", "admin")
            }
            users_collection.insert_one(admin_data)
    
    # Sample notices
    sample_notices = [
        {
            "id": str(uuid.uuid4()),
            "title": "Mid-Term Examinations Schedule",
            "description": "Mid-term examinations for AI Department will commence from March 15, 2024. All students are required to check their hall tickets online.",
            "category": "Exams",
            "date": "2024-03-01"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Guest Lecture on Machine Learning",
            "description": "Distinguished guest lecture by Dr. Sarah Johnson on 'Advanced Machine Learning Techniques' scheduled for March 20, 2024.",
            "category": "Events",
            "date": "2024-03-05"
        }
    ]
    
    for notice in sample_notices:
        existing = notices_collection.find_one({"id": notice["id"]})
        if not existing:
            notices_collection.insert_one(notice)
    
    # Sample events
    sample_events = [
        {
            "id": str(uuid.uuid4()),
            "title": "AI Tech Fest 2024",
            "description": "Annual technical festival showcasing AI projects and innovations by students",
            "date": "2024-03-25",
            "location": "AI Department Auditorium"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Industry Connect Session",
            "description": "Interaction session with AI industry professionals and placement opportunities",
            "date": "2024-03-30",
            "location": "Conference Hall"
        }
    ]
    
    for event in sample_events:
        existing = events_collection.find_one({"id": event["id"]})
        if not existing:
            events_collection.insert_one(event)
    
    # Sample timetable
    sample_timetable = [
        {"id": str(uuid.uuid4()), "day": "Monday", "time": "09:00-10:00", "subject": "Machine Learning", "faculty": "Dr. Smith", "semester": "3", "section": "A"},
        {"id": str(uuid.uuid4()), "day": "Monday", "time": "10:00-11:00", "subject": "Data Structures", "faculty": "Prof. Johnson", "semester": "3", "section": "A"},
        {"id": str(uuid.uuid4()), "day": "Tuesday", "time": "09:00-10:00", "subject": "AI Fundamentals", "faculty": "Dr. Brown", "semester": "3", "section": "A"},
        {"id": str(uuid.uuid4()), "day": "Wednesday", "time": "09:00-10:00", "subject": "Neural Networks", "faculty": "Prof. Davis", "semester": "3", "section": "A"},
    ]
    
    for entry in sample_timetable:
        existing = timetables_collection.find_one({"id": entry["id"]})
        if not existing:
            timetables_collection.insert_one(entry)
    
    # Sample faculty
    sample_faculty = [
        {
            "id": str(uuid.uuid4()),
            "name": "Dr. Sarah Smith",
            "designation": "Professor & Head of Department",
            "email": "sarah.smith@pbrvits.edu.in",
            "photo_url": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=300&h=300&fit=crop&crop=face"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Prof. Michael Johnson",
            "designation": "Associate Professor",
            "email": "michael.johnson@pbrvits.edu.in",
            "photo_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=face"
        }
    ]
    
    for faculty in sample_faculty:
        existing = faculty_collection.find_one({"id": faculty["id"]})
        if not existing:
            faculty_collection.insert_one(faculty)

# Auth endpoints
@app.post("/api/auth/login")
async def login(user_data: UserLogin):
    import re
    
    # Check if password matches roll number
    if user_data.password != user_data.roll_no:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Check if roll number matches the pattern 2473A31XXX (where XXX is any 3 digits)
    roll_pattern = r"^2473A31\d{3}$"
    if not re.match(roll_pattern, user_data.roll_no):
        raise HTTPException(status_code=401, detail="Invalid roll number format")
    
    # Check if user exists in database
    user = users_collection.find_one({"roll_no": user_data.roll_no})
    if not user:
        raise HTTPException(status_code=401, detail="Roll number not found. Contact admin.")
    
    # Generate JWT token
    token = create_jwt_token(user["roll_no"], user["role"])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "roll_no": user["roll_no"],
            "name": user["name"],
            "role": user["role"],
            "semester": user.get("semester", ""),
            "section": user.get("section", "")
        }
    }

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {
        "roll_no": current_user["roll_no"],
        "name": current_user["name"],
        "role": current_user["role"],
        "semester": current_user.get("semester", ""),
        "section": current_user.get("section", "")
    }

# Notices endpoints
@app.get("/api/notices")
async def get_notices(current_user: dict = Depends(get_current_user)):
    notices = list(notices_collection.find({}, {"_id": 0}))
    return notices

@app.post("/api/notices")
async def create_notice(notice: Notice, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    notice_dict = notice.dict()
    notice_dict["id"] = str(uuid.uuid4())
    notices_collection.insert_one(notice_dict)
    return {"message": "Notice created successfully", "id": notice_dict["id"]}

# Events endpoints
@app.get("/api/events")
async def get_events(current_user: dict = Depends(get_current_user)):
    events = list(events_collection.find({}, {"_id": 0}))
    return events

@app.post("/api/events")
async def create_event(event: Event, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    event_dict = event.dict()
    event_dict["id"] = str(uuid.uuid4())
    events_collection.insert_one(event_dict)
    return {"message": "Event created successfully", "id": event_dict["id"]}

# Timetable endpoints
@app.get("/api/timetable")
async def get_timetable(current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "student":
        # Filter by student's semester and section
        timetable = list(timetables_collection.find({
            "semester": current_user.get("semester", ""),
            "section": current_user.get("section", "")
        }, {"_id": 0}))
    else:
        # Admin can see all timetables
        timetable = list(timetables_collection.find({}, {"_id": 0}))
    return timetable

# Faculty endpoints
@app.get("/api/faculty")
async def get_faculty(current_user: dict = Depends(get_current_user)):
    faculty = list(faculty_collection.find({}, {"_id": 0}))
    return faculty

# Resources endpoints
@app.get("/api/resources")
async def get_resources(current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "student":
        # Filter by student's semester
        resources = list(resources_collection.find({
            "semester": current_user.get("semester", "")
        }, {"_id": 0}))
    else:
        # Admin can see all resources
        resources = list(resources_collection.find({}, {"_id": 0}))
    return resources

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Dept-AI Hub - PBR VITS API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)