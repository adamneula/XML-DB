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

if __name__ == '__main__':
    while True:
        crd = input("Enter a CRD number to look up (or 'exit' to quit): ")
        if crd == 'exit' or crd == 'q':
            break
        states = lookup_crd(crd)
        if states:
            print(f"CRD {crd} found! Registered in: {states}")
        else:
            print(f"CRD {crd} not found in the database.")