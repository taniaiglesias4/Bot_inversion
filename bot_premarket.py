import os
import pandas as pd
import requests
import yfinance as yf

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')


def enviar_alerta(mensaje):
  if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print('Error: Faltan las claves de Telegram')
    print(mensaje)
    return
  url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
  payload = {
      'chat_id': TELEGRAM_CHAT_ID,
      'text': mensaje,
      'parse_mode': 'Markdown',
  }
  requests.post(url, json=payload)


def obtener_top_premarket_acciones():
  tickers_watchlist = [
      'AAPL',
      'TSLA',
      'NVDA',
      'AMD',
      'AMZN',
      'MSFT',
      'GOOGL',
      'META',
      'NFLX',
      'PLTR',
      'COIN',
      'MARA',
      'INTC',
      'BA',
      'SPY',
      'QQQ',
  ]
  datos_premarket = []

  for ticker in tickers_watchlist:
    try:
      stock = yf.Ticker(ticker)
      hist = stock.history(period='2d', interval='1d')
      if len(hist) < 2:
        continue
      cierre_ayer = hist['Close'].iloc[-2]
      info = stock.fast_info
      precio_actual = getattr(info, 'last_price', None)

      if precio_actual and cierre_ayer:
        gap_percent = ((precio_actual - cierre_ayer) / cierre_ayer) * 100
        datos_premarket.append(
            {'ticker': ticker, 'gap': gap_percent, 'precio': precio_actual}
        )
    except Exception:
      continue

  df = pd.DataFrame(datos_premarket)
  if df.empty:
    return 'No se pudieron obtener datos del premarket hoy.'

  df_top3 = df.sort_values(by='gap', ascending=False).head(3)
  mensaje = '🚨 *TOP 3 ACCIONES PREMARKET (DIARIO)* 🚨\n\n'
  for i, row in enumerate(df_top3.iterrows(), 1):
    data = row[1]
    mensaje += (
        f"{i}. *{data['ticker']}* ➔ Gap: `+{data['gap']:.2f}%` | Precio:"
        f" `${data['precio']:.2f}`\n"
    )
  mensaje += '\n💡 Abre TradingView en tu Honor para analizar tus entradas.'
  return mensaje


if __name__ == '__main__':
  resultado = obtener_top_premarket_acciones()
  enviar_alerta(resultado)
