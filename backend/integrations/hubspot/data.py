# Define HubSpot API scopes
HUBSPOT_SCOPES = [
    'crm.objects.contacts.write',
    'crm.objects.contacts.read',
    'crm.objects.companies.write', 
    'crm.objects.companies.read',
    'crm.objects.deals.read',
    'crm.objects.deals.write',
    'crm.objects.users.read',
    'crm.objects.users.write',
    'oauth',
    "tickets",
    "content",
]

# Define optional scopes for HubSpot API
HUBSPOT_OPTIONAL_SCOPES = []

# Define field mappings for different HubSpot object types
HUBSPOT_FIELD_MAPPINGS = {
    'objects/contacts': {
        'id': ['id'],
        'type': lambda data: 'Contact',
        'directory': lambda data: False,
        'name': {
            'paths': [['properties', 'firstname'], ['properties', 'lastname']],
            'transform': 'join_names'
        },
        'creation_time': ['createdAt'],
        'last_modified_time': ['updatedAt'],
        'url': {
            'paths': [['properties', 'email']],
            'transform': 'url_email'
        },
        'visibility': {
            'paths': [['archived']],
            'transform': 'bool_inverse'
        },
        'mime_type': lambda data: 'application/vnd.hubspot.contact'
    },
    'objects/companies': {
        'id': ['id'],
        'type': lambda data: 'Company',
        'directory': lambda data: False,
        'name': ['properties', 'name'],
        'creation_time': [
            ['createdAt'],
            ['properties', 'createdate']
        ],
        'last_modified_time': [
            ['updatedAt'],
            ['properties', 'hs_lastmodifieddate']
        ],
        'url': {
            'paths': [['properties', 'domain']],
            'transform': 'url_domain'
        },
        'visibility': {
            'paths': [['archived']],
            'transform': 'bool_inverse'
        },
        'mime_type': lambda data: 'application/vnd.hubspot.company'
    },
    'objects/deals': {
        'id': ['id'],
        'type': lambda data: 'Deal',
        'directory': lambda data: False,
        'name': ['properties', 'dealname'],
        'creation_time': [
            ['createdAt'],
            ['properties', 'createdate']
        ],
        'last_modified_time': [
            ['updatedAt'],
            ['properties', 'hs_lastmodifieddate']
        ],
        'visibility': {
            'paths': [['archived']],
            'transform': 'bool_inverse'
        },
        'mime_type': lambda data: 'application/vnd.hubspot.deal'
    },
    "pages/site-pages": {
        'id': ['id'],
        'type': lambda data: 'SitePage',
        'directory': lambda data: False,
        'name': [ 'htmlTitle'],
        'creation_time': [
            ['createdAt'],
            ['properties', 'hs_createdate']
        ],
        'last_modified_time': [
            ['updatedAt'],
            ['properties', 'hs_lastmodifieddate']
        ],
        'url': ['url'],
        'visibility': ["published"],
        'parent_path_or_name': ['name'],
        'parent_id': ['createdById'],
        'mime_type': lambda data: 'application/vnd.hubspot.sitepage'
    }
}