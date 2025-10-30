# Timewarrior Arbeitszeit-Management System (Complete Edition)

Ein umfassendes Zeiterfassungssystem für Timewarrior mit **regionalen deutschen Feiertagen**, automatischen Funktionen und detaillierten Reports.

## 🌟 Features

### 🏛️ Regionale Feiertage (NEU!)
- **Alle 16 deutschen Bundesländer** unterstützt
- Automatische Berechnung beweglicher Feiertage (Ostern, Pfingsten, etc.)
- Regionale Feiertage (Fronleichnam, Reformationstag, Allerheiligen, etc.)
- Spezielle Feiertage (Buß- und Bettag in Sachsen, Frauentag in Berlin)

### 🏖️ Urlaubs-/Abwesenheitsverwaltung
- Urlaub, Krankheit, Homeoffice und andere Abwesenheitsarten
- Automatische Tagesberechnung
- Übersichtliche Listen und Statistiken
- Integration in alle Reports

### 🤖 Automatische Funktionen
- **Auto-Pause**: 30min Pause bei >4h Arbeitszeit
- **Überstunden-Warnung**: Bei 10h Arbeitszeit
- **Feiertags-Erkennung**: Automatische Benachrichtigung
- **11h Ruhezeit**: Überwachung der gesetzlichen Ruhezeiten

### 📊 Umfassende Reports
- **Tägliche Reports**: Detaillierte Aufschlüsselung mit Projektanalyse
- **Wöchentliche Reports**: KW-basierte Übersichten mit Soll-Ist-Vergleich
- **Monatliche Reports**: Vollständige Monatsanalyse mit Produktivitäts-Metriken

## 🚀 Installation

### Voraussetzungen
```bash
# Ubuntu/Debian
sudo apt install timewarrior python3

# Arch Linux
sudo pacman -S timew python3

# macOS
brew install timewarrior python3
```

### Automatische Installation
```bash
# ZIP-Datei entpacken
unzip timewarrior-system-with-holidays.zip
cd timewarrior-system-with-holidays

# Setup ausführen
chmod +x setup.sh
./setup.sh
```

### Erste Konfiguration
```bash
# 1. Bundesland für regionale Feiertage setzen
timew-holidays --set-state BY  # für Bayern (siehe Liste unten)

# 2. Feiertage für aktuelles Jahr laden
timew-holidays --update-holidays 2024

# 3. Beispiel-Urlaub hinzufügen
timew-vacation add 2024-12-24 2024-12-31 'Weihnachtsurlaub'

# 4. Erste Zeiterfassung starten
timew start mein_projekt

# 5. Ersten Report anzeigen
timew-daily
```

## 📍 Deutsche Bundesländer

| Code | Bundesland |
|------|------------|
| BW   | Baden-Württemberg |
| BY   | Bayern |
| BE   | Berlin |
| BB   | Brandenburg |
| HB   | Bremen |
| HH   | Hamburg |
| HE   | Hessen |
| MV   | Mecklenburg-Vorpommern |
| NI   | Niedersachsen |
| NW   | Nordrhein-Westfalen |
| RP   | Rheinland-Pfalz |
| SL   | Saarland |
| SN   | Sachsen |
| ST   | Sachsen-Anhalt |
| SH   | Schleswig-Holstein |
| TH   | Thüringen |

## 🎯 Regionale Feiertage

Das System berücksichtigt automatisch regionale Unterschiede:

- **Heilige Drei Könige** (6. Jan): BW, BY, ST
- **Fronleichnam**: BW, BY, HE, NW, RP, SL (+ regional in SN, TH)
- **Mariä Himmelfahrt** (15. Aug): BY, SL
- **Reformationstag** (31. Okt): BB, HB, HH, MV, NI, SN, ST, SH, TH
- **Allerheiligen** (1. Nov): BW, BY, NW, RP, SL
- **Buß- und Bettag**: Nur SN
- **Internationaler Frauentag** (8. März): BE (seit 2019)

## 📋 Kommandos

### Feiertage verwalten
```bash
# Bundesland setzen
timew-holidays --set-state BY

# Alle Bundesländer anzeigen
timew-holidays --show-states

# Feiertage für Jahr aktualisieren
timew-holidays --update-holidays 2024

# Alle Feiertage anzeigen
timew-holidays --list
timew-holidays --list 2024  # nur 2024

# Heutigen Status prüfen
timew-holidays --check-today
```

### Urlaub verwalten
```bash
# Urlaub hinzufügen
timew-vacation add 2024-07-15 2024-07-30 'Sommerurlaub'
timew-vacation add 2024-06-10 2024-06-10 'Arzttermin' --type Krankheit

# Alle Urlaube anzeigen
timew-vacation list
timew-vacation list --year 2024
timew-vacation list --type Urlaub

# Urlaubsstatistiken
timew-vacation stats
timew-vacation stats --year 2024

# Urlaub entfernen
timew-vacation remove 0  # Index aus Liste

# Heutigen Status prüfen
timew-vacation today
```

### Reports generieren
```bash
# Tagesberichte
timew-daily                    # heute
timew-daily --yesterday        # gestern
timew-daily 2024-03-15        # spezifisches Datum
timew-daily --week            # letzte 7 Tage

# Wochenberichte  
timew-weekly                  # diese Woche
timew-weekly --last-week      # letzte Woche
timew-weekly --weeks 4        # letzte 4 Wochen

# Monatsberichte
timew-monthly                 # dieser Monat
timew-monthly --last-month    # letzter Monat
timew-monthly --months 3      # letzte 3 Monate
timew-monthly --year 2024 --month 6  # Juni 2024
```

