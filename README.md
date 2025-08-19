# Cruise Price Tracking Web App
Tracks cruise prices over time and visualises them on a graph.

## Description
This web application allows users to track the prices of different cruises (that have been pre-selected by myself), view them in a table, and see historical price trends on an interactive graph. It's built with a React frontend and a Python/Flask backend.

## Features
- View currently tracked cruises in a table
- Display historical price trends on a line graph
- Add and remove cruises from the graph dynamically to compare

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