"""Rotte: parte pubblica (sola lettura) e area amministratore."""
import calendar
import time as tempo
from datetime import date, time, timedelta
from functools import wraps

from flask import (Blueprint, current_app, abort, flash, redirect, render_template,
                   request, session, url_for)

from models import CATEGORIE, Admin, Appointment, db

bp = Blueprint("main", __name__)

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]
GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
GIORNI_BREVI = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]


@bp.app_template_filter("data_it")
def data_it(d):
    """15 maggio 2025 -> 'Giovedì 15 Maggio 2025'."""
    return f"{GIORNI[d.weekday()].capitalize()} {d.day} {MESI[d.month - 1].capitalize()} {d.year}"


@bp.app_template_filter("ora")
def ora(t):
    return t.strftime("%H:%M")


@bp.app_context_processor
def contesto():
    return {"is_admin": bool(session.get("admin_id")), "CATEGORIE": CATEGORIE}


def admin_required(f):
    """Protezione LATO SERVER delle rotte di modifica."""
    @wraps(f)
    def wrapper(*a, **k):
        if not session.get("admin_id"):
            flash("Per fare questa operazione devi accedere come amministratore.", "errore")
            return redirect(url_for("main.login"))
        return f(*a, **k)
    return wrapper


# ---------------------------------------------------------------- Parte pubblica
@bp.route("/")
def index():
    oggi = date.today()
    try:
        anno = int(request.args.get("anno", oggi.year))
        mese = int(request.args.get("mese", oggi.month))
        if not 1900 <= anno <= 2100:
            raise ValueError
        date(anno, mese, 1)
    except ValueError:
        anno, mese = oggi.year, oggi.month

    settimane = calendar.Calendar(firstweekday=0).monthdatescalendar(anno, mese)
    primo, ultimo = settimane[0][0], settimane[-1][-1]
    appuntamenti = (Appointment.query.filter(Appointment.data.between(primo, ultimo))
                    .order_by(Appointment.data, Appointment.ora_inizio).all())
    per_giorno = {}
    for a in appuntamenti:
        per_giorno.setdefault(a.data, []).append(a)

    prec = (anno, mese - 1) if mese > 1 else (anno - 1, 12)
    succ = (anno, mese + 1) if mese < 12 else (anno + 1, 1)

    prossimi = (Appointment.query.filter(Appointment.data >= oggi)
                .order_by(Appointment.data, Appointment.ora_inizio).limit(15).all())
    gruppi = []
    for a in prossimi:
        if not gruppi or gruppi[-1][0] != a.data:
            gruppi.append((a.data, []))
        gruppi[-1][1].append(a)

    return render_template("index.html", anno=anno, mese=mese, nome_mese=MESI[mese - 1].capitalize(),
                           settimane=settimane, per_giorno=per_giorno, oggi=oggi, prec=prec, succ=succ,
                           gruppi=gruppi, giorni=GIORNI, giorni_brevi=GIORNI_BREVI)


@bp.route("/giorno/<iso>")
def giorno(iso):
    try:
        g = date.fromisoformat(iso)
    except ValueError:
        abort(404)
    lista = Appointment.query.filter_by(data=g).order_by(Appointment.ora_inizio).all()
    return render_template("giorno.html", g=g, lista=lista,
                           ieri=g - timedelta(days=1), domani=g + timedelta(days=1))


@bp.route("/appuntamento/<int:id>")
def dettaglio(id):
    return render_template("dettaglio.html", a=db.get_or_404(Appointment, id))


@bp.route("/manifest.webmanifest")
def manifest():
    """Permette di installare il sito come app sulla schermata Home di Android."""
    r = current_app.send_static_file("manifest.webmanifest")
    r.mimetype = "application/manifest+json"
    return r


# ---------------------------------------------------------------- Accesso
@bp.route("/admin", methods=["GET", "POST"])
def login():
    if Admin.query.count() == 0:
        return primo_amministratore()
    if session.get("admin_id"):
        return redirect(url_for("main.index"))
    if request.method == "POST":
        utente = Admin.query.filter_by(username=request.form.get("username", "").strip()).first()
        if utente and utente.controlla_password(request.form.get("password", "")):
            session.clear()
            session.permanent = True
            session["admin_id"] = utente.id
            flash("Accesso eseguito.", "ok")
            return redirect(url_for("main.index"))
        tempo.sleep(1)  # rallenta eventuali tentativi ripetuti
        flash("Nome utente o password non corretti. Riprova.", "errore")
    return render_template("login.html")


