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
  res = requests.post(url, json=payload)
  print(f'Respuesta Telegram: {res.status_code} - {res.text}')


def escanear_mercado_en_vivo():
  try:
    print('Iniciando rastreo de mercado...')

    # 1. Obtenemos directamente la lista de acciones más activas en volumen del mercado
    screening = yf.screen('most_actives', count=100)
    quotes = screening.get('quotes', [])

    if not quotes:
      return '⚠️ No se obtuvieron datos del mercado en este momento.'

    resultados = []
    for q in quotes:
      symbol = q.get('symbol', '')
      precio = q.get('regularMarketPrice', 0.0)
      volumen = q.get('regularMarketVolume', 0)
      cambio = q.get('regularMarketChangePercent', 0.0)

      # FILTRO: Acciones de menos o igual a $5 y con más de 500k de volumen
      if 0 < precio <= 5.0 and volumen >= 500000:
        resultados.append({
            'ticker': symbol,
            'precio': precio,
            'volumen': volumen,
            'cambio': cambio,
        })

    if not resultados:
      return '⚠️ No hay acciones por debajo de $5 entre las más activas con volumen > 500k.'

    # Ordenamos por mayor volumen de negociación
    resultados_ordenados = sorted(
        resultados, key=lambda x: x['volumen'], reverse=True
    )[:3]

    mensaje = '🔥 *TOP 3 SCALPING EN VIVO (< $5)* 🔥\n'
    mensaje += '📌 *Filtro:* Precio ≤ $5 | Vol > 500k\n\n'

    for i, item in enumerate(resultados_ordenados, 1):
      signo = '+' if item['cambio'] > 0 else ''
      mensaje += (
          f"*{i}. {item['ticker']}* ➔ `${item['precio']:.2f}`\n"
          f"   📊 Vol: `{item['volumen']:,.0f}` | 🚀 Var:"
          f" `{signo}{item['cambio']:.2f}%`\n\n"
      )

    mensaje += '💡 *Acciones con mayor liquidez rastreadas en vivo.*'
    return mensaje

  except Exception as e:
    return f'❌ Error al rastrear el mercado: {str(e)}'


if __name__ == '__main__':
  reporte = escanear_mercado_en_vivo()
  print('Enviando reporte...')
  enviar_alerta(reporte)
