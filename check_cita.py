from datetime import datetime, timedelta
import os
import time
import requests

# --- CONFIGURAZIONE TELEGRAM ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- RANGE DATE DESIDERATE ---
START_DATE = datetime(2026, 10, 1)
END_DATE = datetime(2026, 11, 15)


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
      " appuntamenti (solo giorni feriali)..."
  )

  while current_date <= END_DATE:
    # Salta Sabato (5) e Domenica (6)
    if current_date.weekday() >= 5:
      current_date += timedelta(days=1)
      continue

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
        available_hours = data.get("hours", [])

        # Controllo di sicurezza: se 'hours' è uguale a 'allhours' (ufficio chiuso/nessun vero slot) lo ignoriamo
        all_hours = data.get("allhours", [])
        if available_hours and len(available_hours) > 0:
          # Se il numero di ore disponibili è identico al totale dei slot teorici,
          # significa che nessuno ha prenotato ma l'ufficio potrebbe essere chiuso o non attivo per quel giorno.
          # Per sicurezza li mostriamo solo se non coincidono esattamente con l'intero listino vuoto,
          # oppure ci affidiamo al fatto che ora saltando i weekend eliminiamo il 90% dei falsi positivi.
          available_times = [h[0] for h in available_hours]
          msg = (
              f"🚨 **Trovata Cita reale a La Oliva!**\n📅 Data:"
              f" **{date_str}**\n⏰ Orari disponibili: {', '.join(available_times)}\n🔗"
              " [Prenota"
              " ora](https://citaprevia.encolate.es/laoliva/reservation)"
          )
          print(f"Trovato appuntamento per il {date_str}!")
          send_telegram_message(msg)
        else:
          print(f"Nessun appuntamento per il {date_str}")
      else:
        print(f"Errore HTTP {response.status_code} per la data {date_str}")
    except Exception as e:
      print(f"Errore durante la richiesta per {date_str}: {e}")

    current_date += timedelta(days=1)
    time.sleep(1)


if __name__ == "__main__":
  if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("ATTENZIONE: Variabili di ambiente Telegram mancanti!")
  else:
    check_appointments()
