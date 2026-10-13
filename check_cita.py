from datetime import datetime, timedelta
import time
import requests
import os

# --- CONFIGURAZIONE TELEGRAM ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- CONFIGURAZIONE CONTROLLO ---
# Intervallo in secondi tra un controllo e l'altro (es. ogni 5 minuti = 300)
CHECK_INTERVAL = 300

# Range date desiderate (Ottobre e primi 15 giorni di novembre 2026)
START_DATE = datetime(2026, 10, 1)
END_DATE = datetime(2026, 11, 18)


def send_telegram_message(message):
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {
      "chat_id": TELEGRAM_CHAT_ID,
      "text": message,
      "parse_mode": "Markdown",
  }
  try:
    response = requests.post(url, json=payload)
    if not response.ok:
      print(f"Errore invio Telegram: {response.text}")
  except Exception as e:
    print(f"Errore di connessione a Telegram: {e}")


def check_appointments():
  current_date = START_DATE
  print(
      f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Inizio controllo"
      " appuntamenti..."
  )

  while current_date <= END_DATE:
    date_str = current_date.strftime("%Y-%m-%d")
    url = f"https://citaprevia.encolate.es/hours/2081/{date_str}"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": (
            "it-IT,it;q=0.9,ca;q=0.8,en-US;q=0.7,en;q=0.6,es;q=0.5"
        ),
        "referrer": "https://citaprevia.encolate.es/laoliva/reservation",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
            " like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    try:
      response = requests.get(url, headers=headers)
      if response.status_code == 200:
        data = response.json()
        hours = data.get("hours", [])

        # Se l'array 'hours' non è vuoto, ci sono appuntamenti disponibili!
        if hours:
          available_times = [h[0] for h in hours]
          msg = (
              f"🚨 **Trovata Cita a La Oliva!**\n📅 Data: **{date_str}**\n⏰"
              f" Orari disponibili: {', '.join(available_times)}\n🔗"
              " [Prenota"
              " ora](https://citaprevia.encolate.es/laoliva/reservation)"
          )
          print(f"Trovato appuntamento per il {date_str}!")
          send_telegram_message(msg)
      else:
        print(
            f"Errore HTTP {response.status_code} per la data {date_str}"
        )
    except Exception as e:
        print(f"Errore durante la richiesta per {date_str}: {e}")

    # Passa al giorno successivo
    current_date += timedelta(days=1)
    # Una piccola pausa per non sovraccaricare il server
    time.sleep(1)


if __name__ == "__main__":
  # Sostituisci i dati prima di avviare
  if (
      TELEGRAM_BOT_TOKEN == "IL_TUO_BOT_TOKEN"
      or TELEGRAM_CHAT_ID == "IL_TUO_CHAT_ID"
  ):
    print("ATTENZIONE: Ricordati di inserire il Token e il Chat ID di Telegram!")
  else:
    while True:
      check_appointments()
      print(f"Attesa di {CHECK_INTERVAL} secondi prima del prossimo controllo...\n")
      time.sleep(CHECK_INTERVAL)
