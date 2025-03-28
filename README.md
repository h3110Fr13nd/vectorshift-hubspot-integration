# VectorShift Integration Technical Assessment Setup Guide

This guide will help you set up and run the VectorShift Integration Assessment project. The project consists of a React frontend, FastAPI backend, and Redis for session management.

## Prerequisites

- Node.js (v18 or higher)
- Python (v3.10 or higher)
- Redis
- Docker and Docker Compose (optional, for containerized setup)

## Configuration Setup

1. Create and configure the root level environment file:
   ```bash
   cp .env.example .env
   ```
   Configure in root `.env`:
   ```bash
   FRONTEND_ENV=development    # Environment for frontend (development/production)
   FRONTEND_PORT=3000         # Port for frontend service
   BACKEND_PORT=8000         # Port for backend service
   REDIS_PORT=6379          # Port for Redis service
   ```

2. Create and configure the frontend environment file:
   ```bash
   cd frontend
   cp .env.example .env
   ```
   Configure in frontend `.env`:
   ```bash
   REACT_APP_API_URL=http://localhost:8000  # Backend API URL
   ```

3. Create and configure the backend environment file:
   ```bash
   cd backend
   cp .env.example .env
   ```
   Configure in backend `.env`:
   ```bash
   # Redis Configuration
   REDIS_HOST=redis          # Use 'redis' for docker-compose, 'localhost' for local setup
   REDIS_PORT=6379          # Should match root REDIS_PORT

   # OAuth Credentials
   AIRTABLE_CLIENT_ID=your_client_id
   AIRTABLE_CLIENT_SECRET=your_client_secret
   
   NOTION_CLIENT_ID=your_client_id
   NOTION_CLIENT_SECRET=your_client_secret
   
   HUBSPOT_CLIENT_ID=your_client_id
   HUBSPOT_CLIENT_SECRET=your_client_secret

   # OAuth Redirect URIs (adjust ports if changed in root .env)
   AIRTABLE_REDIRECT_URI=http://localhost:8000/oauth/airtable/callback
   NOTION_REDIRECT_URI=http://localhost:8000/oauth/notion/callback
   HUBSPOT_REDIRECT_URI=http://localhost:8000/oauth/hubspot/callback
   ```

Important Notes:
- For Docker setup, use `REDIS_HOST=redis`
- For local setup, use `REDIS_HOST=localhost`
- Ensure all redirect URIs match your OAuth provider settings
- Keep sensitive credentials secure and never commit .env files to version control
- When changing ports in root `.env`, update corresponding service configurations and redirect URIs

## Option 1: Running with Docker Compose

1. Build and start all services:
   ```bash
   docker compose up --build
   ```

2. Access the application:
   - Frontend: http://localhost:80 (or your configured FRONTEND_PORT)
   - Backend: ${process.env.REACT_APP_API_URL} (or your configured BACKEND_PORT)
   - Redis: localhost:6379 (or your configured REDIS_PORT)

## Option 2: Running Locally

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Start Redis server:
   ```bash
   redis-server
   ```

5. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Verifying the Setup

1. Check if the frontend is running:
   - Open http://localhost:3000 in your browser
   - You should see the integration selection interface

2. Check if the backend is running:
   - Open ${process.env.REACT_APP_API_URL}/health
   - You should see `{"status": "healthy"}`

3. Test Redis connection:
   - Redis should be running on port 6379
   - The backend should be able to connect to Redis for session management

## Troubleshooting

1. Port Conflicts
   - If ports are already in use, modify them in your .env files
   - Remember to update redirect URIs if you change the backend port

2. Redis Connection Issues
   - For local setup: ensure Redis is running (`redis-server`)
   - For Docker: ensure the Redis service is up (`docker-compose ps`)

3. Environment Variables
   - Double-check all credentials in .env files
   - Ensure redirect URIs match your setup
   - Verify REDIS_HOST is set correctly ('redis' for Docker, 'localhost' for local)

## Integration Testing

To test the integrations:

1. Set up developer accounts:
   - Create a HubSpot developer account
   - (Optional) Create Notion and Airtable developer accounts

