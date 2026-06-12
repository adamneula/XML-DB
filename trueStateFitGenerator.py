import pandas as pd
import openpyxl
import os
from tqdm import tqdm
from CRD_DB_Lookup import lookup_crd

def get_unique_filename(file_path):
    """Checks if a file exists and appends a numeric suffix if it does."""
    if not os.path.exists(file_path):
        return file_path

    # Split into file path/name and the .xlsx extension
    base, extension = os.path.splitext(file_path)
    counter = 1
    
    # Try 'FileName 1.xlsx', 'FileName 2.xlsx', etc.
    new_path = f"{base} {counter}{extension}"
    while os.path.exists(new_path):
        counter += 1
        new_path = f"{base} {counter}{extension}"
        
    return new_path

def cleanName(firstname: str, lastname: str) -> str:
    if firstname and lastname:
        return f"{firstname.split()[0].capitalize()} {lastname.split()[0].capitalize()}"
    return None

def addTrueState(fitPath: str, oldFitPath: str, fitSheet: str = "FIT", oldFitSheet: str = "FIT (LOC)"):
    
    #In progress: pull all old advisors into a hash map of clean name (with helper function) to true state and use that for later logic
    old = pd.read_excel(oldFitPath, sheet_name=oldFitSheet)
    oldDF = pd.DataFrame(old)
    existing_advisors = dict(map(lambda row:))
    
    advisors = {}
    wb = openpyxl.load_workbook(fitPath)
    ws = wb[fitSheet]
    
    target_index = 10 # Column J - Inserting 2 columns before it (pushing existing content back)
    cols_to_insert = 2
    ws.insert_cols(target_index, cols_to_insert)
    ws.cell(row=2, column=target_index).value = "Home State"
    ws.cell(row=2, column=target_index + 1).value = "Full Name"
    
    for row in tqdm(ws.iter_rows(min_row=3, min_col=10, max_col=18), desc="Processing names"): #0 indexes starting with j
        cell_fullname = row[1]  # Column K (11) - Full Name
        cell_CRD = row[2]  # Column L (12) - Source for CRD lookup
        cell_lastname = row[7]  # Column Q (17) - Name Part 2
        cell_firstname = row[8]  # Column R (18) - Name Part 1

        cell_fullname.value = cleanName(cell_firstname.value, cell_lastname.value)
        if cell_fullname.value in advisors and advisors[cell_fullname.value] is not None:
            if lookup_crd(int(cell_CRD.value)) is not None:
                advisors[cell_fullname.value].update(lookup_crd(int(cell_CRD.value)))
        else:
            advisors[cell_fullname.value] = lookup_crd(int(cell_CRD.value))
    
    for row in tqdm(ws.iter_rows(min_row=3, min_col=10, max_col=18), desc="Processing rows"): #0 indexes starting with j
        cell_homestate = row[0]  # Column J (10) - Home State
        cell_fullname = row[1]  # Column K (11) - Full Name
        cell_CRD = row[2]  # Column L (12) - Source for CRD lookup
        cell_lastname = row[7]  # Column Q (17) - Name Part 2
        cell_firstname = row[8]  # Column R (18) - Name Part 1
        
        cell_homestate.value = str(advisors[cell_fullname.value])

        #todo: implement all that logic to decide which to keep; clean up all these calls in for loops
    wb.save(get_unique_filename(fitPath))
    
addTrueState(r"H:\_INSTITUTIONAL DIVISION\INTERN FOLDER\Adam Neulander\IAPD_Database\5-26.xlsx", r"H:\_INSTITUTIONAL DIVISION\INTERN FOLDER\Adam Neulander\IAPD_Database\4-26-FIT-TrueState.xlsx")