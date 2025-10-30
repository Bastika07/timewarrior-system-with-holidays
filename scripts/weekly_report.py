#!/usr/bin/env python3
"""
Timewarrior Weekly Report
Wöchentlicher Bericht mit Feiertags- und Urlaubserkennung
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

def get_week_dates(target_date):
    """Hole alle Daten der Woche (Montag bis Sonntag)"""
    # Finde Montag der Woche
    days_since_monday = target_date.weekday()
    monday = target_date - timedelta(days=days_since_monday)
    
    week_dates = []
    for i in range(7):  # Montag bis Sonntag
        week_dates.append(monday + timedelta(days=i))
    
    return week_dates

def get_timewarrior_data_for_period(start_date, end_date):
    """Hole Timewarrior-Daten für Zeitraum"""
    try:
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        # Hole export für detaillierte Daten
        if start_str == end_str:
            export_result = subprocess.run(['timew', 'export', start_str], 
                                         capture_output=True, text=True, check=True)
        else:
            export_result = subprocess.run(['timew', 'export', f'{start_str}', f'to', f'{end_str}'], 
                                         capture_output=True, text=True, check=True)
        
        # Parse Export JSON
        export_data = []
        if export_result.stdout.strip():
            try:
                export_data = json.loads(export_result.stdout)
            except:
                export_data = []
        
        return export_data
        
    except subprocess.CalledProcessError:
        return []

def format_duration(seconds):
    """Formatiere Sekunden zu HH:MM"""
    if seconds is None or seconds == 0:
        return "0:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}:{minutes:02d}"

def generate_weekly_report(target_date):
    """Generiere wöchentlichen Bericht"""
    
    if isinstance(target_date, str):
        date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
    else:
        date_obj = target_date
    
    week_dates = get_week_dates(date_obj)
    monday = week_dates[0]
    sunday = week_dates[6]
    
    # Kalenderwoche berechnen
    year, week_num, _ = monday.isocalendar()
    
    print(f"\n{'='*90}")
    print(f"WOCHENBERICHT: KW {week_num}/{year} ({monday.strftime('%d.%m.')} - {sunday.strftime('%d.%m.%Y')})")
    print(f"{'='*90}")
    
    # Hole alle Daten für die Woche
    export_data = get_timewarrior_data_for_period(monday, sunday)
    
    # Organisiere Daten nach Tagen
    daily_data = {}
    total_week_seconds = 0
    
    for day_date in week_dates:
        daily_data[day_date] = {
            'entries': [],
            'total_seconds': 0,
            'projects': {}
        }
    
    # Verarbeite Export-Daten
    for entry in export_data:
        if 'end' not in entry:  # Aktive Einträge überspringen
            continue
            
        start = datetime.fromisoformat(entry['start'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(entry['end'].replace('Z', '+00:00'))
        duration = (end - start).total_seconds()
        
        # Zuordnung zum Tag (basierend auf Startzeit)
        entry_date = start.date()
        
        if entry_date in daily_data:
            daily_data[entry_date]['entries'].append(entry)
            daily_data[entry_date]['total_seconds'] += duration
            total_week_seconds += duration
            
            # Projektname aus Tags
            tags = entry.get('tags', [])
            project = tags[0] if tags else 'Ohne Projekt'
            
            if project not in daily_data[entry_date]['projects']:
                daily_data[entry_date]['projects'][project] = 0
            daily_data[entry_date]['projects'][project] += duration
    
    # Tägliche Übersicht
    print("📅 TÄGLICHE ÜBERSICHT:")
    print(f"{'-'*90}")
    print(f"{'Tag':<12} {'Datum':<12} {'Arbeitszeit':<12} {'Status':<15} {'Hauptprojekte'}")
    print(f"{'-'*90}")
    
    weekdays_de = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
    
    for i, day_date in enumerate(week_dates):
        weekday_de = weekdays_de[i]
        date_str = day_date.strftime('%d.%m.%Y')
        
        # Prüfe Feiertag/Urlaub
        holiday_name = is_holiday(day_date)
        vacation = is_vacation(day_date)
        
        total_seconds = daily_data[day_date]['total_seconds']
        time_str = format_duration(total_seconds)
        
        if holiday_name:
            status = f"🎉 {holiday_name[:10]}..."
            projects_str = ""
        elif vacation:
            status = f"🏖️ {vacation['type']}"
            projects_str = ""
        elif total_seconds == 0:
            status = "📭 Keine Daten"
            projects_str = ""
        else:
            hours = total_seconds / 3600
            if hours >= 8:
                status = "✅ Vollzeit"
            elif hours >= 6:
                status = "⚠️ Teilzeit"
            else:
                status = "🔸 Kurz"
            
            # Top 2 Projekte
            top_projects = sorted(daily_data[day_date]['projects'].items(), 
                                key=lambda x: x[1], reverse=True)[:2]
            projects_str = ", ".join([p[0][:15] for p in top_projects])
        
        print(f"{weekday_de:<12} {date_str:<12} {time_str:<12} {status:<15} {projects_str}")
    
    print(f"{'-'*90}")
    
    # Wochensumme
    total_hours = total_week_seconds / 3600
    average_per_day = total_hours / 5  # Arbeitstage
    
    print(f"\n📊 WOCHENSUMME:")
    print(f"⏰ Gesamtarbeitszeit: {format_duration(total_week_seconds)} ({total_hours:.1f}h)")
    print(f"📊 Durchschnitt/Tag: {format_duration(total_week_seconds/5)} ({average_per_day:.1f}h)")
    
    # Bewertung
    if total_hours >= 40:
        print(f"✅ Vollzeit-Woche erreicht")
    elif total_hours >= 30:
        print(f"⚠️  Teilzeit-Woche")
    elif total_hours > 0:
        print(f"🔸 Kurze Arbeitswoche")
    else:
        print(f"❌ Keine Arbeitszeit erfasst")
    
    if total_hours >= 50:
        print(f"⚠️  Viele Überstunden! ({total_hours:.1f}h)")
    
    # Projekt-Übersicht für die Woche
    print(f"\n📋 PROJEKT-ÜBERSICHT:")
    print(f"{'-'*90}")
    
    week_projects = {}
    for day_date, day_data in daily_data.items():
        for project, duration in day_data['projects'].items():
            if project not in week_projects:
                week_projects[project] = 0
            week_projects[project] += duration
    
    if week_projects:
        print(f"{'Projekt':<30} {'Zeit':<12} {'Anteil':<10} {'Ø/Tag'}")
        print(f"{'-'*90}")
        
        for project, duration in sorted(week_projects.items(), key=lambda x: x[1], reverse=True):
            duration_str = format_duration(duration)
            percentage = (duration / total_week_seconds * 100) if total_week_seconds > 0 else 0
            avg_per_day = format_duration(duration / 5)  # 5 Arbeitstage
            
            print(f"{project:<30} {duration_str:<12} {percentage:6.1f}%   {avg_per_day}")
    else:
        print("Keine Projektdaten verfügbar")
    
    print(f"{'='*90}\n")

def main():
    parser = argparse.ArgumentParser(description='Timewarrior Weekly Report')
    parser.add_argument('date', nargs='?', help='Datum (YYYY-MM-DD), Standard: diese Woche')
    parser.add_argument('--last-week', action='store_true', help='Letzte Woche anzeigen')
    parser.add_argument('--weeks', type=int, default=1, help='Anzahl vergangener Wochen (Standard: 1)')
    
    args = parser.parse_args()
    
    if args.weeks > 1:
        # Zeige mehrere Wochen
        today = date.today()
        for i in range(args.weeks - 1, -1, -1):
            target_date = today - timedelta(weeks=i)
            generate_weekly_report(target_date)
    elif args.last_week:
        last_week = date.today() - timedelta(weeks=1)
        generate_weekly_report(last_week)
    elif args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
            generate_weekly_report(target_date)
        except ValueError:
            print("❌ Ungültiges Datumsformat. Verwende: YYYY-MM-DD")
    else:
        # Standard: diese Woche
        generate_weekly_report(date.today())

if __name__ == '__main__':
    main()
