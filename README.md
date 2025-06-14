# FTO Navigator: Freedom-to-Operate Analysis for Researchers

FTO Navigator is a web-based tool designed to help researchers perform Freedom-to-Operate (FTO) analysis by searching for potential patent conflicts. Users can input their research details, and the application will analyze the USPTO patent database to generate a risk assessment report.

## ✨ Features

-   **Intuitive Research Form**: Submit your research title, description, field of study, and relevant keywords to start the analysis.
-   **Automated Patent Search**: The backend service queries the USPTO database for relevant patents based on your input.
-   **Risk Assessment**: Analyzes retrieved patents to determine a risk level (HIGH, MEDIUM, LOW) based on factors like keyword overlap, classification match, and recency.
-   **Comprehensive Results**: View an executive summary, a detailed list of relevant patents, and actionable recommendations in a clear, tabbed interface.
-   **Report Generation**: Download the complete analysis as a PDF or JSON file for offline viewing and record-keeping.

## ⚙️ Tech Stack

-   **Frontend**: React, Vite, Axios, react-icons
-   **Backend**: Python, FastAPI, SQLAlchemy, aiosqlite
-   **PDF Generation**: jsPDF, jspdf-autotable

## 📂 Project Structure

```
/
├── backend/         # FastAPI backend
│   ├── main.py      # Main application entrypoint
│   ├── database.py  # Database setup and models
│   └── ...
├── frontend/        # React frontend
│   ├── src/
│   │   ├── App.jsx  # Main React component
│   │   └── ...
│   └── ...
└── README.md
```

## 🚀 Getting Started

### Prerequisites

-   Node.js and npm
-   Python 3.8+ and pip

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the FastAPI server:**
    ```bash
    uvicorn main:app --reload
    ```
    The backend will be running at `http://127.0.0.1:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install the required npm packages:**
    ```bash
    npm install
    ```

3.  **Run the React development server:**
    ```bash
    npm run dev
    ```
    The frontend will be running at `http://localhost:5173` and will connect to the backend service.

### How to Use

1.  Open your web browser and navigate to the frontend URL (e.g., `http://localhost:5173`).
2.  Fill out the "Analyze Your Research" form with your research details.
3.  Click "Analyze Patent Landscape" to submit your research for analysis.
4.  The application will display a loading screen while it searches for and analyzes patents.
5.  Once complete, you can view the risk assessment, patent details, and recommendations in the results view.