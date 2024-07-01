# importiere genutzte Django Bibliotheken
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Suchbegriff

# optional: importiere Bibliotheken zur Verschönerung des Textes und allgemeinen Funktionsweise
from urllib.parse import unquote
from urllib.parse import quote
from bs4 import BeautifulSoup as bs
from pickle import load

# Importiere benutzte Bibliotheken für NLP-Teil
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Importierte Funktionen
from .helpers import *


def index(request):
    '''
        Startseite
        1 Feld mit häufigsten Begriffen wird aus Datenbank erstellt.
    '''
    ''' 1 Häufigste Begriffe erstellen '''
    # Häufigste Begriffe heraussuchen
    häufigste_begriffe = Suchbegriff.objects.order_by("-anzahl")[:20]
    # Template und Templatekontext erstellen
    template = loader.get_template("GUI/index.html")
    context = {
        "häufigste_begriffe": häufigste_begriffe,
    }

    return HttpResponse(template.render(context, request))


def dank(request):
    '''
        Dankesseite
        1 automatisierte Dankestexte?
    '''
    # Template und Templatekontext erstellen
    template = loader.get_template("GUI/dank.html")
    context = {
    }
    
    return HttpResponse(template.render(context, request))


def hintergrund(request):
    '''
        Hintergrundseite
    '''
    # Template und Templatekontext erstellen
    template = loader.get_template("GUI/hintergrund.html")
    context = {
    }
    
    return HttpResponse(template.render(context, request))


def datenschutz(request):
    '''
        Datenschutzseite
    '''
    # Template und Templatekontext erstellen
    template = loader.get_template("GUI/datenschutz.html")
    context = {
    }
    
    return HttpResponse(template.render(context, request))


def suche(request):
    '''
        Suchseite
        1 Suchformular um einen neuen Suchbegriff anzugeben.
    '''
    ''' 1 Suchformular rendern '''

    return render(request, "GUI/suche.html")


def ergebnis(request, begriff, modell, treffer):
    '''
        Ergebnisseite
        1 Abstimmung des Suchbegriffs mit der Datenbank.
        2 Suchbegriff mit erstellten Vektoren nach bestem Treffer abgleichen.
        3 Ausgabedatei Erstellen
    '''
    # Initialisierungen
    begriff = unquote(begriff) 
    band = -1
    ret = ""
    ancor = 0
    queries = [
        begriff     # Einzelnen Eintrag statt Liste nehmen
    ]
    pfad = "../kantwerk/GUI/static/GUI/data/"
    if modell == "bielectra":
        modellname = "bi-electra-ms-marco-german-uncased"
    elif modell == "convbert":
        modellname = "convbert-base-german-europeana-cased"
    elif modell == "distilbert":
        modellname = "distilbert-base-german-europeana-cased"
    elif modell == "gelectra":
        modellname = "gelectra-large-germanquad"
    else:
        modellname = ""

    ''' 1 Abgleich des Suchbegriffs mit der Datenbank '''
     # Teste ob Begriff schon existiert
    try:
        sb = Suchbegriff.objects.get(suchbegriff_text=begriff)
    # ...sonst lege Begriff neu an
    except Suchbegriff.DoesNotExist:
        sb = Suchbegriff(suchbegriff_text=begriff, bielectra_absatz="None", convbert_absatz="None", distilbert_absatz="None", gelectra_absatz="None")


    ''' 2 Suchbegriff mit erstellten Vektoren nach bestem Treffer abgleichen '''
    # Wenn noch kein Ergebnisabsatz zu dem Suchbegriff gespeichert wurde, ziehe Vergleich
    if modell != "" and ((sb.bielectra_absatz == "None" and modell == "bielectra") or (sb.convbert_absatz == "None" and modell == "convbert") or (sb.distilbert_absatz == "None" and modell == "distilbert") or (sb.gelectra_absatz == "None" and modell == "gelectra")):
        # Lade Model und Korpusvektoren zu diesem Modell
        bi_model = SentenceTransformer(pfad + "Modelle/" + modellname)
        features_docs = np.loadtxt(pfad + "Vektoren/" + modell + "/1.txt")
        for i in range(2,10):
            features_docs = np.concatenate((features_docs, np.loadtxt(pfad + "Vektoren/" + modell + "/" + str(i) + ".txt")))

        # Erstelle Vektoren zu Suchbegriff
        features_queries = bi_model.encode(queries)

        # Erstelle Cosinus-Vergleich zwischen allen Absätzen des Korpus und der Eingabe des Suchbegriffs
        sim = cosine_similarity(features_queries, features_docs)

        # Suche bestes Suchergebnis
        for i, query in enumerate(queries):
            ranks = np.argsort(-sim[i])
            # Ergebnisabsatz für Kontext bereithalten und in Datenbank speichern
            ranksstr = ""
            for i in range(0,10):
                ranksstr += ranks[i] + "|"
            ranksstr = ranksstr[0:-1]
            ancor = ranksstr
            if modell == "bielectra":
                sb.bielectra_absatz = ranksstr
            elif modell == "convbert":
                sb.convbert_absatz = ranksstr
            elif modell == "distilbert":
                sb.distilbert_absatz = ranksstr
            elif modell == "gelectra":
                sb.gelectra_absatz = ranksstr
            sb.save()
    # ...sonst ziehe Ergebnisabsatz aus Datenbank
    elif modell != "":
        if modell == "bielectra":
            ancor = sb.bielectra_absatz
        elif modell == "convbert":
            ancor = sb.convbert_absatz
        elif modell == "distilbert":
            ancor = sb.distilbert_absatz
        elif modell == "gelectra":
            ancor = sb.gelectra_absatz
    ancor = ancor.split("|")[int(treffer)]

    ''' 3 Ausgabedatei Erstellen '''
    tei = []
    for i in range(1,10):
        tei.append(ladeTEI(i))
    with open(pfad + "Korpustexte/alleids", "rb") as fp:   # Unpickling
        alleidsnorm = load(fp)
    with open(pfad + "Korpustexte/idanzahl", "rb") as fp:   # Unpickling
        idanzahl = load(fp)
    alleidsorig, alledokumenteorig = bereite_daten(tei, modell)
    ancor = suche_absatz(alleidsnorm, alleidsorig, alledokumenteorig, idanzahl, int(ancor), True)
    band = ancor.split(".")[0]
    link = erhalte_link(ancor, pfad)

    # Versuche Datei für Ausgabe zu lesen
    try:
        f = open( pfad + "Korpustexte/" + str(band) + "_out.xml")
        tei = f.read()
        data = bs(tei, 'xml')
        f.close()

        # Dateiformatierung verschönern und für Kontext speichern
        ret += "<div n='1'>"
        printalways = ["h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8", "h9"]
        ret += printstr(data.body, ancor, printalways)
        

        ret += "</div>"

        # Erhöhe die Anzahl der Suchen nach diesem Begriff um eins
        sb.anzahl += 1
        sb.save()
    # ... sonst gebe einen Fehler aus
    except IOError:
        ret = "<p>Die Datei konnte nicht geladen werden.</p>"
        
    return render(request, "GUI/ergebnis.html", {"begriff": begriff, "text": ret, "band": band, "anchor": str(ancor), "link": link})

