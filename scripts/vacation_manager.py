#!/usr/bin/env python3
"""
Timewarrior Vacation Manager
Verwaltet Urlaub, Krankheit und andere Abwesenheiten
"""

import json
import os
import argparse
from datetime import datetime, date, timedelta

def load_vacations():
    """Lade Urlaubsdaten aus lokaler Datei"""
    vacation_file = os.path.expanduser('~/.timewarrior/data/vacation/vacation.json')
    try:
        with open(vacation_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_vacations(vacations):
    """Speichere Urlaubsdaten in lokaler Datei"""
    vacation_dir = os.path.expanduser('~/.timewarrior/data/vacation')
    os.makedirs(vacation_dir, exist_ok=True)
    
    vacation_file = os.path.join(vacation_dir, 'vacation.json')
    with open(vacation_file, 'w', encoding='utf-8') as f:
        json.dump(vacations, f, ensure_ascii=False, indent=2)

def add_vacation(start_date, end_date, name, vacation_type='Urlaub'):
    """Füge neuen Urlaub hinzu"""
    vacations = load_vacations()
    
    # Konvertiere zu Strings falls nötig
    if isinstance(start_date, date):
        start_str = start_date.strftime('%Y-%m-%d')
    else:
        start_str = start_date
        
    if isinstance(end_date, date):
        end_str = end_date.strftime('%Y-%m-%d')
    else:
        end_str = end_date
    
    # Berechne Anzahl Tage
    start_obj = datetime.strptime(start_str, '%Y-%m-%d').date()
    end_obj = datetime.strptime(end_str, '%Y-%m-%d').date()
    days = (end_obj - start_obj).days + 1
    
    vacation_entry = {
        'start': start_str,
        'end': end_str,
        'name': name,
        'type': vacation_type,
        'days': days,
        'created': datetime.now().isoformat()
    }
    
    vacations.append(vacation_entry)
    save_vacations(vacations)
    
    return vacation_entry

def remove_vacation(index):
    """Entferne Urlaub nach Index"""
    vacations = load_vacations()
    
    if 0 <= index < len(vacations):
        removed = vacations.pop(index)
        save_vacations(vacations)
        return removed
    return None

def list_vacations(year=None, vacation_type=None):
    """Liste alle Urlaube auf"""
    vacations = load_vacations()
    
    # Filter nach Jahr
    if year:
        vacations = [v for v in vacations if v['start'].startswith(str(year))]
    
    # Filter nach Typ
    if vacation_type:
        vacations = [v for v in vacations if v['type'].lower() == vacation_type.lower()]
    
    if not vacations:
        print("Keine Urlaubseinträge gefunden.")
        return
    
    print(f"\n{'='*80}")
    print(f"URLAUB/ABWESENHEITEN{' ' + str(year) if year else ''}")
    print(f"{'='*80}")
    print(f"{'Nr':<3} {'Von':>10} {'Bis':>10} {'Tage':>5} {'Typ':>10} {'Beschreibung'}")
    print(f"{'-'*80}")
    
    total_days = 0
    for i, vacation in enumerate(vacations):
        start_date = datetime.strptime(vacation['start'], '%Y-%m-%d').date()
        end_date = datetime.strptime(vacation['end'], '%Y-%m-%d').date()
        
        print(f"{i:<3} {start_date.strftime('%d.%m.%Y'):>10} {end_date.strftime('%d.%m.%Y'):>10} "
              f"{vacation['days']:>5} {vacation['type']:>10} {vacation['name']}")
        
        total_days += vacation['days']
    
    print(f"{'-'*80}")
    print(f"Gesamt: {total_days} Tage")
    print(f"{'='*80}\n")

def is_vacation(check_date):
    """Prüfe ob gegebenes Datum ein Urlaubstag ist"""
    vacations = load_vacations()
    
    if isinstance(check_date, str):
        date_str = check_date
    else:
        date_str = check_date.strftime('%Y-%m-%d')
    
    for vacation in vacations:
        if vacation['start'] <= date_str <= vacation['end']:
            return vacation
    return None

def check_today():
    """Prüfe ob heute Urlaub ist"""
    today = date.today()
    vacation = is_vacation(today)
    
    if vacation:
        print(f"🏖️  Heute ({today.strftime('%d.%m.%Y')}) ist {vacation['type']}: {vacation['name']}")
    else:
        print(f"💼 Heute ({today.strftime('%d.%m.%Y')}) ist ein normaler Arbeitstag.")
        
        # Zeige nächsten Urlaub
        vacations = load_vacations()
        future_vacations = [v for v in vacations 
                          if datetime.strptime(v['start'], '%Y-%m-%d').date() > today]
        
        if future_vacations:
            # Sortiere nach Startdatum
            future_vacations.sort(key=lambda x: x['start'])
            next_vacation = future_vacations[0]
            next_date = datetime.strptime(next_vacation['start'], '%Y-%m-%d').date()
            days_until = (next_date - today).days
            
            print(f"🗓️  Nächster Urlaub: {next_vacation['name']} ab {next_date.strftime('%d.%m.%Y')} (in {days_until} Tagen)")

def vacation_stats(year=None):
    """Zeige Urlaubsstatistiken"""
    vacations = load_vacations()
    
    if year:
        vacations = [v for v in vacations if v['start'].startswith(str(year))]
    
    if not vacations:
        print(f"Keine Urlaubsdaten für {year or 'alle Jahre'} gefunden.")
        return
    
    # Gruppiere nach Typ
    by_type = {}
    total_days = 0
    
    for vacation in vacations:
        vtype = vacation['type']
        days = vacation['days']
        
        if vtype not in by_type:
            by_type[vtype] = {'count': 0, 'days': 0}
        
        by_type[vtype]['count'] += 1
        by_type[vtype]['days'] += days
        total_days += days
    
    print(f"\n{'='*50}")
    print(f"URLAUBSSTATISTIK{' ' + str(year) if year else ''}")
    print(f"{'='*50}")
    
    for vtype, stats in by_type.items():
        print(f"{vtype:15}: {stats['count']:2} Einträge, {stats['days']:3} Tage")
    
    print(f"{'-'*50}")
    print(f"{'Gesamt':15}: {len(vacations):2} Einträge, {total_days:3} Tage")
    print(f"{'='*50}\n")

def main():
    parser = argparse.ArgumentParser(description='Timewarrior Vacation Manager')
    
    # Unterkommandos
    subparsers = parser.add_subparsers(dest='command', help='Verfügbare Befehle')
    
    # Add vacation
    add_parser = subparsers.add_parser('add', help='Urlaub hinzufügen')
    add_parser.add_argument('start', help='Startdatum (YYYY-MM-DD)')
    add_parser.add_argument('end', help='Enddatum (YYYY-MM-DD)')
    add_parser.add_argument('name', help='Beschreibung des Urlaubs')
    add_parser.add_argument('--type', default='Urlaub', help='Typ (Urlaub, Krankheit, etc.)')
    
    # List vacations
    list_parser = subparsers.add_parser('list', help='Urlaube auflisten')
    list_parser.add_argument('--year', type=int, help='Nur bestimmtes Jahr')
    list_parser.add_argument('--type', help='Nur bestimmter Typ')
    
    # Remove vacation
    remove_parser = subparsers.add_parser('remove', help='Urlaub entfernen')
    remove_parser.add_argument('index', type=int, help='Index des zu entfernenden Urlaubs')
    
    # Stats
    stats_parser = subparsers.add_parser('stats', help='Urlaubsstatistiken')
    stats_parser.add_argument('--year', type=int, help='Nur bestimmtes Jahr')
    
    # Check today
    subparsers.add_parser('today', help='Heutigen Status prüfen')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        try:
            vacation = add_vacation(args.start, args.end, args.name, args.type)
            print(f"✅ Urlaub hinzugefügt: {vacation['name']} ({vacation['days']} Tage)")
        except ValueError as e:
            print(f"❌ Ungültiges Datum: {e}")
            
    elif args.command == 'list':
        list_vacations(args.year, args.type)
        
    elif args.command == 'remove':
        removed = remove_vacation(args.index)
        if removed:
            print(f"✅ Urlaub entfernt: {removed['name']}")
        else:
            print(f"❌ Ungültiger Index: {args.index}")
            
    elif args.command == 'stats':
        vacation_stats(args.year)
        
    elif args.command == 'today':
        check_today()
        
    else:
        # Standard: Zeige heutigen Status und Hilfe
        check_today()
        print("\n📖 Verfügbare Befehle:")
        print("timew-vacation add 2024-07-15 2024-07-30 'Sommerurlaub'")
        print("timew-vacation add 2024-06-10 2024-06-10 'Arzttermin' --type Krankheit")
        print("timew-vacation list                    # Alle Urlaube")
        print("timew-vacation list --year 2024        # Nur 2024")
        print("timew-vacation stats                   # Statistiken")
        print("timew-vacation remove 0                # Ersten Urlaub entfernen")

if __name__ == '__main__':
    main()
