# 🚀 Quick Start Guide

## For Replit

1. **Click "Run"** button
2. Wait for setup to complete
3. Update `Trawell-BE/.env` with your API keys
4. Click "Run" again

## For Local Development

```bash
# First time setup
bash setup.sh

# Start application
npm start
# or
bash run.sh

# Open in browser
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Commands Reference

```bash
npm start              # Start both services
npm run backend        # Backend only
npm run frontend       # Frontend only
bash health-check.sh   # Check if services are running
```

## Required API Keys

Get your keys from:
- OpenAI: https://platform.openai.com/api-keys
- Google Maps: https://console.cloud.google.com/
- Amadeus: https://developers.amadeus.com/
- WeatherAPI: https://www.weatherapi.com/
- Supabase: https://supabase.com/

## Troubleshooting

**Services won't start?**
```bash
# Check if ports are free
lsof -i :8000
lsof -i :5173

# Kill if needed
lsof -ti :8000 | xargs kill -9
lsof -ti :5173 | xargs kill -9
```

**Python issues?**
```bash
cd Trawell-BE
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Node issues?**
```bash
cd Trawell-FE
rm -rf node_modules package-lock.json
npm install
```

## File Structure

```
Trawell/
├── run.sh              ← Main entry point
├── setup.sh            ← First-time setup
├── package.json        ← Root dependencies
├── Trawell-BE/         ← Python backend
└── Trawell-FE/         ← React frontend
```

## Environment Files

**Backend** (`Trawell-BE/.env`):
- OPENAI_API_KEY
- GOOGLE_MAPS_API_KEY
- AMADEUS_CLIENT_ID
- AMADEUS_CLIENT_SECRET
- WEATHERAPI_KEY
- SUPABASE_URL
- SUPABASE_KEY

**Frontend** (`Trawell-FE/.env`):
- VITE_API_URL=http://localhost:8000
- VITE_WS_URL=ws://localhost:8000

---

Need help? Check the main [README.md](README.md)
