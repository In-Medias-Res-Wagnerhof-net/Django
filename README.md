# Django
Source Code für das das Masterarbeitsprojekt einer semantischen Suche für das Gesamtwerk von Immanuel Kant.

Die Webseite mit der implementierten Suche (entsprechend diesem Repositorium) ist unter folgendem Link zu finden:
[in-medias-res.wagnerhof.net](https://in-medias-res.wagnerhof.net)

---

Enthalten sind:

- **Django**: Dajngo Projekt
- **Trivia**: Sonstige Informationen

---

## Djangoprojekt

Vollständiges Djangoprojekt mit allen Daten und Modellen, das lauffähig ist. Bereit zur Veröffentlichung auf der Webseite. 
- Es gibt ein CSS-Stylesheet.
- Alle haben eine Überschrift, eine "Navigation" und ein Favicon. 

- Es gibt eine Datenbank:
    - Modell ***Suchbegriff*** mit
        - *suchbegriff_text* (String mit max. 200 Zeichen): Suchtext für einzelne Suche
        - *anzahl* (Integer mit Defaultwert 0): Anzahl der Suchaufrufe dieses Suchtextes
        - 4 mal *absatz* (String mit max. 79 Zeichen): Zielabsätze für alle Modelle

- Folgende Seiten sind implementiert:
    - **Startseite** (Index)
    - **Suchseite**
    - **Hintergrundseite**
    - **Auswertungsseite**
    - **Dankseite**
    - **Datenschutzseite**
    - **Ergebnisübersichtsseite**
    - **Ergebniskontextseite**

### Startseite

Startseite mit Liste der häufigst gesuchten Sucheingaben und einer allgemeinen Einführung in das Projekt / Übersicht.

### Suchseite

Suchformular zur Eingabe des Suchstrings (200 Zeichen):
- verlinkt auf Ergebnis bei guter Eingabe
- sonst wird wieder die Suchseite aufgerufen
- ermöglicht die Auswahl des Suchmodells

### Hintergrundseite

Seite mit Informationen zur Suche.

### Auswertungsseite

Seite mit Informationen zur Auswertung.

### Dankseite

Seite mit Dank für Open Source Projekte und dedizierte Erlaubnis der Nutzung, sowie Dank für Unterstützung.

### Datenschutzseite

Seite mit Datenschutzbestimmungsinhalten.

### Ergebnisübersichtsseite

Seite zum anzeigen einer Übersicht aller den Parametern entsprechenden Ergebnisse:
- Es gibt zehn Ergebnisse pro gewähltem Modell
- jeder Treffer verlinkt auf seine Kontextseite

### Ergebniskontextseite

Seite zum aufzeigen der Ergebnisse:
- Der Zielabsatz wird als Anker gesetzt (Sprungpunkt zum Öffnen der Seite).
- Zusatzinformationen zum Seitenbeginn Sucheingabe als Überschrift und des aktuellen Bandes.
- Der Ergebnistext wird verkleinert auf Kapitel des Ergebnisses und erhält trotzdem Überschriften.

---

## Trivia

### .gitignore

Kantkorpus und Datenbankmigrationen werden nicht übertragen.

### Dependencies

- django
- bs4
- lxml
- urllib
- sentence_transformer

### TODO

Mittelfristig:
- Appendix

Langfristig:
- Suchleiste auch auf der Ergebnisseite, damit man gleich weitersuchen kann.
