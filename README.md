# Faculty IP Management Portal

## Description
A web application for managing faculty intellectual property, including Google Scholar integration, patent tracking, and analytics dashboard.

## Features
- Faculty and Admin login
- Google Scholar profile integration
- Patent management and commercialization tracking
- Analytics dashboard for research impact
- Admin dashboard for faculty management

## Tech Stack
- **Frontend:** React, Tailwind CSS
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## Project Structure
```
portal-main/
  backend/
	 server.py
	 requirements.txt
	 .env
  frontend/
	 src/
	 public/
	 package.json
  README.md
```

## Setup Instructions

### Prerequisites
- Node.js and Yarn (or npm)
- Python 3.8+
- MongoDB

### Backend Setup
1. Go to the backend directory:
	```
	cd backend
	```
2. Install dependencies:
	```
	pip install -r requirements.txt
	```
3. Set up your `.env` file:
	```
	MONGO_URL=mongodb://localhost:27017/
	DB_NAME=innovation_db
	```
4. Start the backend server:
	```
	uvicorn server:app --reload --host 0.0.0.0 --port 8000
	```

### Frontend Setup
1. Go to the frontend directory:
	```
	cd frontend
	```
2. Install dependencies:
	```
	yarn install
	```
3. Start the frontend:
	```
	yarn start
	```

## Default Admin Credentials
- **Email:** nit.official@gmail.com
- **Password:** 12345123

## Notes
- Do not commit your `.env` file to GitHub.
- Make sure MongoDB is running before starting the backend.
# Here are your Instructions
