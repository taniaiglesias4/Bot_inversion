import os
import requests
import yfinance as yf
from yfinance import EquityQuery

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


def escanear_mercado_en_vivo():
  try:
    # Rastreador dinámico sin listas:
    # 1. Región EE.UU.
    # 2. Precio actual <= $5
    # 3. Volumen del día >= 500,000 acciones
    q = EquityQuery('and', [
        EquityQuery('eq', ['region', 'us']),
        EquityQuery('lte', ['intradayprice', 5.0]),
        EquityQuery('gte', ['dayvolume', 500000]),
    ])

    # Ejecutamos la búsqueda dinámica en vivo
    response = yf.screen(q, sort_field='dayvolume', sort_type='desc', size=10)
    quotes = response.get('quotes', [])

    if not quotes:
      return '⚠️ No se encontraron acciones por debajo de $5 con más de 500k de volumen en este momento.'

    resultados = []
    for q_data in quotes[:3]:  # Cogemos las Top 3 con mayor volumen
      symbol = q_data.get('symbol')
      precio = q_data.get('regularMarketPrice', 0)
      volumen = q_data.get('regularMarketVolume', 0)
      cambio = q_data.get('regularMarketChangePercent', 0)

      resultados.append({
          'ticker': symbol,
          'precio': precio,
          'volumen': volumen,
          'cambio': cambio,
      })

    mensaje = '🔥 *TOP 3 SCALPING EN VIVO (MERCADO REAL)* 🔥\n'
    mensaje += '📌 *Filtros:* Precio < $5 | Volumen > 500k\n\n'

    for i, item in enumerate(resultados, 1):
      signo = '+' if item['cambio'] > 0 else ''
      mensaje += (
          f"*{i}. {item['ticker']}* ➔ `${item['precio']:.2f}`\n"
          f"   📊 Vol: `{item['volumen']:,.0f}` | 🚀 Var:"
          f" `{signo}{item['cambio']:.2f}%`\n\n"
      )

    mensaje += '💡 *Escaneo directo del mercado sin lista predefinida.*'
    return mensaje

  except Exception as e:
    return f'❌ Error rastreando el mercado: {str(e)}'


if __name__ == '__main__':
  reporte = escanear_mercado_en_vivo()
  enviar_alerta(reporte)
