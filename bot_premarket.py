import os
import pandas as pd
import requests
import yfinance as yf

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')


def enviar_alerta(mensaje):
  if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print(mensaje)
    return
  url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
  payload = {
      'chat_id': TELEGRAM_CHAT_ID,
      'text': mensaje,
      'parse_mode': 'Markdown',
  }
  requests.post(url, json=payload)


def obtener_top_scalping_baratas():
  # Lista ampliada de acciones populares de bajo precio (< 5$) con alta volatilidad para scalping
  watchlist_baratas = [
      'NIO',
      'SIRI',
      'PLUG',
      'SOFI',
      'F',
      'PTON',
      'INTC',
      'SNAP',
      'NOK',
      'AMC',
      'GME',
      'MULN',
      'VERV',
      'OPEN',
      'TAL',
      'BITF',
  ]
  datos_mercado = []

  for ticker in watchlist_baratas:
    try:
      stock = yf.Ticker(ticker)
      hist = stock.history(period='1d', interval='5m')  # Datos intradía
      if hist.empty:
        continue

      precio_actual = hist['Close'].iloc[-1]
      volumen_hoy = hist['Volume'].sum()

      # FILTRO: Solo acciones de menos de 5 dólares
      if precio_actual <= 5.0:
        # Calculamos una variación rápida o volatilidad basada en el rango intradía
        max_sesion = hist['High'].max()
        min_sesion = hist['Low'].min()
        rango_volatilidad = (
            ((max_sesion - min_sesion) / min_sesion) * 100
            if min_sesion > 0
            else 0
        )

        datos_mercado.append({
            'ticker': ticker,
            'precio': precio_actual,
            'volumen': volumen_hoy,
            'volatilidad': rango_volatilidad,
        })
    except Exception:
      continue

  df = pd.DataFrame(datos_mercado)
  if df.empty:
    return (
        '⚠️ No se encontraron acciones por debajo de $5 con suficientes datos'
        ' en este momento.'
    )

  # Ordenar por mayor volumen y volatilidad intradía (ideal para scalping)
  df_top3 = df.sort_values(by='volumen', ascending=False).head(3)

  mensaje = '⚡ *TOP 3 SCALPING (< $5) - MERCADO ABIERTO* ⚡\n\n'
  for i, row in enumerate(df_top3.iterrows(), 1):
    data = row[1]
    mensaje += (
        f"*{i}. {data['ticker']}* ➔ Precio: `${data['precio']:.2f}`\n"
        f"   📊 Vol: `{data['volumen']:,.0f}` | Rango: `+{data['volatilidad']:.2f}%`\n\n"
    )

  mensaje += '💡 *Ideal para buscar patrones de rotura en gráficos de 1m o 5m.*'
  return mensaje


if __name__ == '__main__':
  resultado = obtener_top_scalping_baratas()
  enviar_alerta(resultado)
