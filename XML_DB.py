import shelve
import xml.etree.ElementTree as ET
from pathlib import Path
import time
import tqdm

def execute_with_countdown(seconds=5):
    print("WARNING: About to run a destructive data operation (Overwriting Database).")
    for i in range(seconds, 0, -1):
        # \r forces the terminal to overwrite the current line
        print(f"\rExecuting in {i} seconds... (Press Ctrl+C to ABORT) ", end="")
        time.sleep(1)
    print("\nCountdown complete. Executing function...")

        
def extract_crd_states(file_path):
    """
    Parses a single XML file and returns a dictionary mapping 
    CRDs to a set of their registered states.
    """
    local_mapping = {}
    
    # iterparse reads sequentially, keeping memory usage near zero
    context = ET.iterparse(file_path, events=("end",))
    
    for event, elem in context:
        if elem.tag == "Indvl":
            info = elem.find("Info")
            
            if info is not None:
                crd = info.get("indvlPK")
                states = set()
                crnt_emps = elem.find("CrntEmps")
                if crnt_emps is not None:
                    for emp in crnt_emps.findall("CrntEmp"):
                        rgstns = emp.find("BrnchOfLocs")
                        if rgstns is not None:
                            for reg in rgstns.findall("BrnchOfLoc"):
                                state = reg.get("state")
                                if state:
                                    states.add(state)
                
                if crd:
                    local_mapping[crd] = list(states) # Convert set to list for shelve storage
            
            # Clear the element from memory once processed
            elem.clear()
            
    return local_mapping

def build_shelve_database(xml_folder, shelve_filename):
    """
    Iterates through all XML files in a folder and saves the 
    mappings into a persistent shelve database.
    """
    xml_files = list(Path(xml_folder).glob("*.xml"))
    
    # Open the shelve database (creates it if it doesn't exist)
    with shelve.open(shelve_filename, flag='n') as db:
        pbar = tqdm(xml_files, desc="Starting...")
        for file_path in pbar:
            pbar.set_description(f"Processing {file_path.name}")
            file_mappings = extract_crd_states(file_path)
            for crd, states in file_mappings.items():
                if crd in db:
                    existing_states = set(db[crd])
                    existing_states.update(states)
                    db[crd] = list(existing_states)
                else:
                    db[crd] = states

    print(f"Finished parsing. Database saved to {shelve_filename}")

if __name__ == '__main__':
    XML_DIRECTORY = r"H:\_INSTITUTIONAL DIVISION\INTERN FOLDER\Adam Neulander\IAPD_Database\IA_INDVL_Feed_04_09_2026"
    SHELVE_DB_NAME = "crd_to_state_db"
    print("WARNING: THIS WILL OVERWRITE THE CURRENT SHELVE DATABASE. PROCEED WITH CAUTION.")
    
    execute_with_countdown(5)
    build_shelve_database(XML_DIRECTORY, SHELVE_DB_NAME)