# Cruise Price Tracking Web App
Tracks cruise prices over time and visualises them on a graph.

## Description
This web application allows users to track the prices of different cruises (that have been pre-selected by myself), view them in a table, and see historical price trends on an interactive graph. It's built with a React frontend and a Python/Flask backend.

## Features
- View currently tracked cruises in a table
- Display historical price trends on a line graph
- Add and remove cruises from the graph dynamically to compare

## How the Data is Collected
- The app fetches cruise pricing and cabin information for selected P&O Cruises using a Python script (`price_tracker.py`).  
- The script requests data from P&O's public API endpoints for a set of predefined cruise codes and cabin types.  
- Data includes:
  - Cruise name and ship
  - Departure port and date
  - Duration
  - Cabin type
  - Pricing for different fare types, onboard credits, and drinks packages  

- The script inserts this data into a local SQLite database (`cruises.db`).  
- **Updates Schedule:** The script is run automatically using **Windows Task Scheduler every 3 days**.  
- **Important:** The repository itself does **not include the latest database updates**. Users cloning the repo will only get the current version of `cruises.db` at the time of latest commit.

## Screenshots
### Main Dashboard
![Main Dashboard](frontend/screenshots/dashboard.png)

### Cruise List
![Cruise List](frontend/screenshots/cruiselist.png)

### Price Graph
![Price Graph](frontend/screenshots/pricegraph.png)

## Technologies Used
- Frontend: React, Chart.js
- Backend: Python, Flask, SQLite
- Styling: CSS

## Installation & Setup
### Prerequisites
- [Python 3.x](https://www.python.org/downloads/) (for backend)
- [Node.js & npm](https://nodejs.org/) (for frontend)

### 1. Clone the repository
git clone https://github.com/J-McGurn/Cruise-Price-Tracking-WebApp.git

### 2. Install the python packages used for backend
```bash
cd Cruise-Price-Tracking-WebApp/backend
pip install -r requirements.txt
```

### 3. Frontend setup
```bash
cd../frontend
npm install
```

### 4. Run the App
Run the batch file
```bash
cd..
start_app.bat
```

### 5. Access the App
Open your browser and go to: http://localhost:3000/ to view the Web App

## Disclaimer
- Data is provided for informational purposes only.
- This project is provided for **educational and personal use only**.
- This app currently only tracks **P&O Cruises** for personal reasons.    
- This project is **not affiliated with or endorsed** by P&O Cruises or any other cruise company.  
- Users should **always check the official P&O Cruises website** before making any booking or travel decisions.