def get_value_from_path(data, path):
    """
    Recursively extract a value from a nested dictionary or list using a path
    
    Args:
        data: The dictionary or list to extract from
        path: List of keys/indices to traverse
        
    Returns:
        The value at the given path or None if any part of the path is missing
    """
    if not path or data is None:
        return data
    
    key = path[0]
    
    # Prevent attempts to use unhashable types as dictionary keys
    if isinstance(key, list) or isinstance(key, dict):
        return None
    
    if isinstance(data, dict) and key in data:
        return get_value_from_path(data[key], path[1:])
    elif isinstance(data, list) and isinstance(key, int) and 0 <= key < len(data):
        return get_value_from_path(data[key], path[1:])
    else:
        return None

def apply_transform(value, transform=None):
    """
    Apply a transformation function to a value
    
    Args:
        value: The value to transform
        transform: The name of the transformation to apply
        
    Returns:
        The transformed value
    """
    if not value:
        return None
    if type(value) == list and len(value) == 1:
        value = value[0]
        
    if transform == 'bool_inverse':
        return not value if type(value) == list else not value
    elif transform == 'url_domain':
        return f"https://{value}" if value else None
    elif transform == 'url_email':
        return f"mailto:{value}" if value else None
    elif transform == 'join_names':
        first, last = value
        full = ' '.join(filter(None, [first, last]))
        return full if full else None
    elif callable(transform):
        return transform(value)
    else:
        return value

def extract_field_value(data, field_config):
    """
    Extract a field value from data using the provided field configuration
    Args:
        data: The source data
        field_config: Configuration for field extraction
        
    Returns:
        The extracted and potentially transformed value
    """
    # If field_config is a callable, call it with the data
    if callable(field_config):
        return field_config(data)
    
    # If field_config is a list of alternative paths, try each path in order
    if isinstance(field_config, list) and all(isinstance(p, list) for p in field_config):
        for path in field_config:
            value = get_value_from_path(data, path)
            if value is not None:
                return value
        return None
    
    # If field_config is a list of path elements, get value from that path
    if isinstance(field_config, list):
        return get_value_from_path(data, field_config)
    
    
    # If field_config is a dictionary with paths and transform
    if isinstance(field_config, dict) and 'paths' in field_config:
        paths = field_config['paths']
        transform = field_config.get('transform')
        
        # If paths is a list of paths, get values from all paths
        if all(isinstance(p, list) or p is None for p in paths):
            values = []
            for path in paths:
                if path is None:
                    values.append(None)
                else:
                    values.append(get_value_from_path(data, path))
            
            # Apply transformation if specified
            result = apply_transform(values, transform)
            
            # Apply chained transforms if they exist
            if 'then' in field_config and result is not None:
                next_config = field_config['then']
                next_config['paths'][0] = result  # Set first path to current result
                result = extract_field_value(data, next_config)
            
            return result
        
        # If paths is a single path, get value from that path
        value = get_value_from_path(data, paths)
        return apply_transform(value, transform)
    
    # Default case, return the field_config itself
    return field_config
