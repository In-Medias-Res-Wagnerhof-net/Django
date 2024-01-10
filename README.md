# Django
Source Code für das das Masterarbeitsprojekt einer semantischen Suche für das Gesamtwerk von Immanuel Kant.

[Link](http://www.in-medias-res.wagnerhof.net)

[temporärer Link](http://138.201.94.48/plesk-site-preview/in-medias-res.wagnerhof.net/https/172.31.1.100)

---

Enthalten sind:

- **Django**: Dajngo Projekt
- **Trivia**: Sonstige Informationen

---

## Djangoprojekt

Vollständiges Djangoprojekt mit allen Daten und Modellen, das lauffähig ist. Bereit zur Veröffentlichung auf der Webseite. 
- Es gibt ein rudimentäres CSS-Stylesheet.
- Alle haben eine Überschrift, eine "Navigation" und ein Favicon. 

- Es gibt eine Datenbank:
    - Modell ***Suchbegriff*** mit
        - *suchbegriff_text* (String mit max. 200 Zeichen): Suchtext für einzelne Suche
        - *anzahl* (Integer mit Defaultwert 0): Anzahl der Suchaufrufe dieses Suchtextes
        - *absatz* (String mit max. 7 Zeichen): Absatz, in dem bestes Ergebnis zu finden ist

- Folgende Seiten sind implementiert:
    - **Startseite** (Index)
    - **Dankseite**
    - **Suchseite**
    - **Ergebnisseite**

### Startseite

Startseite mit Liste der häufigst gesuchten Sucheingaben.

### Dankseite

Seite mit Dank für Open Source Projekte und dedizierte Erlaubnis der Nutzung, sowie Dank für Unterstützung.

### Suchseite

Suchformular zur Eingabe des Suchstrings (200 Zeichen):
- verlinkt auf Ergebnis bei guter Eingabe
- sonst wird wieder die Suchseite aufgerufen
- !CSRF-Token wurde ausgeschaltet, da es nicht funktioniert ist und keine Gefahr davon ausgeht

### Ergebnisseite

Seite zum aufzeigen der Ergebnisse:
- Der Zielabsatz:
    - wird berechnet falls nötig
    - wird gekennzeichnet, 
    - wird als Anker gesetzt (Sprungpunkt zum Öffnen der Seite)
- Zusatzinformationen zum Seitenbeginn:
    - Sucheingabe als Überschrift
    - Angabe des Zielbandes (bisher hardcodiert auf 1)

---

## Trivia

### .gitignore

Kantkorpus und Datenbankmigrationen werden nicht übertragen.
