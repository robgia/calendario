# Calendario appuntamenti

Calendario in sola lettura per tutti; solo l'amministratore può inserire, modificare ed eliminare appuntamenti.
Testo grande, alto contrasto, pulsanti ampi, tutto in italiano.

## Installazione
    python -m venv venv
    source venv/bin/activate        # Windows: venv\Scripts\activate
    pip install -r requirements.txt

## Creare l'amministratore (una delle due vie)
- `python crea_admin.py` (chiede nome utente e password)
- oppure variabili d'ambiente al primo avvio: `ADMIN_USER` e `ADMIN_PASSWORD`

## Avvio
    python app.py
Apri http://127.0.0.1:5000 — l'area amministratore è su `/admin`.

## Opzioni (variabili d'ambiente)
- `HOST=0.0.0.0` e `PORT=5000`: rende l'app visibile nella rete locale (es. da un NAS o PC di casa)
- `SECRET_KEY`: chiave delle sessioni (se assente viene generata in `instance/secret.key`)
- `HTTPS=1`: se l'app è servita via https (cookie sicuri)
- `NO_ESEMPI=1`: non inserisce gli appuntamenti di esempio

Per un uso in rete stabile conviene un server di produzione (es. `pip install waitress` e `waitress-serve --port=5000 app:app`).
I dati sono in `instance/calendario.db`: copia quel file per fare il backup.

## Uso su smartphone Android
**Consigliato (dati condivisi):** avvia l'app su un PC o NAS sempre acceso (`HOST=0.0.0.0`), poi dal telefono
apri `http://INDIRIZZO-DEL-PC:5000` in Chrome e scegli menu ⋮ → "Aggiungi a schermata Home" / "Installa app":
compare un'icona "Calendario" che si apre a schermo intero come un'app.

**Tutto sul telefono:** installa Termux da F-Droid, copia questa cartella sul telefono ed esegui `sh avvia_termux.sh`.
Attenzione: così i dati restano solo su quel telefono.
