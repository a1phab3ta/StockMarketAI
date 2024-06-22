from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import sqlite3


app = Flask(__name__)

def get_stock_tickers():
    url = 'https://stockanalysis.com/stocks/'  
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    tickers = []
    for td in soup.find_all('td', class_='svelte-1yyv6eq'):
        a_tag = td.find('a')
        if a_tag:
            tickers.append(a_tag.text.strip())

    return tickers


def get_stock_price(ticker):
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
    con = sqlite3.connect('myportfolio.db') 
    cur=con.cursor()
    tickers = []
    shares = []
    cur.execute("SELECT * FROM portfolio")
    data = cur.fetchall()
    return render_template('current_portfolio.html', data = data)

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
    price = get_stock_price(ticker)
    return render_template('stock_price.html', ticker=ticker, price=price)


if __name__ == '__main__':
    con = sqlite3.connect('myportfolio.db') 
    cur=con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS portfolio 
                (ticker text NOT NULL,
                 shares text NOT NULL)""")
    print("Successfully connected to database!")
    app.run(debug=True)
