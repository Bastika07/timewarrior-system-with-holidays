#!/usr/bin/env python3
"""
Timewarrior Monthly Report
Monatlicher Bericht mit Feiertags-, Urlaubs- und Projektanalyse
"""

import subprocess
import json
import os
from datetime import datetime, date, timedelta
import calendar
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

def get_month_dates(year, month):
    """Hole alle Daten des Monats"""
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    
    month_dates = []
    current_date = first_day
    while current_date <= last_day:
        month_dates.append(current_date)
        current_date += timedelta(days=1)
    
    return month_dates

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

def generate_monthly_report(year, month):
    """Generiere monatlichen Bericht"""
    
    month_dates = get_month_dates(year, month)
    first_day = month_dates[0]
    last_day = month_dates[-1]
    
    month_name = calendar.month_name[month]
    months_de = ['', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    month_name_de = months_de[month]
    
    print(f"\n{'='*100}")
    print(f"MONATSBERICHT: {month_name_de} {year}")
    print(f"{'='*100}")
    
    # Hole alle Daten für den Monat
    export_data = get_timewarrior_data_for_period(first_day, last_day)
    
    # Organisiere Daten nach Tagen und Wochen
    daily_data = {}
    weekly_data = {}
    total_month_seconds = 0
    working_days = 0
    holiday_days = 0
    vacation_days = 0
    
    for day_date in month_dates:
        daily_data[day_date] = {
            'entries': [],
            'total_seconds': 0,
            'projects': {},
            'is_holiday': False,
            'is_vacation': False,
            'is_weekend': day_date.weekday() >= 5
        }
        
        # Prüfe Feiertag/Urlaub
        if is_holiday(day_date):
            daily_data[day_date]['is_holiday'] = True
            holiday_days += 1
        elif is_vacation(day_date):
            daily_data[day_date]['is_vacation'] = True
            vacation_days += 1
        elif not daily_data[day_date]['is_weekend']:
            working_days += 1
    
    # Verarbeite Export-Daten
    month_projects = {}
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
            total_month_seconds += duration
            
            # Projektname aus Tags
            tags = entry.get('tags', [])
            project = tags[0] if tags else 'Ohne Projekt'
            
            if project not in daily_data[entry_date]['projects']:
                daily_data[entry_date]['projects'][project] = 0
            daily_data[entry_date]['projects'][project] += duration
            
            # Monatsprojekte
            if project not in month_projects:
                month_projects[project] = 0
            month_projects[project] += duration
    
    # Monatsübersicht
    total_hours = total_month_seconds / 3600
    avg_per_working_day = total_hours / working_days if working_days > 0 else 0
    
    print(f"📊 MONATSÜBERSICHT:")
    print(f"{'-'*100}")
    print(f"Kalendertage:        {len(month_dates):2d} Tage")
    print(f"Arbeitstage:         {working_days:2d} Tage")
    print(f"Feiertage:           {holiday_days:2d} Tage")
    print(f"Urlaubstage:         {vacation_days:2d} Tage")
    print(f"Wochenenden:         {len(month_dates) - working_days - holiday_days - vacation_days:2d} Tage")
    print(f"")
    print(f"Gesamtarbeitszeit:   {format_duration(total_month_seconds)} ({total_hours:.1f}h)")
    print(f"Durchschnitt/Tag:    {format_duration(total_month_seconds/working_days if working_days > 0 else 0)} ({avg_per_working_day:.1f}h)")
    print(f"Sollzeit (8h/Tag):   {format_duration(working_days * 8 * 3600)} ({working_days * 8:.1f}h)")
    
    # Bewertung
    should_hours = working_days * 8
    diff_hours = total_hours - should_hours
    
    if diff_hours > 0:
        print(f"Überstunden:         +{format_duration(abs(diff_hours) * 3600)} (+{diff_hours:.1f}h)")
    elif diff_hours < 0:
        print(f"Fehlstunden:         -{format_duration(abs(diff_hours) * 3600)} (-{abs(diff_hours):.1f}h)")
    else:
        print(f"Stundengenau!        ±0:00 (0.0h)")
    
    print(f"{'-'*100}")
    
    # Wöchentliche Aufschlüsselung
    print(f"\n📅 WÖCHENTLICHE AUFSCHLÜSSELUNG:")
    print(f"{'-'*100}")
    print(f"{'KW':<4} {'Zeitraum':<20} {'Arbeitszeit':<12} {'Sollzeit':<10} {'Diff':<8} {'Status'}")
    print(f"{'-'*100}")
    
    # Gruppiere nach Kalenderwochen
    weeks = {}
    for day_date in month_dates:
        year_week, week_num, _ = day_date.isocalendar()
        week_key = f"{year_week}-{week_num:02d}"
        
        if week_key not in weeks:
            weeks[week_key] = {
                'dates': [],
                'total_seconds': 0,
                'working_days': 0
            }
        
        weeks[week_key]['dates'].append(day_date)
        weeks[week_key]['total_seconds'] += daily_data[day_date]['total_seconds']
        
        if not daily_data[day_date]['is_holiday'] and not daily_data[day_date]['is_vacation'] and not daily_data[day_date]['is_weekend']:
            weeks[week_key]['working_days'] += 1
    
    for week_key in sorted(weeks.keys()):
        week_data = weeks[week_key]
        week_dates = sorted(week_data['dates'])
        start_date = week_dates[0]
        end_date = week_dates[-1]
        
        week_num = int(week_key.split('-')[1])
        date_range = f"{start_date.strftime('%d.%m.')} - {end_date.strftime('%d.%m.')}"
        
        actual_time = format_duration(week_data['total_seconds'])
        should_time = format_duration(week_data['working_days'] * 8 * 3600)
        
        actual_hours = week_data['total_seconds'] / 3600
        should_hours = week_data['working_days'] * 8
        diff_hours = actual_hours - should_hours
        
        if diff_hours > 0:
            diff_str = f"+{diff_hours:.1f}h"
            status = "✅ Über"
        elif diff_hours < 0:
            diff_str = f"{diff_hours:.1f}h"
            status = "❌ Unter"
        else:
            diff_str = "±0.0h"
            status = "✅ Genau"
        
        print(f"{week_num:<4} {date_range:<20} {actual_time:<12} {should_time:<10} {diff_str:<8} {status}")
    
    print(f"{'-'*100}")
    
    # Top Projekte des Monats
    print(f"\n📋 PROJEKT-ANALYSE:")
    print(f"{'-'*100}")
    
    if month_projects:
        print(f"{'Projekt':<30} {'Zeit':<12} {'Anteil':<8} {'Ø/Tag':<8} {'Tage'}")
        print(f"{'-'*100}")
        
        for project, duration in sorted(month_projects.items(), key=lambda x: x[1], reverse=True):
            duration_str = format_duration(duration)
            percentage = (duration / total_month_seconds * 100) if total_month_seconds > 0 else 0
            
            # Berechne an wie vielen Tagen gearbeitet wurde
            project_days = 0
            for day_date, day_data in daily_data.items():
                if project in day_data['projects'] and day_data['projects'][project] > 0:
                    project_days += 1
            
            avg_per_day = format_duration(duration / project_days) if project_days > 0 else "0:00"
            
            print(f"{project:<30} {duration_str:<12} {percentage:6.1f}% {avg_per_day:<8} {project_days:2d}")
    else:
        print("Keine Projektdaten verfügbar")
    
    print(f"{'-'*100}")
    
    # Feiertage und Urlaub
    special_days = []
    for day_date in month_dates:
        if daily_data[day_date]['is_holiday']:
            holiday_name = is_holiday(day_date)
            special_days.append(f"🎉 {day_date.strftime('%d.%m.')}: {holiday_name}")
        elif daily_data[day_date]['is_vacation']:
            vacation = is_vacation(day_date)
            special_days.append(f"🏖️ {day_date.strftime('%d.%m.')}: {vacation['name']} ({vacation['type']})")
    
    if special_days:
        print(f"\n🗓️ FEIERTAGE & URLAUB:")
        print(f"{'-'*100}")
        for special_day in special_days:
            print(special_day)
        print(f"{'-'*100}")
    
    # Produktivitäts-Metriken
    print(f"\n📈 PRODUKTIVITÄTS-METRIKEN:")
    print(f"{'-'*100}")
    
    productive_days = sum(1 for day_data in daily_data.values() 
                         if day_data['total_seconds'] > 0 and not day_data['is_weekend'] 
                         and not day_data['is_holiday'] and not day_data['is_vacation'])
    
    productivity_rate = (productive_days / working_days * 100) if working_days > 0 else 0
    
    # Finde den produktivsten Tag
    best_day = None
    best_duration = 0
    for day_date, day_data in daily_data.items():
        if day_data['total_seconds'] > best_duration:
            best_duration = day_data['total_seconds']
            best_day = day_date
    
    print(f"Produktive Tage:     {productive_days}/{working_days} ({productivity_rate:.1f}%)")
    if best_day:
        print(f"Produktivster Tag:   {best_day.strftime('%d.%m.%Y')} ({format_duration(best_duration)})")
    
    consistency = "Hoch" if productivity_rate >= 90 else "Mittel" if productivity_rate >= 70 else "Niedrig"
    print(f"Konsistenz:          {consistency}")
    
    print(f"{'='*100}\n")

def main():
    parser = argparse.ArgumentParser(description='Timewarrior Monthly Report')
    parser.add_argument('--year', type=int, help='Jahr (Standard: aktuelles Jahr)')
    parser.add_argument('--month', type=int, help='Monat (1-12, Standard: aktueller Monat)')
    parser.add_argument('--last-month', action='store_true', help='Letzten Monat anzeigen')
    parser.add_argument('--months', type=int, default=1, help='Anzahl vergangener Monate (Standard: 1)')
    
    args = parser.parse_args()
    
    today = date.today()
    
    if args.last_month:
        # Letzter Monat
        if today.month == 1:
            target_year = today.year - 1
            target_month = 12
        else:
            target_year = today.year
            target_month = today.month - 1
        generate_monthly_report(target_year, target_month)
    elif args.months > 1:
        # Mehrere Monate
        for i in range(args.months - 1, -1, -1):
            if today.month - i <= 0:
                target_year = today.year - 1
                target_month = 12 + (today.month - i)
            else:
                target_year = today.year
                target_month = today.month - i
            generate_monthly_report(target_year, target_month)
    elif args.year and args.month:
        # Spezifisches Jahr/Monat
        generate_monthly_report(args.year, args.month)
    else:
        # Standard: aktueller Monat (oder letzter wenn noch früh im Monat)
        target_year = args.year or today.year
        target_month = args.month or today.month
        generate_monthly_report(target_year, target_month)

if __name__ == '__main__':
    main()
