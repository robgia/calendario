#!/data/data/com.termux/files/usr/bin/sh
# Avvia il calendario direttamente su un telefono Android con Termux (da F-Droid).
cd "$(dirname "$0")"
pkg install -y python >/dev/null 2>&1
pip install -q -r requirements.txt
[ -f instance/calendario.db ] || { echo "Primo avvio: crea l'amministratore"; python crea_admin.py; }
echo "Apri il browser del telefono su http://127.0.0.1:5000"
HOST=0.0.0.0 python app.py
