================================================================================
DataNova — Universal CSV Data Intelligence Platform
================================================================================

DataNova is a powerful tool to automatically profile, clean, analyze, visualize, 
and query any CSV dataset using a Python/FastAPI backend and a React frontend.

========================================
PROJECT STRUCTURE
========================================
Both the backend and frontend code are located in this root directory.
- /app          : Backend API logic, data engines, models, and utilities
- /src          : React + Vite frontend source code
- main.py       : The FastAPI server entry point
- requirements.txt: Python backend dependencies
- package.json  : Node/React frontend dependencies

========================================
HOW TO RUN THE PROJECT
========================================

Since this project has two parts (Backend and Frontend), you need to open 
TWO separate terminal windows to run them at the same time. Both terminals 
must be in this root project folder:
d:\Neel College\Projects\Data analytics project

----------------------------------------
STEP 1: Start the Backend (Terminal 1)
----------------------------------------
1. Install the required Python packages (if you haven't already):
   pip install -r requirements.txt

2. Start the FastAPI server using Uvicorn:
   uvicorn main:app --reload

   (The backend will now run on http://localhost:8000)

----------------------------------------
STEP 2: Start the Frontend (Terminal 2)
----------------------------------------
1. Install the required Node packages (if you haven't already):
   npm install

2. Start the Vite React development server:
   npm run dev

   (The frontend will now run on http://localhost:5173)

----------------------------------------
STEP 3: Use the Application
----------------------------------------
Open your web browser and go to:
http://localhost:5173

You can now upload a CSV file and explore the automatic analysis!
