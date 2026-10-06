"""Calendario appuntamenti - avvio: python app.py"""
import os
import secrets
from datetime import date, time, timedelta
from pathlib import Path

from flask import Flask, render_template
from flask_wtf.csrf import CSRFError, CSRFProtect

from models import Admin, Appointment, db
import routes

BASE = Path(__file__).resolve().parent
# Su Android i dati vanno nella cartella privata dell'app; altrove in instance/
DATI = Path(os.environ["ANDROID_PRIVATE"]) / "dati" if os.environ.get("ANDROID_PRIVATE") else BASE / "instance"


def chiave_segreta():
    """Usa SECRET_KEY dall'ambiente, oppure ne genera una e la salva in instance/."""
    if os.environ.get("SECRET_KEY"):
        return os.environ["SECRET_KEY"]
    f = DATI / "secret.key"
    if not f.exists():
        f.write_text(secrets.token_hex(32))
        try:
            f.chmod(0o600)
        except OSError:
            pass
    return f.read_text().strip()


def crea_admin_da_ambiente():
    """Crea il primo amministratore da ADMIN_USER / ADMIN_PASSWORD (nessuna password nel codice)."""
    if Admin.query.count():
        return
    utente, password = os.environ.get("ADMIN_USER"), os.environ.get("ADMIN_PASSWORD")
    if utente and password:
        a = Admin(username=utente)
        a.imposta_password(password)
        db.session.add(a)
        db.session.commit()
        print(f"Amministratore '{utente}' creato.")
    else:
        print("ATTENZIONE: nessun amministratore. Esegui 'python crea_admin.py' "
              "oppure imposta ADMIN_USER e ADMIN_PASSWORD.")


def esempi():
    """Inserisce alcuni appuntamenti di prova se il database è vuoto."""
    if Appointment.query.count() or os.environ.get("NO_ESEMPI"):
        return
    oggi = date.today()
    dati = [
        (1, "Visita dal dottor Rossi", time(9, 30), time(10, 15), "Ambulatorio, via Roma 10", "medico",
         "Portare la tessera sanitaria e gli esami."),
        (3, "Incontro dell'associazione", time(16, 30), time(18, 0), "Sala parrocchiale", "incontro", None),
        (6, "Pranzo di Natale insieme", time(12, 30), None, "Ristorante Il Faro", "festa",
         "Prenotazione al nome dell'associazione."),
        (6, "Tombola pomeridiana", time(16, 0), time(18, 0), "Centro anziani", "festa", None),
        (10, "Controllo della pressione", time(8, 45), None, "Farmacia comunale", "medico", None),
    ]
    for giorni, titolo, ini, fine, luogo, cat, note in dati:
        db.session.add(Appointment(titolo=titolo, data=oggi + timedelta(days=giorni), ora_inizio=ini,
                                   ora_fine=fine, luogo=luogo, categoria=cat, note=note))
    db.session.commit()


def create_app():
    DATI.mkdir(parents=True, exist_ok=True)
    app = Flask(__name__, instance_path=str(DATI))
    app.config.update(
        SECRET_KEY=chiave_segreta(),
        SQLALCHEMY_DATABASE_URI="sqlite:///" + str(DATI / "calendario.db"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("HTTPS") == "1",  # imposta HTTPS=1 se usi https
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    )
    db.init_app(app)
    CSRFProtect(app)
    app.register_blueprint(routes.bp)

    @app.errorhandler(404)
    def non_trovato(e):
        return render_template("errore.html", msg="La pagina che cerchi non esiste."), 404

    @app.errorhandler(CSRFError)
    def csrf_scaduto(e):
        return render_template("errore.html",
                               msg="La pagina è rimasta aperta troppo a lungo. Torna indietro e riprova."), 400

    @app.errorhandler(500)
    def errore_interno(e):
        return render_template("errore.html", msg="Si è verificato un problema. Riprova tra poco."), 500

    with app.app_context():
        db.create_all()
        crea_admin_da_ambiente()
        esempi()
    return app


app = create_app()

if __name__ == "__main__":
    # HOST=0.0.0.0 per renderla visibile nella rete locale
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 5000)))
