#!/bin/bash
# Script to initialize the FastAPI Backend project

# Create project directory structure
mkdir -p backend/app/routers backend/app/models

# Create empty __init__.py files
touch backend/app/__init__.py
touch backend/app/routers/__init__.py
touch backend/app/models/__init__.py

# Create main application file
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import items
from .config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Backend. Visit /docs for API documentation."}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
EOF

# Create configuration file
cat > backend/app/config.py << 'EOF'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "HCA FastAPI Backend"
    PROJECT_DESCRIPTION: str = "A cross-platform FastAPI backend with live reload capability"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
EOF

# Create router file
cat > backend/app/routers/items.py << 'EOF'
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from ..models.item import Item, ItemCreate, ItemUpdate

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

# Mock database
fake_items_db = {}
item_id_counter = 1

@router.post("/", response_model=Item, status_code=201)
async def create_item(item: ItemCreate):
    global item_id_counter
    item_id = item_id_counter
    item_id_counter += 1
    item_dict = item.model_dump()
    fake_items_db[item_id] = Item(id=item_id, **item_dict)
    return fake_items_db[item_id]

@router.get("/", response_model=List[Item])
async def read_items(skip: int = 0, limit: int = 10):
    return list(fake_items_db.values())[skip : skip + limit]

@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: int):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_items_db[item_id]

@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemUpdate):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    stored_item = fake_items_db[item_id]
    update_data = item.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(stored_item, field, value)
    
    fake_items_db[item_id] = stored_item
    return stored_item

@router.delete("/{item_id}", response_model=Item)
async def delete_item(item_id: int):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = fake_items_db[item_id]
    del fake_items_db[item_id]
    return item
EOF

# Create model file
cat > backend/app/models/item.py << 'EOF'
from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None

class Item(ItemBase):
    id: int
    
    class Config:
        from_attributes = True
EOF

# Create requirements.txt
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.23.2
pydantic==2.4.2
pydantic-settings==2.0.3
python-dotenv==1.0.0
EOF

# Create Dockerfile
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
EOF

# Create docker-compose.yml
cat > backend/docker-compose.yml << 'EOF'
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
    environment:
      - PROJECT_NAME=HCA FastAPI Backend
      - VERSION=0.1.0
EOF

# Create README.md
cat > backend/README.md << 'EOF'
# FastAPI Backend for HCA Project

This is a cross-platform FastAPI backend that can be easily set up on Windows, macOS, and Linux. The API is accessible on localhost:8080 and supports live code refresh during development.

## Features

- FastAPI framework for high-performance API development
- Cross-platform compatibility (Windows, macOS, Linux)
- API accessible on localhost:8080
- Automatic API documentation with Swagger UI
- Live code refresh for development
- Docker support for consistent environments
- Simple CRUD example implementation

## Quick Start

### Option 1: Using Python (requires Python 3.8+)

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
   ```

### Option 2: Using Docker (recommended for team consistency)

1. Make sure you have Docker and Docker Compose installed
2. Clone this repository
3. Build and start the container:
   ```bash
   docker-compose up
   ```

## API Documentation

Once the server is running, you can access:
- API endpoint: http://localhost:8080
- Swagger UI documentation: http://localhost:8080/docs
- ReDoc documentation: http://localhost:8080/redoc

## Development

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
│   │   └── items.py     # Example CRUD routes
│   └── models/          # Pydantic models
│       ├── __init__.py
│       └── item.py      # Example data models
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
└── README.md           # Project documentation
```

### Adding New Routes

1. Create a new file in the `app/routers/` directory
2. Define your router and endpoints
3. Include your router in `app/main.py`

### Testing the API

You can use tools like curl, Postman, or the built-in Swagger UI to test your API endpoints.

Example:
```bash
# Get all items
curl -X GET http://localhost:8080/items

# Create a new item
curl -X POST http://localhost:8080/items -H "Content-Type: application/json" -d '{"name": "Test Item", "description": "This is a test item", "price": 9.99}'
```

## Troubleshooting

- **Port conflict**: If port 8080 is already in use, change the port in `docker-compose.yml` or in the uvicorn command.
- **Docker issues**: Make sure Docker is running and you have appropriate permissions.
- **Dependency issues**: Ensure you're using Python 3.8 or newer and have all dependencies installed.

## License

[MIT License]
EOF

echo "FastAPI Backend project initialized successfully!"
echo "To start the server, navigate to the backend directory and follow the instructions in the README.md file."