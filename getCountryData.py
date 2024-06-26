import requests

# get country codes from geonames
URL_countryInfo = "http://download.geonames.org/export/dump/countryInfo.txt"

response_countryInfo = requests.get(URL_countryInfo)
data_countryInfo = response_countryInfo.text

country_codes = dict()
for line in data_countryInfo.splitlines():
    if line.startswith("#") or not line.strip():  # ???
        continue
    fields = line.split("\t")
    country_name = fields[4]
    country_code = fields[0]
    country_codes[country_name] = country_code


# get codes for first-level administrative divisions from geonames
URL_admin1 = "http://download.geonames.org/export/dump/admin1CodesASCII.txt"

response_admin1 = requests.get(URL_admin1)
data_admin1 = response_admin1.text

admin1_codes = dict()
for line in data_admin1.splitlines():
    fields = line.split("\t")
    admin1_name = fields[1]
    admin1_code = fields[0]
    admin1_geoID = fields[3]
    admin1_codes[admin1_name] = (admin1_code, admin1_geoID)


# get codes for second-level administrative divisions from geonames
URL_admin2 = "http://download.geonames.org/export/dump/admin2Codes.txt"

response_admin2 = requests.get(URL_admin2)
data_admin2 = response_admin2.text

admin2_codes = dict()
for line in data_admin2.splitlines():
    fields = line.split("\t")
    admin2_name = fields[1]
    admin2_code = fields[0]
    admin2_geoID = fields[3]
    admin2_codes[admin2_name] = (admin2_code, admin2_geoID)
