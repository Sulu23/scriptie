import argparse
import re
import regex
import pandas as pd
import csv
import unicodedata
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import spacy

nlp = spacy.load("nl_core_news_lg")
from PyDictionary import PyDictionary

dictionary = PyDictionary()
from googletrans import Translator

translator = Translator()
from getCountryData import country_codes
from getCountryData import admin1_codes
from getCountryData import admin2_codes
import pickle


global placeType_dict
placeType_dict = {
    "stad": ["P", "PPL"],
    "dorp": ["P", "PPL"],
    "gemeente": ["A", "ADM2"],
    "provincie": ["A", "ADM1"],
    "staat": ["A", "ADM1"],
    "hoofdstad": ["P", "PPLC", "PPLA"],
    "eiland": ["T", "ISL"],
}

global continents
continents = {
    "Europa": 6255148,
    "Afrika": 6255146,
    "Azië": 6255147,
    "Oceanië": 6255151,
    "Noord-Amerika": 6255149,
    "Zuid-Amerika": 6255150,
    "Antarctica": 6255152,
}

global adj2noun
adj2noun = dict()


def makeDict(articles_dataset):
    """ makes a dictionary of the given article dataset  with article ID as key """

    articles_dict = {}

    with open(articles_dataset, mode="r") as f:
        file = csv.reader(f)
        next(file)  # skip first row
        for id, datetime, title, content, category, url in file:
            article = {}
            article["datetime"] = datetime
            article["title"] = title
            article["content"] = content
            article["category"] = category
            article["url"] = url
            articles_dict[int(id)] = article

    return articles_dict


def adjectives(text, toponym, type=False):
    """returns adjective that is associated with the given toponym"""
    doc = nlp(text)

    for token in doc:
        if token.text == toponym:
            if type:
                for ancestor in token.ancestors:
                    if ancestor.text == type:
                        # if ancestor.dep_ == 'attr' or ancestor.dep_ == 'nsubj':
                        for child in ancestor.children:
                            if (
                                child.dep_ in {"amod", "acomp"}
                                and child.pos_ == "ADJ"
                                and child.text[0].isupper()
                            ):
                                return child.text
            else:

                for child in token.children:
                    if (
                        child.dep_ in {"amod", "acomp"}
                        and child.pos_ == "ADJ"
                        and child.text[0].isupper()
                    ):
                        return child.text

    return ""


def getCountryCode(toponym):
    """
    returns countryCode and admin1Code
    if given toponym is found in
    country_codes, admin1_codes or admin2_codes
    """

    # toponym is a country name
    if toponym in country_codes:
        return country_codes[toponym], ""

    # toponym is an administrative division of the first order
    elif toponym in admin1_codes:
        admin1_fullCode = admin1_codes[toponym][0]
        countryCode, admin1_code = admin1_fullCode.split(".")
        return countryCode, admin1_code

    # toponym is an administrative division of the second order
    elif toponym in admin2_codes:
        admin2_fullCode = admin2_codes[toponym][0]
        countryCode, admin1_code, admin2_code = admin2_fullCode.split(".")
        return countryCode, admin1_code

    return "", ""


def adj2toponym(adj):
    """returns the toponym that the given adjective refers to"""

    # save results in a dictionary
    if adj in adj2noun:
        return adj2noun[adj]

    trans = translator.translate(adj, src="nl", dest="en")
    adj_en = trans.text
    try:
        meaning = dictionary.meaning(adj_en)["Adjective"][0]
        print(meaning)
        pattern = r"((?:[A-Z][\w]+)(?: [A-Z][\w]+)*)"
        match = re.search(pattern, meaning)
        if match:
            toponym = match.group(1)
            print(f"noun: {toponym}")

            # add adj-noun pair to dictionary
            adj2toponym[adj] = toponym
            return toponym

    except Exception:
        return adj_en


