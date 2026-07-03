#!/usr/bin/env python3

"""
Read a GFF file (tab-separated), split the attributes column into multiple
columns, and write an XLSX file with:
  1. Metadata
  2. QTL| <input filename without .gff>

Usage:
    python gff_to_xlsx.py input_file.gff
    python gff_to_xlsx.py input_file.gff --curator "Jane Smith"

Requires:
    pip install pandas openpyxl
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

import pandas as pd


BASE_COLUMNS = [
    "Chromosome",
    "Trait",
    "Qtl_Type",
    "Start",
    "End",
]


def parse_attributes(attr_text: str) -> Dict[str, str]:
    """
    Parse the 9th GFF column, e.g.
      ID=abc;Reference=paper;Name=qtl1;snp=AX-12345
    into:
      {"ID": "abc", "Reference": "paper", "Name": "qtl1", "snp": "AX-12345"}

    Handles trailing ';' and items without '=' by storing them with empty value.
    """
    result: Dict[str, str] = {}

    if pd.isna(attr_text):
        return result

    text = str(attr_text).strip()
    if not text:
        return result

    parts = text.split(";")
    for part in parts:
        part = part.strip()
        if not part:
            continue

        if "=" in part:
            key, value = part.split("=", 1)
            result[key.strip()] = value.strip()
        else:
            result[part.strip()] = ""

    return result


def read_gff_to_dataframe(gff_path: Path) -> pd.DataFrame:
    """
    Read the GFF file, ignoring comment lines and blank lines.
    Convert columns to:
      Chromosome, Trait, Qtl_Type, Start, End, <attributes...>
    """
    rows: List[Dict[str, str]] = []
    attribute_keys: List[str] = []

    with gff_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")

            # Skip blank lines and GFF comment/header lines
            if not line.strip():
                continue
            if line.startswith("#"):
                continue

            fields = line.split("\t")
            if len(fields) < 9:
                # Skip malformed lines
                continue

            chrom = fields[0]
            trait = fields[1]
            qtl_type = fields[2]
            start = fields[3]
            end = fields[4]
            attributes_text = fields[8]

            attributes = parse_attributes(attributes_text)

            # Accumulate attribute column names in first-seen order
            for key in attributes:
                if key not in attribute_keys:
                    attribute_keys.append(key)

            row = {
                "Chromosome": chrom,
                "Trait": trait,
                "Qtl_Type": qtl_type,
                "Start": start,
                "End": end,
            }
            row.update(attributes)
            rows.append(row)

    df = pd.DataFrame(rows)

    # Ensure all expected columns exist, in desired order
    ordered_columns = BASE_COLUMNS + attribute_keys
    for col in ordered_columns:
        if col not in df.columns:
            df[col] = ""

    df = df[ordered_columns]

    # Convert Start/End to numeric where possible
    for col in ["Start", "End"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def make_metadata_dataframe(sheet_name: str, curator: str) -> pd.DataFrame:
    """
    Create the Metadata worksheet contents:
      Field    QTL| filename
      Crop     Wheat
      parentName Triticum_aestivum_IWGSC_RefSeq_v1.0
      Curator  <curator>
    """
    return pd.DataFrame(
        [
            ["Field", sheet_name],
            ["Crop", "Wheat"],
            ["parentName", "Triticum_aestivum_IWGSC_RefSeq_v1.0"],
            ["Curator", curator],
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a GFF file to an XLSX file with Metadata and QTL worksheets."
    )
    parser.add_argument("input_gff", help="Input .gff file")
    parser.add_argument(
        "--curator",
        default="insert the name of the data curator here",
        help="Curator name to write into the Metadata worksheet",
    )
    args = parser.parse_args()

    input_path = Path(args.input_gff)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    base_name = input_path.stem
    output_path = input_path.with_suffix(".xlsx")
    qtl_sheet_name = f"QTL| {base_name}"

    df = read_gff_to_dataframe(input_path)
    metadata_df = make_metadata_dataframe(qtl_sheet_name, args.curator)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        metadata_df.to_excel(
            writer,
            sheet_name="Metadata",
            index=False,
            header=False,
        )
        df.to_excel(
            writer,
            sheet_name=qtl_sheet_name,
            index=False,
        )

    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()

