# from 
# https://chatgpt.com/share/67b1a57e-1558-800e-8b4c-f82ec4366e41
# https://chatgpt.com/canvas/shared/67b13c8e36c08191a0abc553359812c1

import sys
import os
import pandas as pd

def extract_tissue_name(bed_filename):
    """Extracts the tissue name from the BED filename."""
    suffix = "_2024-05-20_Apollo.BED"
    if bed_filename.endswith(suffix):
        return bed_filename[:-len(suffix)]
    return bed_filename  # Fallback (shouldn't happen with correct files)

def read_bed_file(bed_filename):
    """Reads a BED file and returns a DataFrame with an added Tissue Name column."""
    tissue_name = extract_tissue_name(os.path.basename(bed_filename))
    columns = ['Chromosome', 'Start', 'End', 'Name', 'score', 'strand']
    df = pd.read_csv(bed_filename, sep='\t', names=columns, header=None)
    df['Trait'] = tissue_name
    return df

def process_metadata(metadata_file, writer):
    """Reads the metadata spreadsheet and modifies the header of the second column and appends a row."""
    metadata_df = pd.read_excel(metadata_file, sheet_name='Metadata')
    if not metadata_df.empty and metadata_df.shape[1] > 1:
        metadata_df.columns = [metadata_df.columns[0], "Alignment| Tissue Peptides"]
    new_row = pd.DataFrame({metadata_df.columns[0]: ["tags"], metadata_df.columns[1]: ["QTL"]})
    metadata_df = pd.concat([metadata_df, new_row], ignore_index=True)
    metadata_df.to_excel(writer, sheet_name='Metadata', index=False)

def main():
    if len(sys.argv) < 4:
        print("Usage: python script.py <output.xlsx> <metadata.xlsx> <input1.BED> <input2.BED> ...")
        sys.exit(1)
    
    output_file = sys.argv[1]
    metadata_file = sys.argv[2]
    bed_files = sys.argv[3:]
    
    # Read and merge BED files
    all_data = pd.concat([read_bed_file(f) for f in bed_files], ignore_index=True)
    
    # Write to Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        all_data.to_excel(writer, sheet_name='Alignment| Tissue Peptides', index=False)
        process_metadata(metadata_file, writer)
    
    print(f"Data written to {output_file}")

if __name__ == "__main__":
    main()
