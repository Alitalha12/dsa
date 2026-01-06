# Intelligent Public Transport Routing & Simulation System (ITRS)

A smart, DSA-based transport simulation system that manages bus routes, handles passengers, and calculates shortest travel paths using advanced Data Structures and Algorithms.

**Stack:** Nuxt 3 frontend + Python (Flask) backend.

## Features

- **User Management**: Secure login/signup for passengers with admin panel
- **Route Management**: Linked list-based route creation and management
- **Passenger Queue**: Queue data structure for passenger management at stops
- **Ticket System**: Hash table for O(1) ticket verification
- **Graph Algorithms**: Dijkstra's algorithm for shortest path calculation
- **Action History**: Stack-based undo/redo operations
- **Real-time Simulation**: Bus movement and passenger flow simulation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ITRS-Project
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd ../frontend
npm install
```

## Running the app

1. Start the backend API:
```bash
cd backend
python app.py
```

2. Start the Nuxt frontend:
```bash
cd ../frontend
npm run dev
```
