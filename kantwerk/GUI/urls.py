from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("hintergrund/", views.hintergrund, name="hintergrund"),
    path("dank/", views.dank, name="dank"),
    path("datenschutz/", views.datenschutz, name="datenschutz"),
    path("suche/", views.suche, name="suche"),
    path("suche/ergebnis/<str:begriff>/<str:modell>/<str:treffer>", views.ergebnis, name="ergebnis"),
    path("suche/ergebnis/<str:begriff>", views.ergebnis, name="ergebnis"),
    path("suche/berechnung/", views.berechnung, name="berechnung"),
    path("suche/ergebnisse/<str:begriff>/<str:modelle>", views.ergebnisse, name="ergebnisse"),
]

