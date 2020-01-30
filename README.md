# Batch geocode your csv address file using GeoPy and GoogleMaps Geocoding service

**input** : csv file with addresses you need to geocode

**output** : same csv with appended following fields
 
- Latitude
- Longitude
- Location_Type
- Formatted_Address 
- Error (if needded, for failed geocoded addresses)

sample usage:

    python google_batch_geocoder.py


## Mandatory parameters
  
- ADDRESS_COLUMNS_NAME = ["name", "addressline1", "town"]
*used to set a google geocoding query by merging this value into one string with comma separated. it depends on your CSV Input File*

- NEW_COLUMNS_NAME = ["Lat", "Long", "Error", "formatted_address", "location_type"]
*appended columns name to processed data csv*

- DELIMITER = ";"
*delimiter for input csv file*

- INPUT_CSV_FILE = "./hairdresser_sample_addresses_sample.csv"
*path and name for output csv file*

- OUTPUT_CSV_FILE = "./processed.csv"
*path and name for output csv file*

## Optional parameters

- COMPONENTS_RESTRICTIONS_COLUMNS_NAME = {"country": "IsoCode"}
*used to define component restrictions for google geocoding*
*see [Google componentRestrictions doc](https://developers.google.com/maps/documentation/javascript/reference?hl=FR#GeocoderComponentRestrictions) for details* 

## useful links

- [geopy](https://github.com/geopy/geopy) : Geocoding library for Python.
- [Google Maps Geocoding API](https://developers.google.com/maps/documentation/geocoding/start)
- [Google Maps Geocoding API Usage Limits](https://developers.google.com/maps/documentation/geocoding/usage-limits)
- Display your POIs on a Map with [Woosmap](https://www.woosmap.com/)