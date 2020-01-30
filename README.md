# esri2sql
Convert ESRI Workspace XML to PostgreSQL

This script aims to convert ESRI xml schema into PostgreSQL to create an open environment for sharing data with explicit metadata

## Usage:
python esri2sql.py yourschema.xml

NB: This requires some other librarys which are all available in pip


## TODO:
Does not currently respect domains - these may be implemented in future as foreign key restrictions
