from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Функция для получения реальных курсов валют
def get_exchange_rates():
    try:
        # Бесплатный API без регистрации
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'rates' in data:
            usd_rates = data['rates']
            rub_rate = usd_rates.get('RUB')
            
            if rub_rate:
                # Поддерживаемые валюты
                currencies = ['RUB', 'USD', 'EUR', 'KZT', 'GBP', 'CNY', 'TRY', 'JPY', 'CHF', 'CAD']
                rates = {}
                for currency in currencies:
                    if currency in usd_rates:
                        # Пересчёт относительно рубля
                        rates[currency] = round(usd_rates[currency] / rub_rate, 6)
                
                print(f"✅ Курсы загружены: {rates}")
                return rates
            else:
                raise Exception("Не найден курс рубля")
        else:
            raise Exception("Нет поля rates в ответе")
            
    except Exception as e:
        print(f"❌ Ошибка получения курсов: {e}")
        # Резервные курсы
        return {
            'RUB': 1,
            'USD': 0.0108,
            'EUR': 0.0099,
            'KZT': 5.15,
            'GBP': 0.0085,
            'CNY': 0.078,
            'TRY': 0.37,
            'JPY': 1.62,
            'CHF': 0.0096,
            'CAD': 0.015
        }

@app.route('/')
def index():
    rates = get_exchange_rates()
    return render_template('currency.html', rates=rates)

@app.route('/convert', methods=['POST'])
def convert():
    current_rates = get_exchange_rates()
    
    amount = float(request.form['amount'])
    from_currency = request.form['from_currency']
    to_currency = request.form['to_currency']
    
    # Конвертация через рубль
    amount_in_rub = amount / current_rates[from_currency]
    result = amount_in_rub * current_rates[to_currency]
    result = round(result, 2)
    
    return render_template('currency.html', 
                         rates=current_rates,
                         result=result,
                         amount=amount,
                         from_cur=from_currency,
                         to_cur=to_currency)

if __name__ == '__main__':
    app.run(debug=True)