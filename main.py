from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_stock_tickers():
    url = 'https://stockanalysis.com/stocks/'  # Replace with the actual URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    tickers = []
    for td in soup.find_all('td', class_='svelte-1yyv6eq'):
        a_tag = td.find('a')
        if a_tag:
            tickers.append(a_tag.text.strip())

    return tickers'''

def get_stock_tickers():
    with open("./data/stockData.csv", "r") as file:
        metadata = file.read().splitlines()[1:]
        file.close()
    tickers = []
    for i in metadata:
        i = i.split(",")
        tickers.append(i[0])
    return tickers

def get_stock_prince(ticker):
    if "^" in ticker:
        ticker = ticker.replace("^", "")
    url = f'https://stockanalysis.com/stocks/{ticker}/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        price = soup.find('div', class_='text-4xl font-bold inline-block').text.strip()
    except:
        try:
            price = soup.find('div', class_='text-4xl font-bold block sm:inline').text.strip()
        except:
            price = 'N/A'
    return price

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/refresh_model')
def refresh_model():
    return render_template('refresh_model.html')

@app.route('/current_portfolio')
def current_portfolio():
    return render_template('current_portfolio.html')

@app.route('/top_bearish')
def top_bearish():
    return render_template('top_bearish.html')

@app.route('/top_bullish')
def top_bullish():
    return render_template('top_bullish.html')

@app.route('/stock_tickers')
def stock_tickers():
    tickers = get_stock_tickers()
    return render_template('stock_tickers.html', tickers=tickers)

@app.route('/stock_price/<string:ticker>')
def stock_price(ticker):
    ticker = ticker.upper()
    price = get_stock_prince(ticker)
    return render_template('stock_price.html', ticker=ticker, price=price)
if __name__ == '__main__':
    app.run(debug=True)
