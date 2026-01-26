
"""
Example module demonstrating documentation standards.
"""

def process_data(data: dict, strict: bool = False) -> list:
    """
    Processes the input data and returns a list of results.
    
    Why: We need to normalize data before storage to prevent schema violations.
    
    Args:
        data (dict): The raw input dictionary.
        strict (bool): If True, raises errors on missing keys. Defaults to False.
        
    Returns:
        list: A list of normalized strings.
        
    Raises:
         ValueError: If strict mode is on and keys are missing.
    """
    # Why: Early exit saves processing time for empty inputs
    if not data:
        return []
        
    results = []
    # NOTE: Refactor this loop to use list comprehension once validation logic is stable.
    for key, value in data.items():
        if strict and not value:
             raise ValueError(f"Missing value for {key}")
        results.append(str(value).strip())
        
    return results
