#!/usr/bin/env python3
"""
Timewarrior Daily Report
Detaillierter Tagesbericht mit Feiertagserkennung
"""

import subprocess
import json
import os
from datetime import datetime, date, timedelta
import argparse

def load_holidays():
    """Lade Feiertage aus lokaler Datei"""
    holidays_file = os.path.expanduser('~/.timewarrior/data/holidays/holidays.json')
    try:
        with open(holidays_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def load_vacations():
    """Lade Urlaubsdaten aus lokaler Datei"""
    vacation_file = os.path.expanduser('~/.timewarrior/data/vacation/vacation.json')
    try:
        with open(vacation_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def is_holiday(check_date):
    """Prüfe ob gegebenes Datum ein Feiertag ist"""
    holidays = load_holidays()
    if isinstance(check_date, str):
        date_str = check_date
    else:
        date_str = check_date.strftime('%Y-%m-%d')
    return holidays.get(date_str, None)

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

def get_timewarrior_data(date_str):
    """Hole Timewarrior-Daten für gegebenes Datum"""
    try:
        # Hole summary für den Tag
        result = subprocess.run(['timew', 'summary', date_str, ':ids'], 
                              capture_output=True, text=True, check=True)
        
        # Hole export für detaillierte Daten
        export_result = subprocess.run(['timew', 'export', date_str], 
                                     capture_output=True, text=True, check=True)
        
        summary_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Parse Export JSON
        export_data = []
        if export_result.stdout.strip():
            try:
                export_data = json.loads(export_result.stdout)
            except:
                export_data = []
        
        return summary_lines, export_data
        
    except subprocess.CalledProcessError:
        return [], []

def parse_total_time(summary_lines):
    """Extrahiere Gesamtzeit aus Summary"""
    for line in summary_lines:
        if 'Total' in line:
            parts = line.split()
            for part in parts:
                if ':' in part:  # Format HH:MM
                    return part
                elif 'h' in part:  # Format Xh oder X.Xh
                    return part
    return "0:00"

def format_duration(seconds):
    """Formatiere Sekunden zu HH:MM"""
    if seconds is None:
        return "0:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}:{minutes:02d}"

def generate_daily_report(target_date):
    """Generiere detaillierten Tagesbericht"""
    
    if isinstance(target_date, str):
        date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        date_str = target_date
    else:
        date_obj = target_date
        date_str = target_date.strftime('%Y-%m-%d')
    
    weekday = date_obj.strftime('%A')
    weekday_de = {
        'Monday': 'Montag', 'Tuesday': 'Dienstag', 'Wednesday': 'Mittwoch',
        'Thursday': 'Donnerstag', 'Friday': 'Freitag', 'Saturday': 'Samstag', 'Sunday': 'Sonntag'
    }.get(weekday, weekday)
    
    print(f"\n{'='*80}")
    print(f"TAGESBERICHT: {date_obj.strftime('%d.%m.%Y')} ({weekday_de})")
    print(f"{'='*80}")
    
    # Prüfe Feiertag/Urlaub
    holiday_name = is_holiday(date_obj)
    vacation = is_vacation(date_obj)
    
    if holiday_name:
        print(f"🎉 FEIERTAG: {holiday_name}")
        print(f"{'='*80}")
        return
    
    if vacation:
        print(f"🏖️  {vacation['type'].upper()}: {vacation['name']}")
        print(f"{'='*80}")
        return
    
    # Hole Timewarrior-Daten
    summary_lines, export_data = get_timewarrior_data(date_str)
    
    if not export_data:
        print("📭 Keine Zeiterfassung für diesen Tag")
        print(f"{'='*80}")
        return
    
    # Gesamtzeit
    total_time = parse_total_time(summary_lines)
    print(f"⏰ GESAMTARBEITSZEIT: {total_time}")
    print(f"{'='*80}")
    
    # Detaillierte Aufschlüsselung nach Projekten/Tags
    projects = {}
    total_seconds = 0
    
    for entry in export_data:
        if 'end' not in entry:  # Aktive Einträge überspringen für Tagesbericht
            continue
            
        start = datetime.fromisoformat(entry['start'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(entry['end'].replace('Z', '+00:00'))
        duration = (end - start).total_seconds()
        total_seconds += duration
        
        # Projektname aus Tags
        tags = entry.get('tags', [])
        project = tags[0] if tags else 'Ohne Projekt'
        
        if project not in projects:
            projects[project] = {'duration': 0, 'entries': []}
        
        projects[project]['duration'] += duration
        projects[project]['entries'].append({
            'start': start,
            'end': end,
            'duration': duration,
            'tags': tags
        })
    
    # Zeige Projekte sortiert nach Dauer
    if projects:
        print("📋 AUFSCHLÜSSELUNG NACH PROJEKTEN:")
        print(f"{'-'*80}")
        print(f"{'Projekt':<30} {'Zeit':<10} {'Anteil':<8} {'Einträge'}")
        print(f"{'-'*80}")
        
        for project, data in sorted(projects.items(), key=lambda x: x[1]['duration'], reverse=True):
            duration_str = format_duration(data['duration'])
            percentage = (data['duration'] / total_seconds * 100) if total_seconds > 0 else 0
            entry_count = len(data['entries'])
            
            print(f"{project:<30} {duration_str:<10} {percentage:6.1f}% {entry_count:2d}x")
    
    print(f"{'-'*80}")
    
    # Detaillierte Zeiteinträge
    print("\n🕐 DETAILLIERTE ZEITEINTRÄGE:")
    print(f"{'-'*80}")
    print(f"{'Zeit':<15} {'Dauer':<8} {'Projekt/Tags'}")
    print(f"{'-'*80}")
    
    sorted_entries = []
    for project, data in projects.items():
        for entry in data['entries']:
            sorted_entries.append((entry, project))
    
    # Sortiere nach Startzeit
    sorted_entries.sort(key=lambda x: x[0]['start'])
    
    for entry, project in sorted_entries:
        start_time = entry['start'].strftime('%H:%M')
        end_time = entry['end'].strftime('%H:%M')
        duration_str = format_duration(entry['duration'])
        tags_str = ', '.join(entry['tags']) if entry['tags'] else project
        
        print(f"{start_time}-{end_time:<8} {duration_str:<8} {tags_str}")
    
    print(f"{'-'*80}")
    
    # Arbeitszeit-Bewertung
    total_hours = total_seconds / 3600
    print(f"\n📊 BEWERTUNG:")
    
    if total_hours >= 8:
        print(f"✅ Vollzeit erreicht ({total_hours:.1f}h)")
    elif total_hours >= 6:
        print(f"⚠️  Teilzeit ({total_hours:.1f}h)")
    elif total_hours > 0:
        print(f"🔸 Kurze Arbeitszeit ({total_hours:.1f}h)")
    else:
        print(f"❌ Keine Arbeitszeit erfasst")
    
    if total_hours >= 10:
        print(f"⚠️  Überstunden! 10h-Grenze erreicht ({total_hours:.1f}h)")
    
    print(f"{'='*80}\n")

def main():
    parser = argparse.ArgumentParser(description='Timewarrior Daily Report')
    parser.add_argument('date', nargs='?', help='Datum (YYYY-MM-DD), Standard: heute')
    parser.add_argument('--yesterday', action='store_true', help='Gestern anzeigen')
    parser.add_argument('--week', action='store_true', help='Letzte 7 Tage anzeigen')
    
    args = parser.parse_args()
    
    if args.week:
        # Zeige letzte 7 Tage
        today = date.today()
        for i in range(6, -1, -1):
            target_date = today - timedelta(days=i)
            generate_daily_report(target_date)
    elif args.yesterday:
        yesterday = date.today() - timedelta(days=1)
        generate_daily_report(yesterday)
    elif args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
            generate_daily_report(target_date)
        except ValueError:
            print("❌ Ungültiges Datumsformat. Verwende: YYYY-MM-DD")
    else:
        # Standard: heute
        generate_daily_report(date.today())

if __name__ == '__main__':
    main()
