import re
import regex
import pandas as pd
import csv
import unicodedata
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


#TODO
# check surrounding words? with bash or regex
# make all occurences the same per article? 
# str.partition
# gemeente greedy maken?
# compile regex patterns. p = re.compile(pattern), p.match(str)
# gemeente, provicie (provincies x en y), stad, hoofdstad, gebied, (staat), dorpje, deelstaat, (Drentse Havelte?), bolwerk, Republiek Congo, havenstad, buurland, Oliestaat, Hof, Overijsserlse Bornerbroek, woonplaats, kustplaats, plaatsje, Citadel Aleppo, Volksrepublieken Donetsk en Loehansk, regio, stadskantoor utrecht wijk, eiland, graafschap Somerset, ereveld, kolonie Nederlands-Indie, naburige Simpelveld, 
# station, luchthaven, (perron?), geboorteplaats, Ierse, kustplaats, Golfstaatje, grensplaats, paleis, 
# artikel meta data (binnenland nieuws), rotterdamse, schiereiland, dorp, bergketen, koningsstad, 
# r'dam, check r'dam similarity met alle andere annotaties. geef ID van beste similarity
# stad x, in yland. x (yland). xland naast, bij yland. Buurland, kasteel, thuisstad, bruinkooldorp, stadje, belgische, texaanse, kanaal tynaarlo, parlement, eilandje, land guinee, 


def test():
    # str.partition
    title = "De gemeente weet t even niet"
    b, k, a = title.partition("gemeente")
    print('b:', b, 'k:', k, 'a:', a)
    # loop through toponyms
#    annodata = annodata.reset_index()    # idk if necessary
 #   for index, row in annodata.iterrows():
  #      fun4(artID, row["toponym"], row["isTitle"])
#        print(row["toponym"], row["isTitle"])
# test (?: ) vs (?> ...)


def fun1(dataset):
    '''this function does something '''
    global global_dict
    global_dict = {}

    with open(dataset, mode='r') as f:
        file = csv.reader(f)
        next(file) # skip first row
        for id, datetime, title, content, category, url in file:
            w = {}
            w["datetime"] = datetime
            w["title"] = title
            w["content"] = content
            w["url"] = url
            global_dict[int(id)] = w


def fun5(word0, title, positions):
    ''' does something'''
    # normalize text....
    word = unicodedata.normalize('NFC', word0)

    matches = re.search(re.escape(word), title[positions:], re.UNICODE)

    if matches:
        position = matches.end() + positions
   #     print(word, matches.start()+positions, position)

############## check surrounding words ############
        match = matches.group()
#        x = re.search("(?>\w+ )?"+ re.escape(match) +  "(?> \w+)?", title[positions:])
        pre = r"\b(?:[Gg]emeente|[Pp]rovincie|[Ss]tad|[Hh]oofdstad|[Ee]iland|[Dd]orp|[Ss]taat)(?:je)?\b "
#        pre = "[Gg]emeente "
        x = re.search(pre + re.escape(match) +  "(?> \w+)?", title[positions:])

  #      try:
        if x:
            b = x.group()
            print(b)
#        except:
 #           print("not found:", word, match)

        return position


###################################

    else:
        check = 0
        for wrd in re.split(r'[,;.:\s"]\s*', title[positions:]):
            wrd = wrd.strip()
            if len(wrd) == len(word):

#            rat = fuzz.WRatio(word, wrd)    # choose between fuzz, wfuzz
                rat = fuzz.ratio(word, wrd)    # choose between fuzz, wfuzz
                if rat >= 80:
                    check = 1
                    fun5(wrd, title, positions)
                    break

    # check whether words were skipped
    if  check == 0:
        print('\n', word, "not detected")
        print(title)

    return positions


def fun4(annodata2, id):
    ''' does something'''
    isTitle = annodata2["isTitle"].values[0]    # check if title

    list_toponyms = annodata2["toponym"].to_list()    # make list of toponyms

#    print('\n', list_toponyms)


    if isTitle:    # look at title
        title0 = global_dict[id]["title"]    # dictionary values of this article
        title = unicodedata.normalize('NFC', title0)
 #       print(title)

    #   try some regex
#        x = re.findall("[gG]emeente", title)
        x = re.findall("[gG]emeente (\w+)", title)


        for line in x:
            pass
#            print(title)
 #           print(line)




#################################
        positions = 0
        for word in list_toponyms:
            positions = fun5(word, title, positions)
  #          print('\n')

    else:    # look at content
        content0 = global_dict[id]["content"]    # dictionary values of this article
#        print(list_toponyms, '\n')
        content = unicodedata.normalize('NFC', content0)

#        print(content)

##### trying to get surrounding words
#        x = re.findall("[gG]emeente", content)

#        x = re.findall("[gG]emeente \w+ \w+", content)
#        x = re.findall("[gG]emeente [A-Z]\w+", content)
        x = re.findall("[gG]emeente(?> [A-Z]\w+)+", content)

        for line in x:
            pass
#            print(line)


##########
        positions = 0
        for word in list_toponyms:
            positions = fun5(word, content, positions)
 #       for line in x:
  #          print(line)



def fun3(annodata):
    '''this function does something '''
#    print(annodata.head())

    artID = annodata["articleID"].values[0]    # article ID of this batch
#    print(artID)

    # groupby istitle
    data2 = annodata.groupby(by="isTitle", sort=False).apply(fun4, id=artID)





def fun2(annot):
    '''this function does something '''

    with open(annot, newline='', encoding="utf-8") as f:
        columnNames = ["articleID", "toponym", "geoID", "isTitle"]
        df = pd.read_csv(f, sep='\t', names=columnNames)

    id = "articleID"
    df = df.groupby(by=id, sort=False).apply(fun3)    # processes batches per article ID






def main():
    fun1("dataset.csv") # makes a dict of dataset

    fun2("all_annotations.tsv")


if __name__ == "__main__":
    main()






def test():
        list = ["groningen", "groningen", "utrecht", "lelystad", "utrecht"]
        text = "groningen heeft groningen in de fik gestoken, utrecht en lelystad, utrecht."

        print(list)
        positions = 0

        for word in list:
#            print(text[0:])
            matches = re.search(r'\b' + word + r'\b', text[positions:])
            positions = matches.end()
            print(word, positions)

