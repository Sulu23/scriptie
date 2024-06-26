import argparse
import json
import requests
import csv
import pandas as pd
from functools import lru_cache
import coreference as g
import pickle

# geonames username
global_username = "scriptie_vdwal"


@lru_cache(maxsize=None)
def findID_baseline(placeName):
    """returns GeoNames ID for the baseline program"""

    URL = (
        "http://api.geonames.org/searchJSON?q="
        + placeName
        + "&maxRows=1"
#        + "&fuzzy=0.8"
        + "&username="
        + global_username
    )

    response = requests.get(URL)
    data = response.json()

    if len(data) == 0:  # no data is returned
        return 0

    if data["geonames"]:
        geodata = data["geonames"]
        if len(geodata) == 0:  # no results are found
            return 0

        result = geodata[0]
        id = result["geonameId"]

        return id

    return 0


@lru_cache(maxsize=None)
def findID_backup(placeName, fuzz=1):
    """finds ID using fuzzy search"""

    URL = (
        "http://api.geonames.org/searchJSON?q="
        + placeName
        + "&maxRows=1"
        + "&fuzzy="
        + str(fuzz)
        + "&username="
        + global_username
    )
    response = requests.get(URL)
    data = response.json()

    if len(data) == 0:  # no data is returned
        return 0

    geodata = data["geonames"]
    if len(geodata) == 0:  # no results are found
        return 0

    result = geodata[0]
    id = result["geonameId"]

    return id


def findID(placeName, fcodes, string, adminCode=""):
    """returns geoID based on toponym, feature codes, country codes and admin1 codes"""
    numberofresults = 1
    if adminCode:
        numberofresults = 2

    URL = (
        "http://api.geonames.org/searchJSON?q="
        + placeName
        + string
        + "&maxRows="
        + str(numberofresults)
        + "&fuzzy=0.7"
        + "&type=long"
        + "&username="
        + global_username
    )

    response = requests.get(URL)

    data = response.json()
    print(URL)

    if len(data) == 0:
        print("FAIL")
        return 0

    try:
        geodata = data["geonames"]

        # check admin1 code
        if adminCode:
            print(geodata)
            for i in range(len(geodata)):
                print(adminCode, geodata[i]["adminCode1"])
                if geodata[i]["adminCode1"] == adminCode:
                    id = geodata[i]["geonameId"]
                    return id

        # check fcode
        if fcodes:
            if fcodes[0] != "ISL":
                i = 0
                for j in range(len(geodata)):
                    if geodata[j]["fcode"] == fcodes[i]:
                        id = geodata[j]["geonameId"]
                        return id

        id = geodata[0]["geonameId"]
        return id

    except:
        ID = findID_backup(placeName, 0.8)
        return ID


def newfun(dataframe):
    """adds country bias and feature class to URL"""
    df_copy = dataframe.copy()

    for index, row in dataframe[dataframe["predID"] == 0].iterrows():
        parameter_str = ""

        if row.fcodes != []:
            str_fcodes = "&featureClass=" + row.fcodes[0]
            parameter_str += str_fcodes

        if row.countryCode:
            str_country = "&countryBias=" + row.countryCode
            parameter_str += str_country

        if parameter_str:
            ID = findID(row.lookUp, row.fcodes[1:], parameter_str, row.admin1Code)

        else:
            ID = findID_backup(row.lookUp, 0.8)

        df_copy.at[index, "predID"] = ID

    return df_copy


def readTSV(dataset, baseline):
    """
    processes the given tsv file
    returns a dataset with added GeoName IDs
    """

    if baseline:  # perform the baseline program
        with open(dataset, newline="") as f:
            columnNames = ["articleID", "toponym", "geoID", "isTitle"]
            df = pd.read_csv(f, sep="\t", names=columnNames)
        print("performing the baseline program on\n", df, "...")
        newdf = df.copy()
        newdf["predID"] = df["toponym"].apply(findID_baseline)

    else:  # perform the normal program
        with open("./pickledDf.pkl", "rb") as f:
            df = pickle.load(f)
        print("performing the normal program on\n", df)
        newdf = df.copy()
        newdf = df.groupby("articleID").apply(newfun)

    return newdf


def writeTSV(dataframe):
    """writes pandas dataframe to output.tsv"""
    dataframe.to_csv("output.tsv", sep="\t", index=False)


def agreement(df):
    """calculates agreement between expected and predicted GeoNames IDs"""

    total = len(df)  # total number of annotations
    totalCorrect = 0  # total number of correctly guessed geoIDs
    notGuessed = 0  # total number of geoIDs that were not guessed
    for row in df.itertuples():
        expID = row.geoID
        predID = row.predID

        if expID == predID:
            totalCorrect += 1

        elif predID == 0:
            notGuessed += 1

    totalGuessed = total - notGuessed  # total number of guessed geoIDs

    precision = totalCorrect / totalGuessed
    recall = totalCorrect / total
    f1 = (2 * precision * recall) / (precision + recall)

    print(
        "\nAgreement between the guessed geoIDs and expected geoIDs:\n"
        "\nTotal number of annotations: {}".format(total),
        "\nTotal guessed: {}".format(totalGuessed),
        "\nPrecision: {}".format(precision),
        "\nRecall: {}".format(recall),
        "\nF1-score: {}".format(f1),
    )


def main():

    # commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset", type=str, help="a dataset in tsv format", default="annotations_test.tsv"
    )
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="perform the baseline program",
        default=False,
    )
    parser.add_argument(
        "--username", type=str, help="geonames username", default="scriptie_vdwal"
    )
    args = parser.parse_args()

    # set variables
    dataset = args.dataset
    global global_username
    global_username = args.username

    # process the data
    processed_dataset = readTSV(dataset, args.baseline)
    writeTSV(processed_dataset)
    agreement(processed_dataset)

    # clear cache when program is done running
    #    findID.cache_clear()
    findID_baseline.cache_clear()


if __name__ == "__main__":
    main()
