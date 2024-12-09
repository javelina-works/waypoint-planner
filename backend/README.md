# Interactive App Backend

## Backend Setup

backend/
├── app/
│   ├── main.py               # FastAPI entry point
│   ├── routers/
│   │   ├── waypoints.py      # API routes for waypoints
│   ├── models/
│   │   └── waypoint_model.py # SQLite database model
│   ├── services/
│   │   ├── waypoint_service.py # Business logic
│   ├── db.py                 # Database connection setup
│   └── utils/
│       └── geojson_utils.py  # Helper functions for GeoJSON
├── tests/
│   └── test_waypoints.py     # Unit tests
├── requirements.txt          # Dependencies
└── README.md

### Structure
- **Models**: Define the structure of your database and the data your application works with.
    - Database schema: classes that map to DB tables
    - Validation: Attributes like nullable, unique, and default enforce rules at the database level.
- **Routers**: Handle the HTTP API layer, mapping URLs and HTTP methods to business logic.
    - Endpoints: URL paths with associated HTTP methods (GET, POST, etc.).
    - Dependency Injection: Injects shared components like database sessions into services.
    - Validation: Validates and serializes request/response payloads with Pydantic models.
- **Services**: Implement the core business logic and encapsulate operations on models.
    - Business Logic: Code for creating, reading, updating, or deleting records.
    - Data Transformation: Any manipulation needed before data is stored or returned.
    - Database Queries: Code that uses ORM models to interact with the database.



## Running the Server

`uvicorn app.main:app --reload`