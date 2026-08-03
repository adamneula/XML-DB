import shelve

def lookup_crd(crd_number, shelve_filename="crd_to_state_db"):
    """
    Looks up a CRD number in the local shelve database.
    Returns a list of registered states, or None if not found.
    """
    # Open in read-only mode to prevent accidental overwrites
    try:
        with shelve.open(shelve_filename, flag='r') as db:
            # Ensure the input is a string, since shelve requires string keys
            crd_str = str(crd_number)
            
            if crd_str in db:
                return db[crd_str]
            else:
                return None
    except Exception as e:
        print(f"Error accessing database: {e}")
        return None

def get_address(crd_number, shelve_filename="crd_to_state_db"):
    """
    Looks up a CRD number and returns the formatted full address string.
    """
    try:
        with shelve.open(shelve_filename, flag='r') as db:
            data = db.get(str(crd_number))
            if data and isinstance(data, dict):
                return data.get('address', "Address not found")
            return "Address not found"
    except Exception:
        return "Database error"

def get_full_state(crd_number, shelve_filename="crd_to_state_db"):
    """
    Looks up a CRD number and returns the full state name.
    """
    try:
        with shelve.open(shelve_filename, flag='r') as db:
            data = db.get(str(crd_number))
            if data and isinstance(data, dict):
                return data.get('full_state', "State not found")
            return "State not found"
    except Exception:
        return "Database error"

def get_name_and_address(crd_number, shelve_filename="crd_to_state_db"):
    """
    Looks up a CRD number and returns a tuple of (Full Name, Full Address).
    """
    try:
        with shelve.open(shelve_filename, flag='r') as db:
            data = db.get(str(crd_number))
            if data and isinstance(data, dict):
                first = data.get('first_name', '').strip().capitalize()
                last = data.get('last_name', '').strip().capitalize()
                name = f"{first} {last}".strip()
                address = data.get('address', "Address not found")
                return name, address
            return None, None
    except Exception:
        return None, None

if __name__ == '__main__':
    print("=== Interactive CRD Lookup Tool ===")
    while True:
        crd = input("\nEnter a CRD number to look up (or 'exit' to quit): ").strip()
        if crd.lower() in ('exit', 'q', 'quit'):
            break
        if not crd:
            continue
            
        states = lookup_crd(crd)
        if states:
            name, address = get_name_and_address(crd)
            full_state = get_full_state(crd)
            
            print(f"\n[FOUND] CRD {crd} Database Entry:")
            print(f"  Name:       {name}")
            print(f"  Address:    {address}")
            print(f"  Full State: {full_state}")
        else:
            print(f"\n[NOT FOUND] CRD {crd} not found in the database.")