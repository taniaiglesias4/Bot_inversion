import os
import requests
import yfinance as yf

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')


def enviar_alerta(mensaje):
  if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print('⚠️ Faltan credenciales de Telegram.')
    return
  url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
  payload = {
      'chat_id': TELEGRAM_CHAT_ID,
      'text': mensaje,
      'parse_mode': 'Markdown',
  }
  requests.post(url, json=payload)


def escanear_ganadores_dinamicos():
  try:
    # Obtenemos las acciones con mayores ganancias y más activas del día en tiempo real
    gainers = yf.DayGainers()
    actives = yf.MostActive()

    tickers = []
    if not gainers.empty:
      tickers.extend(gainers.index.tolist())
    if not actives.empty:
      tickers.extend(actives.index.tolist())

    tickers_unicos = list(set(tickers))

    if not tickers_unicos:
      return (
          '⚠️ No se pudieron obtener datos de mercado dinámicos en este'
          ' momento.'
      )

    resultados = []
    for symbol in tickers_unicos:
      try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period='1d', interval='5m')
        if hist.empty:
          continue

        precio_actual = hist['Close'].iloc[-1]
        volumen_total = hist['Volume'].sum()
        precio_apertura = hist['Open'].iloc[0]

        # FILTROS DE SCALPING: Menos de $5 y volumen mínimo de 300k
        if 0 < precio_actual <= 5.0 and volumen_total >= 300000:
          cambio_pct = (
              ((precio_actual - precio_apertura) / precio_apertura) * 100
              if precio_apertura > 0
              else 0
          )

          resultados.append({
              'ticker': symbol,
              'precio': precio_actual,
              'volumen': volumen_total,
              'cambio': cambio_pct,
          })
      except Exception:
        continue

    if not resultados:
      return (
          '⚠️ No se encontraron acciones por debajo de $5 con suficiente'
          ' volumen y movimiento hoy.'
      )

    # Ordenar por mayor variación porcentual de la sesión
    resultados_ordenados = sorted(
        resultados, key=lambda x: x['cambio'], reverse=True
    )[:3]

    mensaje = '🚀 *TOP 3 SCALPING DINÁMICO (< $5)* 🚀\n'
    mensaje += '📌 *Filtro:* Precio ≤ $5 | Alta Actividad\n\n'

    for i, item in enumerate(resultados_ordenados, 1):
      signo = '+' if item['cambio'] > 0 else ''
      mensaje += (
          f"*{i}. {item['ticker']}* ➔ `${item['precio']:.2f}`\n"
          f"   🚀 Var: `{signo}{item['cambio']:.2f}%` | 📊 Vol:"
          f" `{item['volumen']:,.0f}`\n\n"
      )

    mensaje += '💡 *Escaneado automáticamente en directo desde el mercado.*'
    return mensaje

  except Exception as e:
    return f'❌ Error en el escáner dinámico: {str(e)}'


if __name__ == '__main__':
  reporte = escanear_ganadores_dinamicos()
  enviar_alerta(reporte)
