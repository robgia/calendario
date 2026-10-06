"""Crea o aggiorna un amministratore: python crea_admin.py"""
from getpass import getpass

from app import app
from models import Admin, db

utente = input("Nome utente amministratore: ").strip()
password = getpass("Password (almeno 8 caratteri): ")
if not utente or len(password) < 8:
    raise SystemExit("Nome utente mancante o password troppo corta.")
if password != getpass("Ripeti la password: "):
    raise SystemExit("Le password non coincidono.")
with app.app_context():
    a = Admin.query.filter_by(username=utente).first() or Admin(username=utente)
    a.imposta_password(password)
    db.session.add(a)
    db.session.commit()
print("Amministratore salvato.")
