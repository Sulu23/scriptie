import re
import regex
import pandas as pd
import csv
import unicodedata
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


##### in main programma #####
global placeType_dict
placeType_dict = {"stad": ["PPL"], "dorp": ["PPL"], "gemeente": ["ADM2"], "provincie": ["ADM1"], "staat": ["ADM1"], "hoofdstad": ["PPLC", "PPLA"] , "eiland": ["ISL"]}
global continents
continents = {
     "Europa": 6255148, "Afrika": 6255146,
     "Azië":6255147, "Oceanië": 6255151,
     "Noord-Amerika": 6255149, "Zuid-Amerika": 6255149,
     "Antarctica": 6255152
    }
 ##################


def makeDict(articles_dataset):
    '''this function does something '''
    articles_dict = {}

    with open(articles_dataset, mode='r') as f:
        file = csv.reader(f)
        next(file) # skip first row
        for id, datetime, title, content, category, url in file:
            article = {}
            article["datetime"] = datetime
            article["title"] = title
            article["content"] = content
            article["category"] = category
            article["url"] = url
            articles_dict[int(id)] = article

    return articles_dict


def fun5(word0, title, positions):
    ''' does something'''
    # normalize text....
    word = unicodedata.normalize('NFC', word0)


    if word in continents:
        return word, [], 0, continents[word]

#    try:
 #       print("CONTINENT", word, continents[word])
#    except:
 #       print("x ", end=" ")

    matches = re.search(re.escape(word), title[positions:], re.UNICODE)

    if matches:
        position = matches.end() + positions

        match = matches.group()
        fcode = []
        pre = r"\b(:?([Gg]emeente|[Pp]rovincie|[Ss]tad|[Hh]oofdstad|[Ee]iland|[Dd]orp|[Ss]taat))(?:je)?\b "
        x = re.search(pre + re.escape(match), title[positions:])

        if x:
            type = x.group(1)
            fcode = placeType_dict[type]


        return match, fcode, position, 0

    else:
        check = 0
        for wrd in re.split(r'[,;.:\s"]\s*', title[positions:]):
            wrd = wrd.strip()
            if len(wrd) == len(word):

                rat = fuzz.ratio(word, wrd)    # choose between fuzz, wfuzz
                if rat >= 80:
                    check = 1
                    a, code, pos, id = fun5(wrd, title, positions)
                    return a, code, pos, 0
                    break

    # check whether words were skipped
    if  check == 0:
        print('\n', word, "not detected")
        print(title)


def fun4(annodata2, id):
    ''' does something'''
    isTitle = annodata2["isTitle"].values[0]    # check if title
    list_toponyms = annodata2["toponym"].to_list()    # make list of toponyms

    processedData = annodata2.copy()
    processedData["predID"] = 0
    processedData["fcodes"] = [[] for r in range(len(processedData))]
    processedData["lookUp"] = ''

    if isTitle:    # look at title
        title0 = global_dict[id]["title"]    # dictionary values of this article
        title = unicodedata.normalize('NFC', title0)

        positions = 0

        for index, row in processedData.iterrows():
           lookUp, fcode, positions, predID  = fun5(row.toponym, title, positions)
           processedData.at[index, "lookUp"] = lookUp
           processedData.at[index, "fcodes"] = fcode
           processedData.at[index, "predID"] = predID


    else:    # look at content
        content0 = global_dict[id]["content"]    # dictionary values of this article
        content = unicodedata.normalize('NFC', content0)

        positions = 0
        for index, row in processedData.iterrows():
           lookUp, fcode, positions, predID = fun5(row.toponym, content, positions)
           processedData.at[index, "lookUp"] = lookUp
           processedData.at[index, "fcodes"] = fcode
           processedData.at[index, "predID"] = predID

#    print(processedData)
    return processedData

def fun3(annodata):
    '''this function does something '''

    artID = annodata["articleID"].values[0]    # article ID of this batch
    print(artID, global_dict[artID]["category"], ':')

    # groupby istitle
    data2 = annodata.groupby(by="isTitle", sort=False).apply(fun4, id=artID)
 #   data2.reset_index()
    print('\n')

    return(data2)

def process_annotation(annot, dataset):
    '''this function does something '''

    global global_dict
    global_dict = makeDict(dataset)

    with open(annot, newline='', encoding="utf-8") as f:
        columnNames = ["articleID", "toponym", "geoID", "isTitle"]
        df = pd.read_csv(f, sep='\t', names=columnNames)

    id = "articleID"

    dfnew = df.groupby(by=id, sort=False).apply(fun3)    # processes batches per article ID

    dfnew = dfnew.reset_index(drop=True)

    return dfnew   # with open("newfile.txt", 'r') as f:
    #    print(f.read())




