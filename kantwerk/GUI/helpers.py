##############################################################################################################
##############################################################################################################
###
###     Für die Nutzung relevante Funktionen
###
##############################################################################################################
##############################################################################################################


##############################################################################################################
##
##      Import externer Bibliotheken
##
##############################################################################################################
from bs4 import BeautifulSoup as bs
import re


##############################################################################################################
##
##      Funktionen
##
##############################################################################################################
'''
    Inhalt:
    1. Daten laden
    2. Datenvorbereitung
    3. Modell/Vektoren
    4. Suche
'''

'''
    1. Daten laden
'''
def ladeTEI (num: int, pfad:str = "../kantwerk/GUI/static/GUI/data/Korpustexte/"):
    """
        Gibt Datei als Beautiful Soup Element zurück
        Input: 
            num:        Integer,    Nummer des zu öffnenden Bandes
            pfad        String,     (optional) Pfad zu Daten
        Output:
            bs4.element,    Dateiinhalt
                ! Gibt es keinen Treffer, wird nur eine Fehlermeldung auf der Konsole ausgegeben
    """
    # Pfad setzen
    pfad = pfad + str(num) + "_out.xml"

    # Versuche Datei zu öffnen
    try:
        f = open(pfad)
        tei = f.read()
        data = bs(tei, 'xml')
        f.close()
    # ... ansonsten: gebe Fehlermeldung aus
    except IOError:
        print(pfad)
        print("Die Datei konnte nicht geladen werden.")
        return
    
    return data


'''
    2. Datenvorbereitung
'''
def satzextraktion (data:bs, low:bool = False):
    """
        Gibt alle Elemente mit relevanter ID und ihre IDs zurück
        Input: 
            data:   bs4,        Beautiful Soup Element der zu bearbeitenden Datei 
                                ! zu bearbeitende Textstellen sollten bereits mit id-tag ausgezeichnet sein
            low:    Boolean,    Angabe, ob Kleinschribung verwendet werden soll
        Output:
            list,   Liste mit den IDs
                 ...konkruent...
            list,   Liste mit den Absätzen
                ! Gibt es keinen Treffer, wird nur eine Fehlermeldung auf der Konsole ausgegeben
    """
    # Initialisierungen
    ids = []
    absätze = []

    # Lese alle Tags mit id aus
    for inh in data.find_all(id=True):
        
        # Alle Tags sollten eine Überschrift oder Absatz sein
        h = ["h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8", "h9"]
        if inh.name in h or inh.name == "p":
            text = str(inh)
            text = re.sub("\s+", " ", text)
            # Sonderbearbeitung der Überschriften
            if inh.name != "p":
                text = re.sub('<[^!].*?/?>', "", text)
            # Sonderbearbeitung der Absätze
            else:
                text = re.sub("<(.*?)>", "", text)
            text = re.sub("\s+", " ", text)
            text = text.strip()
            # Nichtleere Strings werden aufgenommen (leere Strings sollten eigentlich nicht vorkommen)
            if not text == " " and not text == "":
                if low:
                    absätze.append(text.lower())
                else:
                    absätze.append(text)
                ids.append(inh["id"])
        # ... ansonsten: Probleme aufzeigen
        else:
            print("Es gab ein Problem mit den Inhalten eines Tags mit id. Sie hat nicht das geforderte Format (h1-9 oder p):")
            print(inh.name)
        
    return ids, absätze


def bereite_daten ( tei:list, modell:str = None, low:bool = None, bandanzahl:int = 10 ):
    """
        Bereite Daten aller Bände vor. Es wird eine ID-Liste und eine Dokumentenliste jeweils für die normalisierten und originalen Dateien aller Bände erstellt sowie ein Mapping, das die Gesamtanzahl der Ids jedes Bandes enthält.
        Input: 
            tei:        Liste,      Liste mit Tei-Dateien
            modell:     String,     Modellkürzel
            bandanzahl: Integer,    Anzahl der zu durchsuchenden Bände
        Output:
            list,   ID-Liste der originalen Datei
            list,   Absatzliste der originalen Datei
    """
    # Initialisierung und gegebenenfalls low setzen
    alleidsorig = []
    alledokumenteorig = []
    if low == None and modell != None:
        if "bi-electra" in modell:
            low = True
        else:
            low = False
    elif low == None:
        low = False

    # Daten lesen und vorbereiten
    print("Lese Datei")
    for i in range(1,bandanzahl):
        # Einlesen und laden der Suchabsätze
        ids, docs = satzextraktion(tei[i-1], low)

        # geschachtelte Liste erstellen für Ausgabe
        alleidsorig.append(ids)
        alledokumenteorig.append(docs)

    return alleidsorig, alledokumenteorig