@csrf_exempt
def berechnung(request):
    '''
        Behandlung des Abschickens eines Suchformulars
        1 Eingaben überprüfen und Weiterleitung an entsprechende Funktion
    '''
    ''' 1 Eingaben überprüfen und Weiterleitung '''
    # Versuche Suchbegriff zu erhalten
    try:
        suchbegriff = request.POST["suchbegriff"]
        if suchbegriff == "":
            raise KeyError
        models = request.POST.getlist('models')
        if len(models) == 0:
            raise KeyError
        modelstr = ""
        for mod in models:
            modelstr += str(mod) + "|"
    # ... funktioniert dies nicht, springe zurück zu Suchformular und werfe Fehler
    except (KeyError):

        return render( request, "GUI/suche.html", {"error_message": "Die Eingaben waren unzureichend."} )
    # ... funktioniert es, leite weiter zur Suchergebnisseite
    else:
        return HttpResponseRedirect(reverse("ergebnisse", kwargs={"begriff": suchbegriff, "modelle": modelstr[:-1]}))


def ergebnisse(request, begriff, modelle):
    '''
        Ergebnisübersichtsseite
        1 Abstimmung des Suchbegriffs mit der Datenbank.
        2 Suchbegriff mit erstellten Vektoren nach bestem Treffer abgleichen.
        3 Ausgabedatei Erstellen
    '''
    # Initialisierungen
    begriff = unquote(begriff) 
    ret = ""
    ancor = 0
    queries = [
        begriff     # Einzelnen Eintrag statt Liste nehmen
    ]
    pfad = "../kantwerk/GUI/static/GUI/data/"
    modelle = modelle.split("|")

    ''' 1 Abgleich des Suchbegriffs mit der Datenbank '''
     # Teste ob Begriff schon existiert
    try:
        sb = Suchbegriff.objects.get(suchbegriff_text=begriff)
    # ...sonst lege Begriff neu an
    except Suchbegriff.DoesNotExist:
        sb = Suchbegriff(suchbegriff_text=begriff, bielectra_absatz="None", convbert_absatz="None", distilbert_absatz="None", gelectra_absatz="None")


    ''' 2 Suchbegriff mit erstellten Vektoren nach bestem Treffer abgleichen '''
    # Wenn noch kein Ergebnisabsatz zu dem Suchbegriff gespeichert wurde, ziehe Vergleich
    bandanzahl = 10
    tei = []
    for i in range(1,bandanzahl):
        tei.append(ladeTEI(i))
    with open(pfad + "Korpustexte/alleids", "rb") as fp:   # Unpickling
        alleidsnorm = load(fp)
    with open(pfad + "Korpustexte/idanzahl", "rb") as fp:   # Unpickling
        idanzahl = load(fp)
    alleidsorig, alledokumenteorig = bereite_daten(tei, low = False, bandanzahl=bandanzahl)
    modellestr = "<ul>"
    for modell in modelle:
        if modell == "bielectra":
            modellname = "bi-electra-ms-marco-german-uncased"
        elif modell == "convbert":
            modellname = "convbert-base-german-europeana-cased"
        elif modell == "distilbert":
            modellname = "distilbert-base-german-europeana-cased"
        elif modell == "gelectra":
            modellname = "gelectra-large-germanquad"
        else:
            modellname = ""
        if modell != "" and ((sb.bielectra_absatz == "None" and modell == "bielectra") or (sb.convbert_absatz == "None" and modell == "convbert") or (sb.distilbert_absatz == "None" and modell == "distilbert") or (sb.gelectra_absatz == "None" and modell == "gelectra")):
            # Lade Model und Korpusvektoren zu diesem Modell
            bi_model = SentenceTransformer(pfad + "Modelle/" + modellname)
            features_docs = np.loadtxt(pfad + "Vektoren/" + modell + "/1.txt")
            for i in range(2,10):
                features_docs = np.concatenate((features_docs, np.loadtxt(pfad + "Vektoren/" + modell + "/" + str(i) + ".txt")))

            # Erstelle Vektoren zu Suchbegriff
            features_queries = bi_model.encode(queries)

            # Erstelle Cosinus-Vergleich zwischen allen Absätzen des Korpus und der Eingabe des Suchbegriffs
            sim = cosine_similarity(features_queries, features_docs)

            # Suche bestes Suchergebnis
            for i, query in enumerate(queries):
                ranks = np.argsort(-sim[i])
                # Ergebnisabsatz für Kontext bereithalten und in Datenbank speichern
                ranksstr = ""
                for i in range(0,10):
                    ranksstr += str(ranks[i]) + "|"
                ranksstr = ranksstr[:-1]
                ancors = ranksstr
                if modell == "bielectra":
                    sb.bielectra_absatz = ranksstr
                elif modell == "convbert":
                    sb.convbert_absatz = ranksstr
                elif modell == "distilbert":
                    sb.distilbert_absatz = ranksstr
                elif modell == "gelectra":
                    sb.gelectra_absatz = ranksstr
                sb.save()
        # ...sonst ziehe Ergebnisabsatz aus Datenbank
        elif modell != "":
            if modell == "bielectra":
                ancors = sb.bielectra_absatz
            elif modell == "convbert":
                ancors = sb.convbert_absatz
            elif modell == "distilbert":
                ancors = sb.distilbert_absatz
            elif modell == "gelectra":
                ancors = sb.gelectra_absatz

        ''' 3 Ausgabedatei Erstellen '''
        ret += "<div class='box'>"
        ancors = ancors.split("|")
        ret += "<h3>" + modell + "</h3>"
        for i, ancor in enumerate(ancors):
            absatz, sid = suche_absatz(alleidsnorm, alleidsorig, alledokumenteorig, idanzahl, int(ancor))
            link, zit = erhalte_link(sid,pfad,True)
            ret += "<h4>Treffer " + str(i+1) + ": [<a href='#' onclick=\"showLoaderOnClick('/suche/ergebnis/" + quote(begriff) + "/" + modell + "/" + str(i) + "')\">" + sid + "</a>]</h4>"
            ret += "<p><a href='" + link + "'>" + zit + "</a></p>"
            ret += "<a class='button light breit kontrast' href='#' onclick=\"showLoaderOnClick('/suche/ergebnis/" + quote(begriff) + "/" + modell + "/" + str(i) + "')\">" + absatz + "</a>"

        ret += "</div>"
        modellestr += "<li>" + modell + "</li>"
    modellestr += "</ul>"
    
    return render(request, "GUI/ergebnisse.html", {"begriff": begriff, "models": modellestr, "ergebnisse": ret})