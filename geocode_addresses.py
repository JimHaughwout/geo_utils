#! /usr/bin/env python
"""
Geocodes a CSV file of addresses using pygeocoder:
- Imports the CSV
- Attempts to geocode with `pygeocoder` 
- Combines original address and geocoded GADM features into single output file

pygeocoder is slower but more robust in terms of tolerance of partial 
addresses and level of formated information provided. 
This still makes use of Google's geocoding API V3.
 
Dependency: pip install pygeocoder
  
: param -h : Show usage help
: param -s : Name of CSV input file
 
To make a command line script:
- Move this file to /usr/local/bin
- Remove .py extention
- chmod +x filename
- Ensure "/usr/local/bin" is in your PATH
"""

from sys import argv, exit, exc_info
from pygeocoder import Geocoder
from time import sleep
from csv import DictReader, DictWriter
import getopt

# INPUT SETTINGS - Infile Attributes
# Set these to the requesite column names used in your input CSV
# ST_NUM_KEY, POSTAL_KEY and COUNTRY_KEY are optional
ST_NUM_KEY = None   
STREET_KEY = 'stp_address'
CITY_KEY = 'cty_name'
STATE_KEY = 'stp_state'
POSTAL_KEY = 'stp_zipcode'
COUNTRY_KEY = None  

 
def geocode_address(address="77 Massachusetts Avenue, Cambridge, MA"):
    """ 
    Geocode an address query
 
    :param string address: the address you which to encode
 
    Result is class GeocoderResult with following useful properties:
        lat, lng = result.coordinates
        latitude = result.latitude
        longitude = result.longitude
        street_number = result.street_number
        street = result.route
        city/locality = result.city
        county = result.county 
        neighborhood = result.neighborhood
        state = result.state
        province = result.province
        postal_code = result.postal_code
        country = result.country
        formatted_address = result.formatted_address
        valid_address is TRUE or FALSE
    
    :returns GeocoderResult result: Resulting pygeocoder object
    """
    assert isinstance(address, str), "geocode_address TypeError: Did not pass a str: %s" % addr

    try:
        result = Geocoder.geocode(address)
    except: #Catch all extraneous exceptions and exit
        e = exc_info()[1]
        print "Geocoder %s for %s" % (e, address)
        result = None
    
    return result


def process_address(addr):
    """
    Processes an address dictionary:
    - Extracts address for geocoding based on INPUT SETTINGS
    - Geocodes it 
    - Append the resulting geocoding features to the dict

    :param dict addr: address dictionary from CSV import
    :returns dict addr: original address dict appended with geocode features
    :returns boolean geocodeable: True=Geocodable address, False=Not
    """
    assert isinstance(addr, dict), "process_address TypeError: Did not pass a valid dict: %s" % addr
    
    result = geocode_address(extract_address(addr))

    if result == None: geocodeable = False
    else: geocodeable = result.valid_address

    addr['geocodable'] = geocodeable  
    addr['g_latitude'] = result.latitude if geocodeable else None
    addr['g_longitude'] = result.longitude if geocodeable else None
    addr['g_street_num'] = result.street_number if geocodeable else None
    addr['g_street'] = result.route if geocodeable else None
    addr['g_city'] = result.city if geocodeable else None
    addr['g_county'] = result.county if geocodeable else None
    addr['g_neighborhood'] = result.neighborhood if geocodeable else None
    addr['g_state'] = result.state if geocodeable else None
    addr['g_province'] = result.province if geocodeable else None
    addr['g_postal_code'] = result.postal_code if geocodeable else None
    addr['g_country'] = result.country if geocodeable else None
    addr['g_formatted_address'] = result.formatted_address if geocodeable else None

    return addr, geocodeable


def extract_address(csv_row):
    """
    Build addres string for geocoding from CSV dict keys
    Exits with error if required fields are not present.

    :param dict csv_row: Imported CSV row as a dict (via csv.DictReader)
    :returns dict address: Resulting extracted 1-line address for CSV row
    """
    assert isinstance(csv_row, dict), "extract_address TypeError: Did not pass a valid dict: %s" % csv_row

    try:
        address = ""
        if ST_NUM_KEY: address += "%s " % csv_row[ST_NUM_KEY]
        address += "%s, %s, %s" % (csv_row[STREET_KEY], csv_row[CITY_KEY], csv_row[STATE_KEY])
        if POSTAL_KEY: address += " %s" % csv_row[POSTAL_KEY]
        if COUNTRY_KEY: address += ", %s" % csv_row[COUNTRY_KEY]
    except:
        e = exc_info()[1]
        exit("build_address Error: %s\nCould not build address from %s" % (e, csv_row))
    
    return address 


def print_usage_and_exit(msg=None):
    """ 
    Pretty print exit on error

    :param str msg: Message to append to show user.
    """
    print "\nUsage: python %s [-s][-h]" % argv[0]
    print "\t-h Print usage help"
    print "\t-s Source CSV file - Required"
    if msg: print msg + "\n"
    exit(1)


def parse_opts(argv):
    """
    Parse opts, ensure we have required opts to determine mode, source, target.
    Checks if source file is a .csv. Generated outfile based on infile name.

    :param list argv: Arguments passed on Python invocation
    :returns str infile: CSV input filename
    :returns str outfile: Generated CSV output filename
    """
    infile = None

    try:
        opts, args = getopt.getopt(argv, "hs:")
        if not opts:
            print_usage_and_exit('No options supplied')
    except getopt.GetoptError as e:
        print_usage_and_exit('Could not parse options: %s' % e)

    for opt, arg in opts:
        if opt == '-h':
            print_usage_and_exit()   
        elif opt == '-s':
            infile = arg

    if not(infile):
        print_usage_and_exit('-s source_file not specified')
    elif infile[-4:] != '.csv':
        print_usage_and_exit('source_file is not a .csv file')
    else:
        outfile = infile[:-4] + '_geocoded.csv'

    return infile, outfile


def main(argv):
    """
    Main method. Reads in file based on INPUT SETTINGS
    Geocodes addresses and adds geocoder attributes to output
    Write alls to target csv and prints summary.
    """
    infile, outfile = parse_opts(argv)
    
    # Build a list of processed addresses
    processed_list = list()
    address_count = 0
    geocodeable_count = 0
    try:
        with open(infile) as csv_infile:
            reader = DictReader(csv_infile)
            print "Importing from %s" % infile
            for csv_row in reader:
                sleep(0.2) # So we do not exceed 10 / second API limit
                print '.',
                addr_result, geocodeable = process_address(csv_row)
                processed_list.append(addr_result)
                address_count += 1
                if geocodeable: geocodeable_count += 1
    except IOError as e:
        print_usage_and_exit(("\nCould not open %r to read: %s" % (infile, e)))

    # Write results to file (original plus new geocoder attriutes)
    try:
        with open(outfile, 'wb') as csv_outfile:
            target = DictWriter(csv_outfile, processed_list[0].keys())
            target.writeheader()
            target.writerows(processed_list)
    except IOError as e:
        print_usage_and_exit(("\nCould not open %r to write: %s" % (outfile, e)))

    geocode_rate = float(geocodeable_count) / float(address_count) * 100.0

    print "\nImported %d records. %d (%.2f %%) were geocodeable." % (address_count,
     geocodeable_count, geocode_rate)
    print "Wrote results to %s." % outfile


if __name__ == '__main__':
    main(argv[1:])