## 🔧 Konfiguration

### Timewarrior Grundlagen
```bash
# Arbeitszeit starten
timew start projekt_name tag1 tag2

# Arbeitszeit stoppen
timew stop

# Status anzeigen
timew

# Heutiges Summary
timew summary :day

# Diese Woche
timew summary :week
```

### Automatische Features

#### Auto-Pause Hook
- Fügt automatisch 30min Pause ein bei >4h Arbeitszeit
- Teilt längere Arbeitsblöcke auf
- Konfigurierbar in `hooks/on-modify-autopause`

#### Überstunden-Warnung
- Warnt bei 8.5h und 10h Arbeitszeit
- Desktop-Benachrichtigungen (falls verfügbar)
- Konfigurierbar in `hooks/on-modify-warnings`

#### Feiertags-Erkennung
- Erkennt automatisch Feiertage und Urlaub
- Passt Erwartungen entsprechend an
- Berücksichtigt regionale Unterschiede

## 📊 Report-Beispiele

### Tagesbericht
```
================================================================================
TAGESBERICHT: 15.03.2024 (Freitag)
================================================================================
⏰ GESAMTARBEITSZEIT: 8:30

📋 AUFSCHLÜSSELUNG NACH PROJEKTEN:
--------------------------------------------------------------------------------
Projekt                        Zeit       Anteil   Einträge
--------------------------------------------------------------------------------
WebApp Development             5:15       61.8%    3x
Code Review                    2:00       23.5%    2x
Meeting                        1:15       14.7%    1x
--------------------------------------------------------------------------------

📊 BEWERTUNG:
✅ Vollzeit erreicht (8.5h)
```

### Wochenbericht
```
==========================================================================================
WOCHENBERICHT: KW 11/2024 (11.03. - 17.03.2024)
==========================================================================================
📅 TÄGLICHE ÜBERSICHT:
------------------------------------------------------------------------------------------
Tag          Datum        Arbeitszeit  Status          Hauptprojekte
------------------------------------------------------------------------------------------
Montag       11.03.2024   8:15         ✅ Vollzeit     WebApp, Testing
Dienstag     12.03.2024   7:45         ⚠️ Teilzeit     WebApp, Meetings
Mittwoch     13.03.2024   8:30         ✅ Vollzeit     WebApp, Code Review
Donnerstag   14.03.2024   8:00         ✅ Vollzeit     Testing, Documentation
Freitag      15.03.2024   8:30         ✅ Vollzeit     WebApp, Code Review
------------------------------------------------------------------------------------------

📊 WOCHENSUMME:
⏰ Gesamtarbeitszeit: 41:00 (41.0h)
📊 Durchschnitt/Tag: 8:12 (8.2h)
✅ Vollzeit-Woche erreicht
```

### Monatsbericht
```
====================================================================================================
MONATSBERICHT: März 2024
====================================================================================================
📊 MONATSÜBERSICHT:
----------------------------------------------------------------------------------------------------
Kalendertage:        31 Tage
Arbeitstage:         21 Tage
Feiertage:            1 Tage  (Karfreitag)
Urlaubstage:          2 Tage
Wochenenden:          7 Tage

Gesamtarbeitszeit:   168:30 (168.5h)
Durchschnitt/Tag:    8:01 (8.0h)
Sollzeit (8h/Tag):   168:00 (168.0h)
Überstunden:         +0:30 (+0.5h)
```

## 🛠️ Erweiterte Konfiguration

### Hooks anpassen
Die Hooks befinden sich in `~/.timewarrior/hooks/`:
- `on-modify-autopause`: Auto-Pause Konfiguration
- `on-modify-warnings`: Überstunden-Warnungen
- `on-modify-holidays`: Feiertags-Erkennung

### Neue Feiertage hinzufügen
Eigene Feiertage können in `~/.timewarrior/data/holidays/holidays.json` ergänzt werden:
```json
{
  "2024-12-24": "Heiligabend (Betriebsurlaub)",
  "2024-12-31": "Silvester (Betriebsurlaub)"
}
```

### Backup & Sync
```bash
# Backup aller Daten
tar -czf timewarrior-backup.tar.gz ~/.timewarrior/

# Restore
tar -xzf timewarrior-backup.tar.gz -C ~/
```

## 🐛 Troubleshooting

### Hooks werden nicht ausgeführt
```bash
# Hooks aktivieren
echo "hooks = on" >> ~/.timewarrior/timewarrior.cfg

# Berechtigungen prüfen
chmod +x ~/.timewarrior/hooks/*
```

### Keine Feiertage angezeigt
```bash
# Bundesland prüfen
timew-holidays --check-today

# Feiertage neu laden
timew-holidays --update-holidays 2024
```

### Reports zeigen keine Daten
```bash
# Daten prüfen
timew summary :month

# Export testen
timew export :day
```

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe LICENSE für Details.

## 🤝 Beitragen

Beiträge sind willkommen! Besonders für:
- Weitere regionale Feiertage
- Neue Report-Features
- Verbesserungen der Hooks
- Dokumentation

## 📞 Support

Bei Problemen oder Fragen:
1. Prüfe die Troubleshooting-Sektion
2. Überprüfe die Timewarrior-Logs: `~/.timewarrior/data/`
3. Teste mit `timew diagnostics`

---

**Viel Erfolg mit der effizienten Zeiterfassung! 🚀**
