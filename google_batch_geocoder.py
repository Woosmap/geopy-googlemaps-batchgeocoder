#!/usr/bin/env python3
import csv
import time
from csv import Dialect

from geopy.exc import (
    GeocoderQueryError,
    GeocoderQuotaExceeded,
    ConfigurationError,
    GeocoderParseError,
    GeocoderTimedOut
)
from geopy.geocoders import GoogleV3

# used to set a google geocoding query by merging this value into one string with comma separated
ADDRESS_COLUMNS_NAME = ["name", "addressline1", "town"]
# used to define component restrictions for google geocoding
COMPONENT_RESTRICTIONS_COLUMNS_NAME = {}

# appended columns name to processed data csv
NEW_COLUMNS_NAME = ["Lat", "Long", "Error", "formatted_address", "location_type"]

# delimiter for input csv file
DELIMITER = ";"

# Automatically retry X times when GeocoderErrors occur (sometimes the API Service return intermittent failures).
RETRY_COUNTER_CONST = 5

# name for output csv file
INPUT_CSV_FILE = "hairdresser_sample_addresses.csv"

# name for output csv file
OUTPUT_CSV_FILE = "hairdresser_sample_addresses_processed.csv"

# google keys - see https://dev.to/gaelsimon/bulk-geocode-addresses-using-google-maps-and-geopy-5bmg for more details
GOOGLE_API_KEY = "AIzaSyAQanzCC6g4sR3tgj8tmFlByqhGFVKBFZI"  # it's the new mandatory parameter


# dialect to manage different format of CSV
class CustomDialect(Dialect):
    delimiter = DELIMITER
    quotechar = '"'
    doublequote = True
    skipinitialspace = True
    lineterminator = '\n'
    quoting = csv.QUOTE_ALL


csv.register_dialect('ga', CustomDialect)


def process_addresses_from_csv():
    geo_locator = GoogleV3(api_key=GOOGLE_API_KEY)

    with open(INPUT_CSV_FILE, 'r') as csvinput:
        with open(OUTPUT_CSV_FILE, 'w') as csvoutput:

            # new csv based on same dialect as input csv
            writer = csv.writer(csvoutput, dialect="ga")

            # create a proper header with stripped fieldnames for new CSV
            header = [h.strip('"').strip() for h in next(csvinput).split(DELIMITER)]
            # read Input CSV as Dict of Dict
            reader = csv.DictReader(csvinput, dialect="ga", fieldnames=header)

            # append new columns, to receive geocoded information, to the header of the new CSV
            header = list(reader.fieldnames)
            for column_name in NEW_COLUMNS_NAME:
                header.append(column_name)
            writer.writerow([s.strip() for s in header])

            # iterate through each row of input CSV
            for record in reader:
                # build a line address based on the merge of multiple field values to pass to Google Geocoder
                line_address = ','.join(
                    str(val) for val in (record[column_name] for column_name in ADDRESS_COLUMNS_NAME))

                # if you want to use componentRestrictions feature,
                # build a matching dict {'googleComponentRestrictionField' : 'yourCSVFieldValue'}
                # to pass to Google Geocoder
                component_restrictions = {}
                if COMPONENT_RESTRICTIONS_COLUMNS_NAME:
                    for key, value in COMPONENT_RESTRICTIONS_COLUMNS_NAME.items():
                        component_restrictions[key] = record[value]

                # geocode the built line_address and passing optional componentRestrictions
                location = geocode_address(geo_locator, line_address, component_restrictions)

                # build a new temp_row for each csv entry to append to process_data Array
                # first, append existing fieldnames value to this temp_row
                temp_row = [record[column_name] for column_name in reader.fieldnames]
                # then, append geocoded field value to this temp_row
                for column_name in NEW_COLUMNS_NAME:
                    try:
                        temp_row.append(location[column_name])
                    except BaseException as error:
                        print(error)
                        temp_row.append('')

                # Finally append your row with geocoded values with csvwriter.writerow(temp_row)
                try:
                    writer.writerow(temp_row)
                except BaseException as error:
                    print(error)
                    print(temp_row)


def geocode_address(geo_locator, line_address, component_restrictions=None, retry_counter=1):
    try:
        # the geopy GoogleV3 geocoding call
        location = geo_locator.geocode(line_address, components=component_restrictions)

        if location is not None:
            # build a dict to append to output CSV
            location_result = {"Lat": location.latitude, "Long": location.longitude, "Error": "",
                               "formatted_address": location.raw['formatted_address'],
                               "location_type": location.raw['geometry']['location_type']}
        else:
            location_result = {"Lat": 0, "Long": 0,
                               "Error": "None location found, please verify your address line",
                               "formatted_address": "",
                               "location_type": ""}

    # To catch generic geocoder errors.
    except (ValueError, GeocoderQuotaExceeded, ConfigurationError, GeocoderParseError) as error:
        if hasattr(error, 'message'):
            error_message = error.message
        else:
            error_message = error
        location_result = {"Lat": 0, "Long": 0, "Error": error_message, "formatted_address": "", "location_type": ""}

    # To retry because intermittent failures and timeout sometimes occurs
    except (GeocoderTimedOut, GeocoderQueryError) as geocodingerror:
        if retry_counter < RETRY_COUNTER_CONST:
            return geocode_address(geo_locator, line_address, component_restrictions, retry_counter + 1)
        else:
            if hasattr(geocodingerror, 'message'):
                error_message = geocodingerror.message
            else:
                error_message = geocodingerror
            location_result = {"Lat": 0, "Long": 0, "Error": error_message, "formatted_address": "",
                               "location_type": ""}
    # To retry because intermittent failures and timeout sometimes occurs
    except BaseException as error:
        if retry_counter < RETRY_COUNTER_CONST:
            time.sleep(5)
            return geocode_address(geo_locator, line_address, component_restrictions, retry_counter + 1)
        else:
            location_result = {"Lat": 0, "Long": 0, "Error": error, "formatted_address": "",
                               "location_type": ""}

    print("address line     : {0}".format(line_address))
    print("geocoded address : {0}".format(location_result["formatted_address"]))
    print("location type    : {0}".format(location_result["location_type"]))
    print("Lat/Long         : [{0},{1}]".format(location_result["Lat"], location_result["Long"]))
    print("-------------------")

    return location_result


if __name__ == '__main__':
    process_addresses_from_csv()
