# slack.py

import json
import secrets
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
import base64
from integrations.integration_item import IntegrationItem

from redis_client import add_key_value_redis, get_value_redis, delete_key_redis
import os
from .data import HUBSPOT_SCOPES, HUBSPOT_OPTIONAL_SCOPES, HUBSPOT_FIELD_MAPPINGS
from .utils import extract_field_value

# HubSpot OAuth credentials - for a real implementation, these should be in environment variables
CLIENT_ID = os.getenv('HUBSPOT_CLIENT_ID')
CLIENT_SECRET = os.getenv('HUBSPOT_CLIENT_SECRET')
REDIRECT_URI = os.getenv('HUBSPOT_REDIRECT_URI')

encoded_client_id_secret = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()

# Create authorization URL with scopes
authorization_url = f'https://app.hubspot.com/oauth/authorize?client_id={CLIENT_ID}' \
    + f'&redirect_uri={REDIRECT_URI}' \
    + f'&scope={"%20".join(HUBSPOT_SCOPES)}' \
    + f'&optional_scopes={"%20".join(HUBSPOT_OPTIONAL_SCOPES)}'

async def authorize_hubspot(user_id, org_id):
    """
    Generate OAuth URL for HubSpot with state parameter for security
    """
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = json.dumps(state_data)
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', encoded_state, expire=600)
    
    return f'{authorization_url}&state={encoded_state}'

async def oauth2callback_hubspot(request: Request):
    """
    Handle OAuth callback from HubSpot
    """
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error'))
    
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    state_data = json.loads(encoded_state)
    
    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')
    
    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')
    
    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')
    
    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                'https://api.hubapi.com/oauth/v1/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'redirect_uri': REDIRECT_URI,
                    'code': code
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            ),
            delete_key_redis(f'hubspot_state:{org_id}:{user_id}')
        )
    
    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(response.json()), expire=600)
    
    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_hubspot_credentials(user_id, org_id):
    """
    Retrieve stored HubSpot credentials from Redis
    """
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    credentials = json.loads(credentials)
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')
    
    return credentials


async def fetch_hubspot_objects(client, domain_type, object_type, headers):
    """
    Fetch objects of a specific type from HubSpot API
    
    Args:
        client: httpx.AsyncClient instance
        domain_type: Domain type for the request (crm, cms)
        object_type: Type of object to fetch (contacts, companies, deals, etc.)
        headers: Request headers including authorization
        
    Returns:
        List of objects of the specified type
    """
    try:
        response = await client.get(
            f'https://api.hubapi.com/{domain_type}/v3/{object_type}',
            headers=headers
        )
        response.raise_for_status()
        return response.json().get('results', []), object_type
    except httpx.HTTPStatusError as e:
        print(f"HTTP error fetching {object_type}: {str(e)}")
        return [], object_type


def create_integration_item_metadata_object(response_json, item_type):
    """
    Create an IntegrationItem object from HubSpot API response
    using declarative field mappings
    """
    
    # Get the field mapping for this item type
    field_mapping = HUBSPOT_FIELD_MAPPINGS.get(item_type, {})
    
    # Extract values for all fields using the mapping
    field_values = {}
    for field, config in field_mapping.items():
        field_values[field] = extract_field_value(response_json, config)
    
    # Create and return the IntegrationItem
    return IntegrationItem(**field_values)


async def get_items_hubspot(credentials):
    """
    Retrieve items from HubSpot API using the provided credentials
    """
    credentials = json.loads(credentials)
    access_token = credentials.get('access_token')
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Define object types to fetch
    object_types = {
        "crm": [
            'objects/contacts',
            'objects/companies',
            'objects/deals',
        ],
        "cms": [
            'pages/site-pages',
        ]
    }
    
    list_of_integration_items = []
    
    # Fetch all object types in parallel
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Create tasks for all object types
        tasks = [
            fetch_hubspot_objects(client, domain_type, object_type, headers)
            for domain_type, object_types in object_types.items() for object_type in object_types
        ]
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks)
        
        # Process results - simplified approach
        list_of_integration_items = [
            create_integration_item_metadata_object(obj, object_type)
            for objects, object_type in results
            if object_type and objects
            for obj in objects
        ]

    
    return list_of_integration_items