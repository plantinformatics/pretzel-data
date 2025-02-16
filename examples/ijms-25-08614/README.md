# Examples of loading data from published supplementary data

The data included in the supplementary data of science papers varies according to the data methods of the paper.
These datasets can be viewed in Pretzel if they have these columns : Chromosome Start Name.
End is an optional column.
All other columns will be loaded as attributes of the dataset Features, in Feature.values, and will be displayed in the Feature Table when the feature is within the scope of the axis brush.

To enable a spreadsheet to be loaded into Pretzel, suitable columns should be renamed to match that convention : Chromosome Start End Name,
and a Metadata worksheet should be added describing the dataset.
This usually a simple process which can be done manually in a Spreadsheet GUI such as MS Excel or Libre Office Calc.
It can also be done using a Python / Pandas program, which is the approach which is demonstrated by the examples in this directory.
The benefit of this approach is that it can be automatically re-run when a new version of the source spreadsheet becomes available,
and it enables the curation of datasets for Pretzel to be automated.

The 3 Python / Pandas programs shown here were generated using LLMs (OpenAI ChatGPT) to demonstrate that this task can be done with limited programming skills;  the prompt does need to be a good specification of the required data conversion for this to work.


# Source publication

```
 Community Resource: Large-Scale Proteogenomics to Refine Wheat Genome Annotations
 by Delphine Vincent and Rudi Appels
 Int. J. Mol. Sci. 2024, 25(16), 8614
 https://doi.org/10.3390/ijms25168614
 https://www.mdpi.com/1422-0067/25/16/8614
```

"All the results reported in this study are available as Supplementary Files, including all peptide mapping BED files for upload in IGB or T. aestivum Apollo Jbrowse repository (https://bread-wheat-um.genome.edu.au/apollo/49826/jbrowse/), The Python code and Galaxy workflow, as well as BED files are available on GitHub
([`https://github.com/dlf2024/Python_Wheat_Proteogenomics`](https://github.com/dlf2024/Python_Wheat_Proteogenomics) )."



---

# Downloading the supplementary data

```
wget  https://www.mdpi.com/article/10.3390/ijms25168614/s1 -O ijms-25-08614-s001.zip
```
or 
```
curl  https://www.mdpi.com/article/10.3390/ijms25168614/s1 > ijms-25-08614-s001.zip
```


ijms-25-08614-s001.zip contains 
- the BED files : `[0-9]*_2024-05-20_Apollo.BED`
- `Vincent_supplementary-tables_2024-06-05.xlsx`
which contains supplementary tables in these worksheets :
- 'Suppl. Table S1'
- 'Suppl. Table S2'
- 'Suppl. Table S3'

Extract the spreadsheet containing the supplementary data in individual worksheets.
```
unzip ijms-25-08614-s001.zip Vincent_supplementary-tables_2024-06-05.xlsx
```

`Vincent_supplementary-tables_2024-06-05.xlsx` contains worksheets including these :
- 'Suppl. Table S1'
- 'Suppl. Table S2'
- 'Suppl. Table S3'



These files can also be downloaded individually from `https://github.com/dlf2024/Python_Wheat_Proteogenomics` :
- [BED files](https://github.com/dlf2024/Python_Wheat_Proteogenomics/tree/main/BED%20files)
- [IJMS article](https://github.com/dlf2024/Python_Wheat_Proteogenomics/tree/main/IJMS%20article) contains the spreadsheet `Vincent_Appels_Supplementary-Tables_2024-08-08_ijms-25-08614.xlsx`



## Metadata worksheet

A Metadata worksheet is required.  Only the header row and the 'Crop' and 'parentName' rows are required.

| Field	| `Alignment| Tissue Peptides` |
| -- | -- |
| Crop	| Wheat |
| parentName	| `Wheat_CSv2.1_Genes-HC` |
| Reference	| Int. J. Mol. Sci. 2024, 25(16), 8614 |
| DOI	| https://doi.org/10.3390/ijms25168614 |

It is also possible to use :

| ... | ... |
| -- | -- |
| parentName	| `Wheat_IWGSC_RefSeq_v2.1` |

Which will not automatically load the HC Genes when the supplementary dataset is loaded.

The following examples utilise a spreadsheet called `Metadata.S2.xlsx` or `Metadata.Dataset_Name.xlsx` which contains just a Metadata worksheet.

## 'Suppl. Table S1'

`Suppl_Table_S1.py` expects the input spreadsheet to be named supplementary-tables.xlsx
```
ln -s  Vincent_supplementary-tables_2024-06-05.xlsx supplementary-tables.xlsx
python Suppl_Table_S1.py
```
The output spreadsheet is named `processed_output.xlsx`

## 'Suppl. Table S2'

The command-line parameters are 
1. input spreadsheet
2. output spreadsheet
3. metadata spreadsheet

```
python Suppl_Table_S2.py supplementary-tables.xlsx Suppl_Table_S2.Pretzel.xlsx Metadata.S2.xlsx
Processed data written to Suppl_Table_S2.Pretzel.xlsx
```



## Suppl. Table S3
'Suppl. Table S3' already has the required column headers, so no program is required to convert it.  Instead :
- copy worksheet 'Suppl. Table S3' to a new spreadsheet
- add a Metadata worksheet


### Wheat Tissue BED files

Extract the BED files (this also extracts the .xlsx file)
```
unzip ijms-25-08614-s001.zip
```

The command line parameters are
- output spreadsheet
- metadata spreadsheet
- input1.BED input2.BED ...


```
bedToPretzel.py
python $pretzelData/examples/ijms-25-08614/bedToPretzel.py wheatTissue_bed.xlsx Metadata.Dataset_Name.xlsx [0-9]*.BED
```
