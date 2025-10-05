# 🌍 TraWell - AI-Powered Travel Planning

TraWell is an intelligent travel planning application that combines the power of AI with real-time travel data to create personalized trip recommendations and itineraries.

## 🏗️ Project Structure

```
Trawell/
├── Trawell-BE/          # FastAPI Backend
│   ├── app/
│   │   ├── agents/      # AI agents (brainstorm, planning)
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Data models
│   │   ├── services/    # External services (Google Places, Amadeus, etc.)
│   │   └── main.py      # FastAPI application
│   └── requirements.txt
│
├── Trawell-FE/          # React + Vite Frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── api/         # API hooks
│   │   └── main.tsx     # Application entry
│   └── package.json
│
├── package.json         # Root package.json (monorepo)
├── run.sh              # Main runner script
├── setup.sh            # Setup script
└── README.md           # This file
```

## 🚀 Quick Start

### Option 1: Using Replit (Recommended)

1. **Fork or Clone** this repository to Replit
2. **Click "Run"** - Replit will automatically:
   - Install all dependencies
   - Set up environment files
   - Start both backend and frontend
3. **Configure API Keys** in `Trawell-BE/.env`
4. **Restart** to apply changes

### Option 2: Local Development

#### Prerequisites
- Python 3.11+
- Node.js 18+
- npm 9+

#### Installation

```bash
# Run setup script
bash setup.sh

# Or manually:
npm install              # Install root dependencies
cd Trawell-BE && pip install -r requirements.txt
cd ../Trawell-FE && npm install
```

#### Running the Application

```bash
# Start both backend and frontend
npm start
# or
bash run.sh

# Or run separately:
npm run backend    # Backend only (port 8000)
npm run frontend   # Frontend only (port 5173)
```

## 🔑 Environment Variables

### Backend (`Trawell-BE/.env`)

```env
# AI & APIs
OPENAI_API_KEY=your_openai_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
AMADEUS_CLIENT_ID=your_amadeus_id
AMADEUS_CLIENT_SECRET=your_amadeus_secret
WEATHERAPI_KEY=your_weather_api_key

# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Environment
ENVIRONMENT=development
```

### Frontend (`Trawell-FE/.env`)

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 📡 API Endpoints

Once running, access:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## ✨ Features

### 🧠 AI-Powered Brainstorming
- Natural language conversation for travel preferences
- Smart destination recommendations with ratings
- Real-time location photo fetching
- Interactive location selection with 1-3 star ratings

### 📅 Trip Planning
- WebSocket-based real-time chat
- Inline photos of attractions and landmarks
- Automatic data extraction (budget, dates, highlights)
- Flight and hotel integration via Amadeus API
- Weather forecasts for destinations

### 🎨 Modern UI
- Beautiful gradient-based design
- Responsive mobile-first interface
- Real-time streaming responses
- Photo galleries and attraction cards

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **LangChain** - AI agent orchestration
- **OpenAI GPT-4** - Conversational AI
- **Supabase** - PostgreSQL database
- **Google Places API** - Location photos and data
- **Amadeus API** - Flights and hotels
- **WeatherAPI** - Weather forecasts

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **TypeScript** - Type safety
- **TanStack Query** - Data fetching
- **Tailwind CSS** - Styling
- **Lucide Icons** - Icon library

## 📝 Development Scripts

```bash
# Root level
npm start              # Start both services
npm run dev            # Same as start
npm run backend        # Backend only
npm run frontend       # Frontend only
npm run setup          # Run setup script
npm run install:all    # Install all dependencies

# Backend (in Trawell-BE/)
uvicorn app.main:app --reload

# Frontend (in Trawell-FE/)
npm run dev
npm run build
npm run preview
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill processes on ports 8000 and 5173
lsof -ti :8000 | xargs kill -9
lsof -ti :5173 | xargs kill -9
```

### Python Dependencies Issues
```bash
cd Trawell-BE
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node Dependencies Issues
```bash
cd Trawell-FE
rm -rf node_modules package-lock.json
npm install
```

## 🔒 Security Notes

- Never commit `.env` files to version control
- Keep API keys secure and rotate them regularly
- Use environment variables for all sensitive data
- Enable CORS only for trusted domains in production

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review API docs at `/docs` endpoint

---

**Made with ❤️ by the TraWell Team**