def fun5(toponym, text, positions):
    """
    find the toponym in the title,
    return information based on its context in the given text
    """

    toponym = unicodedata.normalize("NFC", toponym)

    if toponym in continents:
        return toponym, [], 0, continents[toponym], "", ""

    admin1Code = ""
    countryCode = ""

    # look for toponym in the text
    x = re.search(r"\b" + re.escape(toponym) + r"\b", text[positions:], re.UNICODE)

    if x:
        position = x.end() + positions

        match = x.group()
        print(match)
        match_start = x.start() + positions
        match_end = x.end() + positions

        fcode = []
        pre = (
            r"\b(:?([Gg]emeente|[Pp]rovincie|[Ss]tad|[Hh]oofdstad|[Ee]iland|[Dd]orp|[Ss]taat))(?:je)?\s"
            + re.escape(match)
        )
        text_type = text[max(0, match_start - 12) : match_end]
        type_match = re.search(pre, text_type)
        if type_match:
            type = type_match.group(1)
            fcode = placeType_dict.get(type, [])
            text_adj = text[max(0, match_start - 32) : match_end]
            adj = adjectives(text_adj, match, type)
            if adj:
                print(adj, type, match)
                adj_toponym = adj2toponym(adj)
                countryCode, admin1Code = getCountryCode(adj_toponym)

            return match, fcode, match_end, 0, countryCode, admin1Code

        text_adj = text[max(0, match_start - 20) : match_end]
        adj = adjectives(text_adj, match)
        if adj:
            print(adj, match)
            adj_toponym = adj2toponym(adj)
            countryCode, admin1Code = getCountryCode(adj_toponym)

        return match, [], match_end, 0, countryCode, admin1Code

    x2 = re.search(re.escape(toponym), text[positions:], re.UNICODE)

    if x2:
        position = x2.end() + positions
        match = x2.group()
        match_start = x2.start() + positions
        match_end = x2.end() + positions

        fcode = []
        # Regular expression to find the type of place
        pre = (
            r"\b(:?([Gg]emeente|[Pp]rovincie|[Ss]tad|[Hh]oofdstad|[Ee]iland|[Dd]orp|[Ss]taat))(?:je)?\s"
            + re.escape(match)
        )
        text_type = text[max(0, match_start - 12) : match_end]
        type_match = re.search(pre, text_type)
        if type_match:
            type = type_match.group(1)
            fcode = placeType_dict.get(type, [])
            text_adj = text[max(0, match_start - 32) : match_end]
            adj = adjectives(text_adj, match, type)
            if adj:
                print(adj, type, match)
                adj_toponym = adj2toponym(adj)
                countryCode, admin1Code = getCountryCode(adj_toponym)
            return match, fcode, match_end, 0, countryCode, admin1Code

        text_adj = text[max(0, match_start - 20) : match_end]
        adj = adjectives(text_adj, match)
        if adj:
            print(adj, match)
            adj_toponym = adj2toponym(adj)
            countryCode, admin1Code = getCountryCode(adj_toponym)
        return match, [], match_end, 0, countryCode, admin1Code

    # If no exact match is found, use fuzzy matching
    else:
        check = 0
        for wrd in re.split(r'[,;.:\s"]\s*', text[positions:]):
            wrd = wrd.strip()
            if len(wrd) == len(toponym):

                rat = fuzz.ratio(toponym, wrd)
                if rat >= 80:
                    check = 1
                    a, code, pos, id, countryCode, admin1Code = fun5(
                        wrd, text, positions
                    )
                    return a, code, pos, id, countryCode, admin1Code
                    break

    return toponym, [], positions, 0, "", ""

    # check whether toponyms were skipped
    if check == 0:
        print("\n", toponym, "not detected")
        print(text)


def fun4(annodata2, id):
    """returns a copy of the given dataframe,
    but with extra information extracted from arcticle context"""
    isTitle = annodata2["isTitle"].values[0]

    processedData2 = annodata2.copy()
    processedData2["predID"] = 0
    processedData2["fcodes"] = [[] for r in range(len(processedData2))]
    processedData2["lookUp"] = ""
    processedData2["countryCode"] = ""
    processedData2["admin1Code"] = ""
    processedData = processedData2.copy()

    if isTitle:
        title0 = global_dict[id]["title"]
        title = unicodedata.normalize("NFC", title0)

        positions = 0

        for index, row in processedData.iterrows():
            lookUp, fcode, positions, predID, countryCode, admin1Code = fun5(
                row.toponym, title, positions
            )
            processedData.at[index, "lookUp"] = lookUp
            processedData.at[index, "fcodes"] = fcode
            processedData.at[index, "predID"] = predID
            processedData.at[index, "countryCode"] = countryCode
            processedData.at[index, "admin1Code"] = admin1Code

    else:
        content0 = global_dict[id]["content"]
        content = unicodedata.normalize("NFC", content0)

        positions = 0
        for index, row in processedData2.iterrows():
            lookUp, fcode, positions, predID, countryCode, admin1Code = fun5(
                row.toponym, content, positions
            )
            processedData.at[index, "lookUp"] = lookUp
            processedData.at[index, "fcodes"] = fcode
            processedData.at[index, "predID"] = predID
            processedData.at[index, "countryCode"] = countryCode
            processedData.at[index, "admin1Code"] = admin1Code

    return processedData


def fun3(annodata):
    """processes the data by title and content seperately"""

    artID = annodata["articleID"].values[0]  # article ID of this batch
    data2 = annodata.groupby(by="isTitle", sort=False).apply(fun4, id=artID)

    return data2


def process_annotation(annot, dataset):
    """processes the given annotation and pickles the result"""

    global global_dict
    global_dict = makeDict(dataset)

    with open(annot, newline="", encoding="utf-8") as f:
        columnNames = ["articleID", "toponym", "geoID", "isTitle"]
        df = pd.read_csv(f, sep="\t", names=columnNames)

    id = "articleID"

    # processes batches per article ID
    dfnew = df.groupby(by=id, sort=False).apply(fun3)

    dfnew = dfnew.reset_index(drop=True)

    dfnew.to_pickle("./pickledDf.pkl")


def main():
    # commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--annotations",
        type=str,
        help="a dataset in tsv format",
        default="annotations_test.tsv",
    )

    args = parser.parse_args()

    process_annotation(args.annotations, "dataset.csv")


if __name__ == "__main__":
    main()