2. Configure OAuth credentials:
   - Add OAuth credentials to your backend .env file
   - Ensure redirect URIs are correctly configured in the provider dashboards

3. Test the OAuth flow:
   - Click "Connect to HubSpot" in the UI
   - Complete the OAuth authorization
   - Verify the connection status updates

## Additional Notes

- The frontend runs in development mode with hot reloading enabled
- The backend uses FastAPI's automatic reload capability
- Redis persistence is enabled in Docker setup
- Frontend is served through Nginx in Docker setup

## HubSpot Integration Architecture

The HubSpot integration is designed to be highly extensible and maintainable through a declarative field mapping system. This architecture allows for easy addition of new HubSpot API endpoints and object types without changing the core logic.

### Key Features

1. **Declarative Field Mappings**: Field mappings are defined in a configuration object (`HUBSPOT_FIELD_MAPPINGS`) rather than hardcoded in the processing logic.

2. **Parallel API Fetching**: Multiple HubSpot API endpoints are queried concurrently for better performance.

3. **Flexible Data Extraction**: Supports multiple data extraction patterns:
   - Direct field mapping
   - Nested field access
   - Multiple alternative paths
   - Custom transformations
   - Chained transformations

### Adding New HubSpot API Endpoints

To add a new HubSpot API endpoint, follow these steps:

1. Add the endpoint to the `object_types` dictionary in `get_items_hubspot()`:

```python
object_types = {
    "crm": [
        'objects/contacts',
        'objects/companies',
        'objects/deals',
        'your_new_endpoint'  # Add your new endpoint here
    ],
    "cms": [
        'pages/site-pages',
    ]
}
```

2. Define the field mapping in `HUBSPOT_FIELD_MAPPINGS`:

```python
HUBSPOT_FIELD_MAPPINGS = {
    'your_new_endpoint': {
        'id': ['id'],  # Direct field mapping
        'type': lambda data: 'YourType',  # Function mapping
        'name': ['properties', 'name'],  # Nested field mapping
        'creation_time': [  # Multiple alternative paths
            ['createdAt'],
            ['properties', 'createdate']
        ],
        'url': {  # Field with transformation
            'paths': [['properties', 'domain']],
            'transform': 'url_domain'
        },
        'complex_field': {  # Chained transformations
            'paths': [['field1'], ['field2']],
            'transform': 'first_transform',
            'then': {
                'paths': [null],  # Result from previous transform
                'transform': 'second_transform'
            }
        }
    }
}
```

### Field Mapping Options

1. **Direct Field Access**:
```python
'id': ['id']  # Maps to object.id
```

2. **Nested Field Access**:
```python
'name': ['properties', 'firstname']  # Maps to object.properties.firstname
```

3. **Multiple Alternative Paths**:
```python
'creation_time': [
    ['createdAt'],
    ['properties', 'createdate']
]  # Tries each path in order until a value is found
```

4. **Function Mapping**:
```python
'type': lambda data: 'Contact'  # Returns constant value
```

5. **Transformation with Single Path**:
```python
'url': {
    'paths': [['properties', 'domain']],
    'transform': 'url_domain'
}
```

6. **Transformation with Multiple Inputs**:
```python
'name': {
    'paths': [['properties', 'firstname'], ['properties', 'lastname']],
    'transform': 'join_names'
}
```

### Available Transformations

- `bool_inverse`: Inverts a boolean value
- `url_domain`: Prepends 'https://' to a domain
- `url_email`: Prepends 'mailto:' to an email
- `join_names`: Combines first and last names with a space

To add a new transformation, add it to the `apply_transform` function in `utils.py`:

```python
def apply_transform(value, transform=None):
    # ...existing transforms...
    elif transform == 'your_new_transform':
        return your_transform_logic(value)
```

### Best Practices

1. **Field Validation**: Always handle missing or null values gracefully in your field mappings.

2. **Transformation Reuse**: Create reusable transformations for common data patterns.

3. **Documentation**: Document the expected data structure when adding new endpoints.

4. **Testing**: Test your field mappings with sample API responses before deployment.

5. **Extensibility**: This architecture ensures that adding new HubSpot API endpoints is a matter of configuration rather than code changes, making the system highly maintainable and extensible.