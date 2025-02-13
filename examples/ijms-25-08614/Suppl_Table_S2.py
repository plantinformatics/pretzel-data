# from https://chatgpt.com/share/67add943-b324-800e-a69f-23208e2847a0

import sys
import pandas as pd

def process_spreadsheets(input_file, output_file, metadata_file):
    # Read the input spreadsheet, skipping the first two rows
    sheet_name = 'Suppl. Table S2'
    df = pd.read_excel(input_file, sheet_name=sheet_name, skiprows=2)
    
    # Rename columns as specified
    column_renames = {
        'saccver': 'Chromosome',
        'sstart': 'Start',
        'send': 'End',
        'qaccver': 'Name'
    }
    df.rename(columns=column_renames, inplace=True)
    
    # Read the metadata sheet from the metadata file
    metadata_sheet = 'Metadata'
    metadata_df = pd.read_excel(metadata_file, sheet_name=metadata_sheet)
    
    # Write to the output spreadsheet
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Alignment| Suppl_Table_S2', index=False)
        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
    
    print(f"Processed data written to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_spreadsheet> <output_spreadsheet> <metadata_spreadsheet>")
        sys.exit(1)
    
    input_spreadsheet = sys.argv[1]
    output_spreadsheet = sys.argv[2]
    metadata_spreadsheet = sys.argv[3]
    
    process_spreadsheets(input_spreadsheet, output_spreadsheet, metadata_spreadsheet)
