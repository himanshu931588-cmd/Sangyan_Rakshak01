# Sangyan Rakshak

Sangyan Rakshak is a multimodal scam-detection and complaint-preparation platform designed to help users verify suspicious financial and investment claims, assess risk from uploaded media, and generate complaint dossiers for the right regulatory or enforcement channels.

The platform combines a React frontend with a FastAPI backend to provide a fast, user-friendly experience for fraud detection, complaint drafting, and regulatory verification.

## Highlights

- Verify suspicious text and claims against known regulatory or entity patterns
- Detect high-risk scam signals in Hindi and English content
- Analyze uploaded screenshots or audio for scam indicators
- Generate a formal complaint dossier and suggest filing portals
- Provide a modern interactive dashboard for user investigation workflows
- Built for the Indian financial fraud and scam-reporting context

## Tech Stack

### Frontend
- React + TypeScript
- Vite
- Tailwind CSS
- Framer Motion
- React Three Fiber / Drei

### Backend
- Python
- FastAPI
- SQLAlchemy / SQLite
- Pydantic Settings
- Async database setup

## Project Structure

```text
SANGYAN/
├── backend/
│   ├── database/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── config.py
│   └── main.py
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── tests/
├── .gitignore
├── alembic.ini
├── requirements.txt
├── README.md
└── .env.example (if added later)
```

## Features

### 1. Scam Verification Engine
The backend can evaluate suspicious text and return risk verdicts such as SAFE, SUSPICIOUS, HIGH_RISK, or CRITICAL_FRAUD.

### 2. Media-Based Analysis
Users can upload screenshots or audio content, and the service extracts text and signals associated with scam patterns.

### 3. Regulatory Dossier Generation
For grievance cases, the system creates structured dossiers and recommends the likely filing portal such as SEBI SCORES or cybercrime channels.

### 4. Investigative Dashboard
The frontend presents a streamlined user workflow for verifying entities, reviewing scam indicators, and preparing formal complaint materials.

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/himanshu931588-cmd/Sangyan_Rakshak01.git
cd Sangyan_Rakshak01
```

### 2. Set up the backend

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn backend.main:app --reload
```

API documentation will be available at:

- http://localhost:8000/docs
- http://localhost:8000/redoc

### 3. Set up the frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will typically run at:

- http://localhost:5173

## Testing

Run the backend test suite from the project root:

```bash
pytest -q
```

## Environment Notes

The project uses local SQLite storage by default for development, which makes local testing and demos simple.

## Contribution

Contributions are welcome. Please open an issue or propose a change with a clear summary and rationale.

## License

This project is currently distributed for educational and internal project use unless otherwise specified by the repository owner.

## Project Status

This repository is a working prototype focused on scam-risk detection and grievance workflow support for financial fraud investigation use cases.
