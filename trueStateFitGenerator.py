import pandas as pd
import openpyxl
from tqdm import tqdm
from CRD_DB_Lookup import lookup_crd

def addTrueState(fitPath: str, fitSheet: str = "FIT", oldFitSheet: str = "FIT (LOC)"):
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

        cell_fullname.value = f"{cell_firstname.value.strip()} {cell_lastname.value.strip()}" if cell_firstname.value and cell_lastname.value else None
        if cell_fullname.value in advisors and advisors[cell_fullname.value] is not None:
            if lookup_crd(int(cell_CRD.value)) is not None:
                advisors[cell_fullname.value].append(lookup_crd(int(cell_CRD.value)))
        else:
            advisors[cell_fullname.value] = [lookup_crd(int(cell_CRD.value))]
    
    for row in tqdm(ws.iter_rows(min_row=3, min_col=10, max_col=18), desc="Processing rows"): #0 indexes starting with j
        cell_homestate = row[0]  # Column J (10) - Home State
        cell_fullname = row[1]  # Column K (11) - Full Name
        cell_CRD = row[2]  # Column L (12) - Source for CRD lookup
        cell_lastname = row[7]  # Column Q (17) - Name Part 2
        cell_firstname = row[8]  # Column R (18) - Name Part 1
        
        cell_homestate.value = str(advisors[cell_fullname.value])
    
    wb.save(fitPath)
    
addTrueState(r"H:\_INSTITUTIONAL DIVISION\INTERN FOLDER\Adam Neulander\IAPD_Database\5-26.xlsx")