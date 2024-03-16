# importiere genutzte Django Bibliotheken
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Suchbegriff

# optional: importiere Bibliotheken zur Verschönerung des Textes und allgemeinen Funktionsweise
from urllib.parse import unquote
from bs4 import BeautifulSoup as bs

# Importiere benutzte Bibliotheken für NLP-Teil
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def index(request):
    '''
        Startseite
        1 Feld mit häufigsten Begriffen wird aus Datenbank erstellt.
    '''
    ''' 1 Häufigste Begriffe erstellen '''
    # Häufigste Begriffe heraussuchen
    häufigste_begriffe = Suchbegriff.objects.order_by("-anzahl")[:5]
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


def ergebnis(request, begriff):
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

    ''' 1 Abgleich des Suchbegriffs mit der Datenbank '''
     # Teste ob Begriff schon existiert
    try:
        sb = Suchbegriff.objects.get(suchbegriff_text=begriff)
    # ...sonst lege Begriff neu an
    except Suchbegriff.DoesNotExist:
        sb = Suchbegriff(suchbegriff_text=begriff, absatz="None")


    ''' 1 Suchbegriff mit erstellten Vektoren nach bestem Treffer abgleichen '''
    # Wenn noch kein Ergebnisabsatz zu dem Suchbegriff gespeichert wurde, ziehe Vergleich
    if sb.absatz == "None":
        # Lade Model und Korpusvektoren zu diesem Modell
        bi_model = SentenceTransformer(pfad + "bi-electra-ms-marco-german-uncased")
        features_docs = np.loadtxt(pfad + "1.txt")
        for i in range(2,10):
            features_docs = np.concatenate((features_docs, np.loadtxt(pfad + str(i) + ".txt")))

        # Erstelle Vektoren zu Suchbegriff
        features_queries = bi_model.encode(queries)

        # Erstelle Cosinus-Vergleich zwischen allen Absätzen des Korpus und der Eingabe des Suchbegriffs
        sim = cosine_similarity(features_queries, features_docs)

        # Suche bestes Suchergebnis
        for i, query in enumerate(queries):
            ranks = np.argsort(-sim[i])
            # Ergebnisabsatz für Kontext bereithalten und in Datenbank speichern
            ancor = ranks[0]
            sb.absatz = str(ranks[0])
            sb.save()
    # ...sonst ziehe Ergebnisabsatz aus Datenbank
    else:
        ancor = sb.absatz
    
    ''' 1 Ausgabedatei Erstellen '''
    # Versuche Datei für Ausgabe zu lesen
    try:
        # mapping laden
        f = open(pfad + "mapping.txt")
        mapping = f.read().split("\n")
        f.close()
        for m in range(len(mapping)):
            mapping[m] = int(mapping[m])
        # Band und tatsächliche ID bestimmen
        band = 1
        absatz = int(ancor)
        for m in mapping:
            # zu geringe Bände überspringen
            if absatz > m:
                absatz -= m
                band += 1
            # Entsprechendes Element speichern
            else:
                break
        ancor = str(band) + "." + str(absatz)
        f = open( pfad + "Korpustexte/" + str(band) + "_out.xml")
        tei = f.read()
        data = bs(tei, 'xml')
        f.close()

        # Dateiformatierung verschönern und für Kontext speichern
        ret += "<div n='1'>"
        if data.find(id=ancor).parent.name == "div" and data.find(id=ancor).parent["n"] == "1":
            p = True
        else:
            p = False
        for d in data.find(id=str(ancor)).parents:
            if d.has_attr("n") and d["n"] == "1":
                for t in d:
                    if t.name == "h3":
                        ret += t.prettify()
                    elif t.name == "div" and t["n"] == "2" and t.find(id=str(ancor)) != None:
                        ret += "<hr>"
                        ret += t.prettify()
                        ret += "<hr>"
                    elif t.name == "group" and t.find(id=str(ancor)) != None:
                        ret += "<hr>"
                        if t["type"] == "footnotes":
                            ret += "<h3>Fußnoten</h3>"
                        elif t["type"] == "marginalia":
                            ret += "<h3>Marginalia</h3>"
                        ret += t.prettify()
                        ret += "<hr>"
                    elif p and t.name == "p":
                        ret += t.prettify()
        ret += "</div>"

        # Erhöhe die Anzahl der Suchen nach diesem Begriff um eins
        sb.anzahl += 1
        sb.save()
    # ... sonst gebe einen Fehler aus
    except IOError:
        ret = "<p>Die Datei konnte nicht geladen werden.</p>"
        
    return render(request, "GUI/ergebnis.html", {"begriff": begriff, "text": ret, "band": band, "anchor": str(ancor)})

@csrf_exempt
def ergebnisse(request):
    '''
        Behandlung des Abschicken eines Suchformulars
        1 Eingaben überprüfen und Weiterleitung an entsprechende Funktion
    '''
    ''' 1 Eingaben überprüfen und Weiterleitung '''
    # Versuche Suchbegriff zu erhalten
    try:
        suchbegriff = request.POST["suchbegriff"]
    # ... funktioniert dies nicht, springe zurück zu Suchformular und werfe Fehler
    except (KeyError):

        return render( request, "GUI/suche.html", {"error_message": "Die Eingaben waren unzureichend."} )
    # ... funktioniert es, leite weiter zur Suchergebnisseite
    else:
        return HttpResponseRedirect(reverse("ergebnis", kwargs={"begriff": suchbegriff}))
