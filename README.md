# SwipeRepublic - FastAPI Backend

<img src="pictures/SwipeRepublic.png" alt="SwipeRepublic Logo" width="200"/>

> Just a swipe away from investing in you

This is a cross-platform FastAPI backend that powers the SwipeRepublic application - a stock discovery and financial
literacy platform developed for Trade Republic as part of the CDTM HACK 2025.

## 📱 About SwipeRepublic

SwipeRepublic introduces three key features to make investing more accessible and engaging:

1. **Swipeable Stock Discovery** - Explore unfamiliar stocks with a familiar swiping interface
2. **Personalized News** - Get tailored financial insights based on your watchlist
3. **Yearly Investment Recap** - See your investment journey through shareable story-like recaps

## 🚀 Quick Start

### Option 1: Using Python (requires Python 3.11+)

1. Clone this repository
   ```bash
   git clone https://github.com/CDTMFloMooJaKa/CDTMBackend.git
   cd CDTMBackend
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment
    - Windows: `venv\Scripts\activate`
    - macOS/Linux: `source venv/bin/activate`

4. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

5. Start the server
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
   ```

## 📚 API Documentation

Once the server is running, you can access:

- API endpoint: http://localhost:8080
- Swagger UI documentation: http://localhost:8080/docs
- ReDoc documentation: http://localhost:8080/redoc

## 🔧 Development

The server automatically reloads when you make changes to any Python file in the project.

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # Main FastAPI application
│   ├── config.py        # Application settings
│   ├── routers/         # API routes
│   │   ├── __init__.py
│   │   ├── items.py     # Example CRUD routes
│   │   ├── stocks.py    # Stock discovery endpoints
│   │   ├── insights.py  # Personalized news endpoints
│   │   └── recap.py     # Yearly recap endpoints
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   ├── stock_service.py
│   │   ├── news_service.py
│   │   └── recap_service.py
│   └── models/          # Pydantic models
│       ├── __init__.py
│       ├── item.py      # Example data models
│       ├── stock.py     # Stock data models
│       ├── news.py      # News data models
│       └── recap.py     # Recap data models
├── tests/               # Unit and integration tests
│   ├── __init__.py
│   ├── test_stocks.py
│   ├── test_insights.py
│   └── test_recap.py
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
└── README.md            # Project documentation
```

## 🚢 Deployment

The backend is deployed on Render, while the frontend is hosted on Vercel.

- Live Frontend Demo: https://trade-republic-replica-ui.vercel.app/

## 💻 Tech Stack

### Backend

- FastAPI (Python web framework)
- Pydantic (Data validation)
- SQLAlchemy (ORM, optional)
- Uvicorn (ASGI server)

### Frontend

- TypeScript
- React
- Vite
- TailwindCSS

## ⚙️ Configuration

Environment variables can be set in a `.env` file:

```
DATABASE_URL=sqlite:///./app.db
API_KEY=your_api_key_here
DEBUG=True
```

## 🔍 Troubleshooting

- **Port conflict**: If port 8080 is already in use, change the port in `docker-compose.yml` or in the uvicorn command.
- **Docker issues**: Make sure Docker is running and you have appropriate permissions.
- **Dependency issues**: Ensure you're using Python 3.8 or newer and have all dependencies installed.
- **CORS errors**: If you're experiencing CORS issues when connecting with the frontend, check the CORS settings in
  `app/main.py`.

## 🌟 Team

**Team LMUnicorns - CDTM HACK 2025**
<p align="left">
  <img src="pictures/LMUUnicornsLogo.png" alt="LMUnicorns Logo" width="200"/>
</p>

- Florian Korn
- Joseph Zgawlik
- Kai Ponel
- Mohamed Islam

## 📄 Project Information

- **Assigned Case:** Trade Republic
- **Team Name:** LMUnicorns
- **Project Name:** SwipeRepublic
- **Pitch Video:** https://youtu.be/QG_v-Zfu9i4
- **Demo:** https://trade-republic-replica-ui.vercel.app/
- **GitHub Repositories:**
    - Frontend: https://github.com/CDTMFloMooJaKa/SwipeRepublic
    - Backend: https://github.com/CDTMFloMooJaKa/CDTMBackend

## 📝 License

[MIT License]
