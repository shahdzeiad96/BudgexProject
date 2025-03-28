import requests

def get_exchange_rate(base_currency, target_currency):
    api_key = 'd9958a13dcc722efda342413'  # Replace with your actual API key
    url = f'https://api.exchangerate-api.com/v4/latest/USD'
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        rates = data['rates']
        
        # Get the exchange rate for the target currency
        exchange_rate = rates.get(target_currency)
        if exchange_rate:
            return exchange_rate
        else:
            return f"Exchange rate for {target_currency} not found."
    else:
        return "Error: Unable to fetch data from the API."