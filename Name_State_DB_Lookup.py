import shelve
from rapidfuzz import process, fuzz

def clean_token(s):
    if not s or not isinstance(s, str):
        return ""
    # Strip, uppercase, replace slashes/pipes/commas with space, and collapse extra whitespace
    cleaned = s.replace('/', ' ').replace('|', ' ').replace(',', ' ').replace('-', ' ').strip().upper()
    return " ".join(cleaned.split())

def lookup_firm(advisor_name, state, shelve_filename="name_state_to_firm_db", threshold=80):
    """
    Looks up an advisor by name and state in the 2D partitioned shelve database.
    
    Returns a tuple: (firm_records, match_confidence_score, matched_db_name)
    - firm_records: list of matching dicts (or None if not found)
    - match_confidence_score: float from 0.0 to 100.0
    - matched_db_name: exact string key in the DB that matched
    """
    cleaned_name = clean_token(advisor_name)
    cleaned_state = clean_token(state)
    
    if not cleaned_name or not cleaned_state:
        return None, 0.0, None
        
    tokens = cleaned_name.split()
    if not tokens:
        return None, 0.0, None
        
    # Determine candidate prefix characters across all tokens (handles Last/First, team names like Rubinstein/Gelbman, etc.)
    candidate_chars = []
    seen_chars = set()
    
    # Prioritize last token first char, then first token first char, then any other tokens
    if len(tokens) >= 2:
        for t in [tokens[-1], tokens[0]] + tokens[1:-1]:
            if t and t[0].isalpha():
                c = t[0]
                if c not in seen_chars:
                    seen_chars.add(c)
                    candidate_chars.append(c)
    else:
        if tokens[0] and tokens[0][0].isalpha():
            candidate_chars.append(tokens[0][0])
            
    if not candidate_chars:
        candidate_chars.append('OTHER')

    try:
        with shelve.open(shelve_filename, flag='r') as db:
            best_overall_score = 0.0
            best_overall_records = None
            best_overall_name = None

            # Check primary candidate prefix partitions
            for char in candidate_chars:
                partition_key = f"STATE_PREFIX|{cleaned_state}|{char}"
                if partition_key in db:
                    prefix_dict = db[partition_key]
                    if not prefix_dict:
                        continue
                        
                    # 1. Exact Match Check inside partition
                    if cleaned_name in prefix_dict:
                        return prefix_dict[cleaned_name], 100.0, cleaned_name
                        
                    if len(tokens) >= 2:
                        short_name = f"{tokens[0]} {tokens[1]}"
                        if short_name in prefix_dict:
                            return prefix_dict[short_name], 100.0, short_name
                            
                    # 2. Fuzzy Match inside partition (~3,800 records max even for NY!)
                    result = process.extractOne(
                        cleaned_name, 
                        prefix_dict.keys(), 
                        scorer=fuzz.token_sort_ratio
                    )
                    if result:
                        match_name, score, _ = result
                        if score > best_overall_score:
                            best_overall_score = float(score)
                            best_overall_records = prefix_dict[match_name]
                            best_overall_name = match_name
                            
                            if best_overall_score == 100.0:
                                return best_overall_records, 100.0, best_overall_name

            # Return best match if above threshold
            if best_overall_score >= threshold:
                return best_overall_records, best_overall_score, best_overall_name
            else:
                return None, best_overall_score, best_overall_name
                
    except Exception as e:
        print(f"Error reading database '{shelve_filename}': {e}")
        return None, 0.0, None

def format_firms_output(firm_records):
    """
    Given a list of firm records from DB, formats a unique joined string of firm names.
    """
    if not firm_records:
        return "Not Found"
    
    seen = set()
    firms = []
    for r in firm_records:
        fname = r.get('firm_name', '').strip()
        if fname and fname not in seen:
            seen.add(fname)
            firms.append(fname)
            
    return " | ".join(firms) if firms else "Not Found"

if __name__ == '__main__':
    print("=== Interactive 2D Name + State -> Firm Lookup ===")
    while True:
        try:
            name = input("\nEnter Advisor Name (or 'exit' to quit): ").strip()
            if name.lower() in ('exit', 'q', 'quit'):
                break
            if not name:
                continue
            state = input("Enter State Code (e.g. NE, NY, FL): ").strip()
            if not state:
                continue
                
            records, score, matched_name = lookup_firm(name, state)
            if records:
                firms_str = format_firms_output(records)
                print(f"\n[FOUND] Match: '{matched_name}' (Score: {score:.1f}%)")
                print(f"Firm(s): {firms_str}")
                for i, rec in enumerate(records, 1):
                    print(f"  ({i}) Advisor CRD: {rec.get('crd')} | Firm CRD: {rec.get('firm_crd')} | Reg Date: {rec.get('reg_date')}")
            else:
                print(f"\n[NOT FOUND] No match found above threshold (Best match: '{matched_name}' with score {score:.1f}%)")
        except KeyboardInterrupt:
            break
