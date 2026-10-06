"""Modelli del database: Amministratore e Appuntamento."""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# chiave: (nome, colore scuro, simbolo). Il simbolo e il nome evitano di usare solo il colore.
CATEGORIE = {
    "generale": ("Generale", "#0B3D91", "●"),
    "medico": ("Visita medica", "#8B0000", "✚"),
    "incontro": ("Incontro", "#0B5D1E", "■"),
    "festa": ("Festa o evento", "#6A1B9A", "★"),
}


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def imposta_password(self, password):
        self.password_hash = generate_password_hash(password)

    def controlla_password(self, password):
        return check_password_hash(self.password_hash, password)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(120), nullable=False)
    data = db.Column(db.Date, nullable=False, index=True)
    ora_inizio = db.Column(db.Time, nullable=False)
    ora_fine = db.Column(db.Time)
    luogo = db.Column(db.String(160))
    note = db.Column(db.Text)
    categoria = db.Column(db.String(20), default="generale")

    @property
    def cat_nome(self):
        return CATEGORIE.get(self.categoria, CATEGORIE["generale"])[0]

    @property
    def cat_colore(self):
        return CATEGORIE.get(self.categoria, CATEGORIE["generale"])[1]

    @property
    def cat_simbolo(self):
        return CATEGORIE.get(self.categoria, CATEGORIE["generale"])[2]
