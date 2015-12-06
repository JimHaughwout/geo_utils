# geo_utils
GIS utilities

## path_utils.py
> TODO: Docs

## geocode_addresses.py
Geocodes a CSV file of addresses using pygeocoder:
- Imports the CSV
- Attempts to geocode with `pygeocoder` 
- Combines original address and geocoded GADM features into single output file

The CSV input file requires, at a minimum:
- Street Address
- City
- State/Province.

`pygeocoder` is slower but more robust in terms of tolerance of partial 
addresses and level of formated information provided. 
This still makes use of Google's geocoding API V3.
 
#### Dependencies
You will to install `pygeocoder==1.2.4` or later via `pip` or `conda`.

You also will need a Google API key if geocoding more than 10,000 addresses. 

#### Usage
Update the `INPUT SETTINGS` to reflect the column names used in input file.

Run from command line:
```sh
Usage: python geocode_addresses.py [-s][-h]
    -h Print usage help
    -s Source CSV file - Required
```

#### Note
All functions are included in single script file. As such you can make this
a command line script by doing the following"
- Move this file to `/usr/local/bin`
- Remove `.py` extention
- `chmod +x [filename]`
- Ensure `/usr/local/bin` is in your environment `PATH`