'''
    4. Suche
'''
def suche_absatz (alleidsnorm:list, alleidsorig:list, alledokumenteorig:list, idanzahl:list, absatznummer:int, getid:bool = False):
    """
        Gibt den Absatz entsprechend der Id zurück, basierend auf mapping wird zum nächsten Text gesprungen
        Input: 
            alleidsnorm:        Liste,      Liste der Ids, basierend auf den normalisierten Absätzen
            alleidsorig:        Liste,      Liste der Ids, basierend auf den originalen Absätzen
            alledokumenteorig:  Liste,      Liste der Absätze, basierend auf den originalen Absätzen
            idanzahl:           Liste,      Gesamtanzahl an Ids je Band (basierend auf der normalisierten Datei)
            absatznummer:       Integer,    Indize des Absatzes in fortlaufender Form (ohne Bandzusatz)
            getid:              Boolean,    Angabe ob ausschließlich id zurückgegeben werden soll
        Output:
            String, korrekte ID für Text
            String, (optional) Absatz der zu entsprechender ID zugehörig ist
                    ! Falls kein Absatz gefunden werden kann wird false zurückgegeben
    """
    # Bei Band eins beginnend hochzählen
    band = 0
    for m in idanzahl:
        # zu geringe Bände überspringen
        if absatznummer > m-1:
            absatznummer -= m
            band += 1
        # Entsprechendes Element ausgeben
        else:
            break
    # ID speichern
    sid = alleidsnorm[band][absatznummer]
    print("Die ID ddes gesuchten Absatzes lautet: " + str(sid))

    # Rückgabe des Absatzes in der originalen Absatzliste entsprechend der ID
    try:
        if getid:
            return sid
        else:
            return alledokumenteorig[band][alleidsorig[band].index(str(sid))], sid
    except:
        return False


def printstr (data:bs, ancor:str, printalways:list):
    """
        Gibt den String mit dem Text aus für die Ausgabe
        Input: 
            data:           bs,     Zu durchsuchendes BeautifulSoup-Element
            ancor:          str,    ZielID
            printalways:    list,   Liste der Tagnamen für Tags, die immer ausgegeben werden sollen
        Output:
            String, Aufbereiteter String mit Überschriften nicht gesuchter divs und das komplette div, das ancor als ID enthält
    """
    ret = ""
    # Alle Elemente Überprüfen
    for elem in data.contents:
        # Elemente die immer auszugeben sind ausgeben
        if elem.name in printalways:
            ret += elem.prettify()
        # Sonderbehandlung für divs:
        elif elem.name == "div":
            # ... falls ancor als ID enthalten ist:
            if elem.find(id=str(ancor)) != None:
                # Bei übergeordneterm div Rekursion anstoßen
                if elem.find(id=str(ancor), recursive=False) == None:
                    ret += "<div n=" + elem["n"] + ">"
                    ret += printstr(elem, ancor, printalways)
                    ret += "</div>"
                    ret += "<hr>"
                # ... sonst: Ausgabe des kompletten Divs
                else:
                    ret += elem.prettify()
                    ret += "<hr>"
            # ... ansonsten: div-container setzen und Elemente die immer auszugeben sind ausgeben
            else:
                ret += "<div n=" + elem["n"] + ">"
                for content in elem.contents:
                    if content.name in printalways:
                        ret += content.prettify()
                ret += "</div>"
                ret += "<hr>"

    return ret