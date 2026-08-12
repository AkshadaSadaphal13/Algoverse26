# Voice-to-Slide-Deck Node

A full-stack hackathon project for AI-powered pay-per-use presentation generation.

This repo includes:

- `backend/` — FastAPI backend with audio upload, duration-based pricing, payment gating, and result generation simulation.
- `frontend/` — React 19 + Vite + Tailwind frontend for upload, payment, processing, and result pages.

## Features

- Upload audio files (`mp3`, `wav`, `m4a`)
- Detect audio duration and calculate USDC pricing
- Create jobs and generate payment requirements
- Enforce HTTP `402 Payment Required` for unpaid jobs
- Simulate payment verification and return a generated result summary
- Full frontend flow from upload to payment to result

## Backend Setup

1. Open a PowerShell terminal in `backend/`
2. Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install backend dependencies:

```powershell
pip install -r requirements.txt
```

4. Copy the env example and configure your database settings:

```powershell
copy .env.example .env
```

5. Update `.env` with your database URL and any Algorand/testnet settings.

6. Run backend tests:

```powershell
pytest -q
```

7. Start the backend server:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend Setup

1. Open a terminal in `frontend/`
2. Install dependencies:

```bash
npm install
```

3. Run the development server:

```bash
npm run dev
```

4. Build for production:

```bash
npm run build
```

## Usage

- Backend API root: `http://127.0.0.1:8000`
- Frontend app: `http://127.0.0.1:5173`
- Use the `/generate` route to upload audio and begin the payment flow.

## Notes

- Payment is currently simulated with a verify endpoint. Real Algorand x402 wallet integration can be added next.
- The result page displays a generated outline summary after payment and processing.
