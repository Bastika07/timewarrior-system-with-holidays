#!/usr/bin/env python3
"""
Timewarrior Regional Holiday Manager
Verwaltet deutsche Feiertage mit Bundesland-spezifischen Feiertagen
"""

import json
import os
import argparse
from datetime import datetime, date, timedelta
import subprocess

# Deutsche Bundesländer
BUNDESLAENDER = {
    'BW': 'Baden-Württemberg',
    'BY': 'Bayern', 
    'BE': 'Berlin',
    'BB': 'Brandenburg',
    'HB': 'Bremen',
    'HH': 'Hamburg',
    'HE': 'Hessen',
    'MV': 'Mecklenburg-Vorpommern',
    'NI': 'Niedersachsen',
    'NW': 'Nordrhein-Westfalen',
    'RP': 'Rheinland-Pfalz',
    'SL': 'Saarland',
    'SN': 'Sachsen',
    'ST': 'Sachsen-Anhalt',
    'SH': 'Schleswig-Holstein',
    'TH': 'Thüringen'
}

def get_config_dir():
    """Hole Konfigurationsverzeichnis"""
    return os.path.expanduser('~/.timewarrior/data/config')

def save_state_config(state_code):
    """Speichere Bundesland-Konfiguration"""
    config_dir = get_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    
    config_file = os.path.join(config_dir, 'regional.json')
    config = {
        'state': state_code,
        'state_name': BUNDESLAENDER.get(state_code, 'Unbekannt'),
        'updated': datetime.now().isoformat()
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_state_config():
    """Lade Bundesland-Konfiguration"""
    config_file = os.path.join(get_config_dir(), 'regional.json')
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def calculate_easter(year):
    """Berechne Ostersonntag für gegebenes Jahr (Gregorianischer Kalender)"""
    # Algorithmus nach Gauß
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    
    return date(year, month, day)

def get_german_holidays(year, state_code=None):
    """Erstelle deutsche Feiertage für gegebenes Jahr und Bundesland"""
    holidays = {}
    
    # Bundesweite Feiertage
    holidays[f"{year}-01-01"] = "Neujahr"
    holidays[f"{year}-05-01"] = "Tag der Arbeit"
    holidays[f"{year}-10-03"] = "Tag der Deutschen Einheit"
    holidays[f"{year}-12-25"] = "1. Weihnachtsfeiertag"
    holidays[f"{year}-12-26"] = "2. Weihnachtsfeiertag"
    
    # Berechne bewegliche Feiertage basierend auf Ostern
    easter = calculate_easter(year)
    
    # Karfreitag (2 Tage vor Ostern) - bundesweit
    karfreitag = easter - timedelta(days=2)
    holidays[karfreitag.strftime('%Y-%m-%d')] = "Karfreitag"
    
    # Ostermontag (1 Tag nach Ostern) - bundesweit
    ostermontag = easter + timedelta(days=1)
    holidays[ostermontag.strftime('%Y-%m-%d')] = "Ostermontag"
    
    # Christi Himmelfahrt (39 Tage nach Ostern) - bundesweit
    himmelfahrt = easter + timedelta(days=39)
    holidays[himmelfahrt.strftime('%Y-%m-%d')] = "Christi Himmelfahrt"
    
    # Pfingstmontag (50 Tage nach Ostern) - bundesweit
    pfingstmontag = easter + timedelta(days=50)
    holidays[pfingstmontag.strftime('%Y-%m-%d')] = "Pfingstmontag"
    
    # Regionale Feiertage basierend auf Bundesland
    if state_code:
        
        # Heilige Drei Könige (6. Januar)
        if state_code in ['BW', 'BY', 'ST']:
            holidays[f"{year}-01-06"] = "Heilige Drei Könige"
        
        # Fronleichnam (60 Tage nach Ostern)
        if state_code in ['BW', 'BY', 'HE', 'NW', 'RP', 'SL']:
            fronleichnam = easter + timedelta(days=60)
            holidays[fronleichnam.strftime('%Y-%m-%d')] = "Fronleichnam"
        
        # Erweitert: Fronleichnam auch in Teilen von Sachsen und Thüringen
        if state_code in ['SN', 'TH']:
            fronleichnam = easter + timedelta(days=60)
            holidays[fronleichnam.strftime('%Y-%m-%d')] = "Fronleichnam (regional)"
        
        # Mariä Himmelfahrt (15. August)
        if state_code in ['BY', 'SL']:
            holidays[f"{year}-08-15"] = "Mariä Himmelfahrt"
        
        # Reformationstag (31. Oktober)
        if state_code in ['BB', 'HB', 'HH', 'MV', 'NI', 'SN', 'ST', 'SH', 'TH']:
            holidays[f"{year}-10-31"] = "Reformationstag"
        
        # Allerheiligen (1. November)  
        if state_code in ['BW', 'BY', 'NW', 'RP', 'SL']:
            holidays[f"{year}-11-01"] = "Allerheiligen"
        
        # Buß- und Bettag (Mittwoch vor dem 23. November) - nur Sachsen
        if state_code == 'SN':
            # Finde Mittwoch vor dem 23. November
            nov_23 = date(year, 11, 23)
            days_back = (nov_23.weekday() - 2) % 7
            if days_back == 0:
                days_back = 7
            buss_bettag = nov_23 - timedelta(days=days_back)
            holidays[buss_bettag.strftime('%Y-%m-%d')] = "Buß- und Bettag"
        
        # Berliner Spezialitäten
        if state_code == 'BE':
            # Internationaler Frauentag (8. März) - seit 2019
            if year >= 2019:
                holidays[f"{year}-03-08"] = "Internationaler Frauentag"
    
    return holidays

def save_holidays(holidays):
    """Speichere Feiertage in lokaler Datei"""
    holidays_dir = os.path.expanduser('~/.timewarrior/data/holidays')
    os.makedirs(holidays_dir, exist_ok=True)
    
    holidays_file = os.path.join(holidays_dir, 'holidays.json')
    with open(holidays_file, 'w', encoding='utf-8') as f:
        json.dump(holidays, f, ensure_ascii=False, indent=2)

def load_holidays():
    """Lade Feiertage aus lokaler Datei"""
    holidays_file = os.path.expanduser('~/.timewarrior/data/holidays/holidays.json')
    try:
        with open(holidays_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def list_holidays(year=None):
    """Liste alle Feiertage auf"""
    holidays = load_holidays()
    config = load_state_config()
    
    if year:
        holidays = {k: v for k, v in holidays.items() if k.startswith(str(year))}
    
    if not holidays:
        print("Keine Feiertage gefunden. Führe --update-holidays aus.")
        return
    
    state_info = ""
    if config:
        state_info = f" ({config['state_name']})"
    
    print(f"\n{'='*70}")
    print(f"FEIERTAGE{' ' + str(year) if year else ''}{state_info}")
    print(f"{'='*70}")
    
    # Gruppiere nach Jahr für bessere Übersicht
    by_year = {}
    for date_str, name in holidays.items():
        year_key = date_str[:4]
        if year_key not in by_year:
            by_year[year_key] = []
        by_year[year_key].append((date_str, name))
    
    for year_key in sorted(by_year.keys()):
        if len(by_year) > 1:
            print(f"\n--- {year_key} ---")
        
        for date_str, name in sorted(by_year[year_key]):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            weekday = date_obj.strftime('%A')
            weekday_de = {
                'Monday': 'Mo', 'Tuesday': 'Di', 'Wednesday': 'Mi',
                'Thursday': 'Do', 'Friday': 'Fr', 'Saturday': 'Sa', 'Sunday': 'So'
            }.get(weekday, weekday)
            
            # Markiere regionale Feiertage
            regional_marker = " 🏛️" if any(x in name for x in ["Heilige Drei Könige", "Fronleichnam", "Mariä Himmelfahrt", "Reformationstag", "Allerheiligen", "Buß- und Bettag", "Frauentag", "regional"]) else ""
            
            print(f"{date_obj.strftime('%d.%m.%Y')} ({weekday_de}): {name}{regional_marker}")
    
    if config:
        print(f"\n💡 Bundesland: {config['state_name']} ({config['state']})")
        print(f"🏛️ = regionale Feiertage")
    else:
        print(f"\n⚠️  Kein Bundesland konfiguriert - nur bundesweite Feiertage!")
        print(f"   Verwende: timew-holidays --set-state [BUNDESLAND]")
    
    print(f"{'='*70}\n")

def set_state(state_code):
    """Setze Bundesland für regionale Feiertage"""
    state_code = state_code.upper()
    
    if state_code not in BUNDESLAENDER:
        print(f"❌ Ungültiges Bundesland: {state_code}")
        print(f"\nVerfügbare Bundesländer:")
        for code, name in BUNDESLAENDER.items():
            print(f"  {code} = {name}")
        return False
    
    save_state_config(state_code)
    state_name = BUNDESLAENDER[state_code]
    
    print(f"✅ Bundesland gesetzt: {state_name} ({state_code})")
    print(f"\n💡 Aktualisiere Feiertage mit regionalen Feiertagen:")
    print(f"   timew-holidays --update-holidays {datetime.now().year}")
    
    return True

def check_today():
    """Prüfe ob heute ein Feiertag ist"""
    today = date.today()
    holidays = load_holidays()
    config = load_state_config()
    
    date_str = today.strftime('%Y-%m-%d')
    holiday_name = holidays.get(date_str)
    
    if holiday_name:
        regional_info = ""
        if config and any(x in holiday_name for x in ["Heilige Drei Könige", "Fronleichnam", "Mariä Himmelfahrt", "Reformationstag", "Allerheiligen", "Buß- und Bettag", "Frauentag", "regional"]):
            regional_info = f" (🏛️ {config['state_name']})"
        
        print(f"🎉 Heute ({today.strftime('%d.%m.%Y')}) ist {holiday_name}{regional_info}!")
    else:
        print(f"📅 Heute ({today.strftime('%d.%m.%Y')}) ist kein Feiertag.")
        
        # Zeige nächsten Feiertag
        future_holidays = {k: v for k, v in holidays.items() 
                         if datetime.strptime(k, '%Y-%m-%d').date() > today}
        
        if future_holidays:
            next_date = min(future_holidays.keys())
            next_holiday = future_holidays[next_date]
            next_date_obj = datetime.strptime(next_date, '%Y-%m-%d').date()
            days_until = (next_date_obj - today).days
            
            print(f"🗓️  Nächster Feiertag: {next_holiday} am {next_date_obj.strftime('%d.%m.%Y')} (in {days_until} Tagen)")
    
    # Zeige aktuelles Bundesland
    if config:
        print(f"\n💡 Konfiguriert für: {config['state_name']} ({config['state']})")
    else:
        print(f"\n⚠️  Kein Bundesland konfiguriert! Verwende:")
        print(f"   timew-holidays --set-state [BUNDESLAND]")

def main():
    parser = argparse.ArgumentParser(description='Timewarrior Regional Holiday Manager')
    parser.add_argument('--update-holidays', type=int, metavar='YEAR', 
                       help='Aktualisiere Feiertage für Jahr (mit regionalem Bundesland)')
    parser.add_argument('--list', type=int, nargs='?', const=0, metavar='YEAR',
                       help='Liste Feiertage auf (optional: nur bestimmtes Jahr)')
    parser.add_argument('--check-today', action='store_true',
                       help='Prüfe ob heute ein Feiertag ist')
    parser.add_argument('--set-state', metavar='STATE',
                       help='Setze Bundesland (BW, BY, BE, BB, HB, HH, HE, MV, NI, NW, RP, SL, SN, ST, SH, TH)')
    parser.add_argument('--show-states', action='store_true',
                       help='Zeige alle verfügbaren Bundesländer')
    
    args = parser.parse_args()
    
    if args.set_state:
        set_state(args.set_state)
        
    elif args.show_states:
        print(f"\n{'='*50}")
        print(f"VERFÜGBARE BUNDESLÄNDER")
        print(f"{'='*50}")
        for code, name in sorted(BUNDESLAENDER.items()):
            print(f"{code:3} = {name}")
        print(f"{'='*50}\n")
        print(f"Verwendung: timew-holidays --set-state {list(BUNDESLAENDER.keys())[0]}")
        
    elif args.update_holidays:
        year = args.update_holidays
        config = load_state_config()
        state_code = config['state'] if config else None
        
        print(f"🔄 Aktualisiere Feiertage für {year}...")
        if state_code:
            print(f"   Bundesland: {config['state_name']} ({state_code})")
        else:
            print(f"   ⚠️  Nur bundesweite Feiertage (kein Bundesland konfiguriert)")
        
        # Lade bestehende Feiertage
        existing_holidays = load_holidays()
        
        # Füge neue Feiertage hinzu
        new_holidays = get_german_holidays(year, state_code)
        existing_holidays.update(new_holidays)
        
        # Speichere aktualisierte Liste
        save_holidays(existing_holidays)
        
        regional_count = len([h for h in new_holidays.values() if any(x in h for x in ["Heilige Drei Könige", "Fronleichnam", "Mariä Himmelfahrt", "Reformationstag", "Allerheiligen", "Buß- und Bettag", "Frauentag", "regional"])])
        
        print(f"✅ {len(new_holidays)} Feiertage für {year} hinzugefügt!")
        print(f"   davon {regional_count} regionale Feiertage")
        
    elif args.list is not None:
        year = args.list if args.list > 0 else None
        list_holidays(year)
        
    elif args.check_today:
        check_today()
        
    else:
        # Standard: Zeige heutigen Status und verfügbare Befehle
        check_today()
        print("\n📖 Verfügbare Befehle:")
        print("timew-holidays --set-state BY                 # Bundesland Bayern setzen")
        print("timew-holidays --show-states                  # Alle Bundesländer anzeigen")
        print("timew-holidays --update-holidays 2024         # Feiertage für 2024 (mit Bundesland)")
        print("timew-holidays --list                         # Alle Feiertage")
        print("timew-holidays --check-today                  # Heutigen Status prüfen")

if __name__ == '__main__':
    main()
