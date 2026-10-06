# Come ottenere il file APK (gratis, da browser)

1. Crea un account gratuito su https://github.com e premi "New repository" (nome: calendario, tipo Private va bene).
2. Carica **tutto il contenuto di questa cartella** ("Add file" → "Upload files"), poi "Commit changes".
   Se la cartella nascosta `.github` non risulta caricata: "Add file" → "Create new file", scrivi come nome
   `.github/workflows/apk.yml` e incolla il contenuto di `apk.yml.txt`.
3. Apri la scheda **Actions** → "Crea APK" → "Run workflow". La prima compilazione dura 20-40 minuti.
4. A fine lavoro, nella pagina dell'esecuzione, sezione **Artifacts**, scarica `calendario-apk` (è uno zip con dentro il file .apk).
5. Copia l'.apk sul telefono, aprilo e consenti "Installa app sconosciute" quando richiesto.

## Al primo avvio dell'app
Si apre la pagina "Primo avvio": scegli nome utente e password dell'amministratore. Poi l'app funziona da sola, senza internet.
I dati restano sul telefono (non sono condivisi con altri telefoni).

## Se la compilazione dà errore
Apri il log del passaggio fallito e incollalo a Claude: di solito basta correggere una riga di `buildozer.spec`.
