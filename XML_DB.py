import shelve
import xml.etree.ElementTree as ET
from pathlib import Path
import time
from tqdm import tqdm

def execute_with_countdown(seconds=5):
    print("WARNING: About to run a destructive data operation (Overwriting Database).")
    for i in range(seconds, 0, -1):
        print(f"\rExecuting in {i} seconds... (Press Ctrl+C to ABORT) ", end="")
        time.sleep(1)
    print("\nCountdown complete. Executing function...")

def extract_crd_states(file_path):
    """
    Parses a single XML file and returns a mapping of CRDs to their Names and Registrations.
    Format: 
    { 
      '1234567891': {
          'first_name': 'FIRST NAME',
          'last_name': 'LAST NAME',
          'registrations': {'1967-08-13': ['AK', 'TX']}
      } 
    }
    """
    local_mapping = {}
    context = ET.iterparse(file_path, events=("end",))
    
    for event, elem in context:
        if elem.tag == "Indvl":
            info = elem.find("Info")
            
            if info is not None:
                crd = info.get("indvlPK")
                # Extract and standardize names (uppercase, stripped of extra spaces)
                first_name = info.get("firstNm", "").strip().upper()
                last_name = info.get("lastNm", "").strip().upper()
                
                date_state_map = {} 
                crnt_emps = elem.find("CrntEmps")
                
                if crnt_emps is not None:
                    for emp in crnt_emps.findall("CrntEmp"):
                        rgstns = emp.find("CrntRgstns")
                        if rgstns is not None:
                            for reg in rgstns.findall("CrntRgstn"):
                                state = reg.get("regAuth")
                                date = reg.get("stDt")
                                
                                if state and date:
                                    if date not in date_state_map:
                                        date_state_map[date] = set()
                                    date_state_map[date].add(state)
                
                if crd and date_state_map:
                    local_mapping[crd] = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'registrations': {d: list(s) for d, s in date_state_map.items()}
                    }
            
            elem.clear()
            
    return local_mapping

def build_shelve_database(xml_folder, shelve_filename):
    xml_files = list(Path(xml_folder).glob("*.xml"))
    
    with shelve.open(shelve_filename, flag='n') as db:
        pbar = tqdm(xml_files, desc="Starting...")
        for file_path in pbar:
            pbar.set_description(f"Processing {file_path.name}")
            file_mappings = extract_crd_states(file_path)
            
            for crd, new_data in file_mappings.items():
                if crd in db:
                    existing_data = db[crd]
                    
                    # Merge chronological registrations
                    for date, states in new_data['registrations'].items():
                        if date in existing_data['registrations']:
                            combined_states = set(existing_data['registrations'][date])
                            combined_states.update(states)
                            existing_data['registrations'][date] = list(combined_states)
                        else:
                            existing_data['registrations'][date] = states
                            
                    db[crd] = existing_data
                else:
                    db[crd] = new_data

    print(f"\nFinished parsing. Database saved to {shelve_filename}")

if __name__ == '__main__':
    XML_DIRECTORY = r"H:\_INSTITUTIONAL DIVISION\INTERN FOLDER\Adam Neulander\IAPD_Database\IA_INDVL_Feed_06_08_2026"
    SHELVE_DB_NAME = "crd_to_state_db"
    print("WARNING: THIS WILL OVERWRITE THE CURRENT SHELVE DATABASE. PROCEED WITH CAUTION.")
    
    execute_with_countdown(5)
    build_shelve_database(XML_DIRECTORY, SHELVE_DB_NAME)