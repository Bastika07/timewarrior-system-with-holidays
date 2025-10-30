#!/bin/bash
# Timewarrior Arbeitszeit-Management Setup (Complete Edition)
set -e

echo "🚀 Timewarrior Arbeitszeit-Management Setup (Complete Edition)"
echo "=============================================================="

if ! command -v timew &> /dev/null; then
    echo "❌ Timewarrior ist nicht installiert!"
    echo "Installation:"
    echo "Ubuntu/Debian: sudo apt install timewarrior"
    echo "Arch Linux:    sudo pacman -S timew"
    echo "macOS:         brew install timewarrior"
    exit 1
fi

echo "✅ Timewarrior gefunden"

TIMEW_DIR="$HOME/.timewarrior"
mkdir -p "$TIMEW_DIR/hooks"
mkdir -p "$TIMEW_DIR/data/holidays"
mkdir -p "$TIMEW_DIR/data/vacation"
mkdir -p "$TIMEW_DIR/data/config"

echo "📂 Installiere Hooks..."
cp hooks/on-modify-autopause "$TIMEW_DIR/hooks/"
cp hooks/on-modify-warnings "$TIMEW_DIR/hooks/"
cp hooks/on-modify-holidays "$TIMEW_DIR/hooks/"
chmod +x "$TIMEW_DIR/hooks/"*

echo "⚙️ Installiere Konfiguration..."
cp config/timewarrior.cfg "$TIMEW_DIR/"

echo "📜 Installiere Scripts..."
chmod +x scripts/*.py
mkdir -p "$HOME/.local/bin"
ln -sf "$(pwd)/scripts/daily_report.py" "$HOME/.local/bin/timew-daily"
ln -sf "$(pwd)/scripts/weekly_report.py" "$HOME/.local/bin/timew-weekly"
ln -sf "$(pwd)/scripts/monthly_report.py" "$HOME/.local/bin/timew-monthly"
ln -sf "$(pwd)/scripts/holiday_manager.py" "$HOME/.local/bin/timew-holidays"
ln -sf "$(pwd)/scripts/vacation_manager.py" "$HOME/.local/bin/timew-vacation"

echo "🏖️ Erstelle Feiertags- und Urlaubsdaten..."
python3 scripts/holiday_manager.py --update-holidays 2024

echo ""
echo "🎉 Installation abgeschlossen!"
echo ""
echo "WICHTIG: Konfiguriere dein Bundesland für regionale Feiertage!"
echo "=========================================================="
echo "timew-holidays --set-state [BUNDESLAND]"
echo ""
echo "Verfügbare Bundesländer:"
echo "BW=Baden-Württemberg, BY=Bayern, BE=Berlin, BB=Brandenburg"
echo "HB=Bremen, HH=Hamburg, HE=Hessen, MV=Mecklenburg-Vorpommern"
echo "NI=Niedersachsen, NW=Nordrhein-Westfalen, RP=Rheinland-Pfalz"
echo "SL=Saarland, SN=Sachsen, ST=Sachsen-Anhalt, SH=Schleswig-Holstein, TH=Thüringen"
echo ""
echo "Beispiel: timew-holidays --set-state BY  # für Bayern"
echo ""
echo "ERSTE SCHRITTE:"
echo "==============="
echo "1. timew-holidays --set-state [DEIN_BUNDESLAND]"
echo "2. timew-vacation add 2024-12-24 2024-12-31 'Weihnachtsurlaub'"
echo "3. timew start mein_projekt"
echo "4. timew-daily"
