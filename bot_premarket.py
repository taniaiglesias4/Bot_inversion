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


def escanear_mercado_100_dinamico():
  try:
    # Consultamos la API pública de Yahoo Finance en tiempo real para obtener tendencias (SIN LISTAS)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    url = 'https://query1.finance.yahoo.com/v1/finance/trending/us?count=50'

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
      return (
          '⚠️ No se pudo conectar con el servicio de tendencias de mercado.'
      )

    data = response.json()
    finance_results = data.get('finance', {}).get('result', [])
    if not finance_results:
      return '⚠️ No hay datos de mercado disponibles ahora mismo.'

    quotes = finance_results[0].get('quotes', [])
    tickers_dinamicos = [q.get('symbol') for q in quotes if q.get('symbol')]

    if not tickers_dinamicos:
      return '⚠️ No se encontraron activos en tendencia en este momento.'

    resultados = []
    for symbol in tickers_dinamicos:
      try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period='1d', interval='5m')
        if hist.empty:
          continue

        precio_actual = hist['Close'].iloc[-1]
        precio_apertura = hist['Open'].iloc[0]
        volumen_total = hist['Volume'].sum()

        # Filtro estricto para scalping: Menos de $5 y volumen mínimo
        if 0 < precio_actual <= 5.0 and volumen_total >= 200000:
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
      return '⚠️ Ninguna acción en tendencia actual cumple con precio ≤ $5 y volumen requerido.'

    # Ordenar por el mayor porcentaje de cambio positivo
    resultados_ordenados = sorted(
        resultados, key=lambda x: x['cambio'], reverse=True
    )[:3]

    mensaje = '🔥 *TOP 3 SCALPING 100% DINÁMICO (< $5)* 🔥\n'
    mensaje += (
        '📌 *Fuente:* Tendencias en vivo | *Filtro:* Precio ≤ $5 y buen'
        ' volumen\n\n'
    )

    for i, item in enumerate(resultados_ordenados, 1):
      signo = '+' if item['cambio'] > 0 else ''
      mensaje += (
          f"*{i}. {item['ticker']}* ➔ `${item['precio']:.2f}`\n"
          f"   🚀 Var: `{signo}{item['cambio']:.2f}%` | 📊 Vol:"
          f" `{item['volumen']:,.0f}`\n\n"
      )

    mensaje += '💡 *Escaneo puramente dinámico sin listas previas.*'
    return mensaje

  except Exception as e:
    return f'❌ Error en el escáner: {str(e)}'


if __name__ == '__main__':
  reporte = escanear_mercado_100_dinamico()
  enviar_alerta(reporte)