def primo_amministratore():
    """Se non esiste ancora nessun amministratore, permette di crearlo dal browser (utile sull'app Android)."""
    if request.method == "POST":
        nome = request.form.get("username", "").strip()
        pw = request.form.get("password", "")
        if not nome:
            flash("Scrivi un nome utente.", "errore")
        elif len(pw) < 8:
            flash("La password deve avere almeno 8 caratteri.", "errore")
        elif pw != request.form.get("password2", ""):
            flash("Le due password non coincidono.", "errore")
        else:
            a = Admin(username=nome)
            a.imposta_password(pw)
            db.session.add(a)
            db.session.commit()
            flash("Amministratore creato. Ora puoi accedere.", "ok")
            return redirect(url_for("main.login"))
    return render_template("setup.html")


@bp.route("/admin/esci", methods=["POST"])
def logout():
    session.clear()
    flash("Hai effettuato l'uscita.", "ok")
    return redirect(url_for("main.index"))


# ---------------------------------------------------------------- Area amministratore
def leggi_form(f):
    """Valida i campi del form. Restituisce (dati, lista_errori)."""
    errori = []
    titolo = f.get("titolo", "").strip()
    if not titolo:
        errori.append("Scrivi il titolo dell'appuntamento.")
    elif len(titolo) > 120:
        errori.append("Il titolo è troppo lungo (massimo 120 caratteri).")
    try:
        data = date.fromisoformat(f.get("data", ""))
    except ValueError:
        data = None
        errori.append("La data non è valida.")
    try:
        inizio = time.fromisoformat(f.get("ora_inizio", ""))
    except ValueError:
        inizio = None
        errori.append("Indica l'ora di inizio (esempio: 16:30).")
    fine = None
    if f.get("ora_fine", "").strip():
        try:
            fine = time.fromisoformat(f["ora_fine"])
        except ValueError:
            errori.append("L'ora di fine non è valida.")
    if inizio and fine and fine <= inizio:
        errori.append("L'ora di fine deve essere dopo l'ora di inizio.")
    cat = f.get("categoria", "generale")
    dati = dict(titolo=titolo, data=data, ora_inizio=inizio, ora_fine=fine,
                luogo=f.get("luogo", "").strip()[:160] or None,
                note=f.get("note", "").strip() or None,
                categoria=cat if cat in CATEGORIE else "generale")
    return dati, errori


def valori_iniziali(a=None, data=None):
    if a:
        return dict(titolo=a.titolo, data=a.data.isoformat(), ora_inizio=ora(a.ora_inizio),
                    ora_fine=ora(a.ora_fine) if a.ora_fine else "", luogo=a.luogo or "",
                    note=a.note or "", categoria=a.categoria)
    return dict(titolo="", data=data or date.today().isoformat(), ora_inizio="", ora_fine="",
                luogo="", note="", categoria="generale")


def gestisci_form(a, titolo_pagina):
    if request.method == "POST":
        dati, errori = leggi_form(request.form)
        if errori:
            for e in errori:
                flash(e, "errore")
            v = {**valori_iniziali(a), **request.form.to_dict()}
            return render_template("form.html", v=v, titolo_pagina=titolo_pagina)
        if a is None:
            a = Appointment()
            db.session.add(a)
        for k, val in dati.items():
            setattr(a, k, val)
        db.session.commit()
        flash("Appuntamento salvato.", "ok")
        return redirect(url_for("main.dettaglio", id=a.id))
    return render_template("form.html", v=valori_iniziali(a, request.args.get("data")),
                           titolo_pagina=titolo_pagina)


@bp.route("/admin/nuovo", methods=["GET", "POST"])
@admin_required
def nuovo():
    return gestisci_form(None, "Nuovo appuntamento")


@bp.route("/admin/<int:id>/modifica", methods=["GET", "POST"])
@admin_required
def modifica(id):
    return gestisci_form(db.get_or_404(Appointment, id), "Modifica appuntamento")


@bp.route("/admin/<int:id>/elimina", methods=["GET", "POST"])
@admin_required
def elimina(id):
    a = db.get_or_404(Appointment, id)
    if request.method == "POST":
        db.session.delete(a)
        db.session.commit()
        flash("Appuntamento eliminato.", "ok")
        return redirect(url_for("main.index", anno=a.data.year, mese=a.data.month))
    return render_template("conferma.html", a=a)
