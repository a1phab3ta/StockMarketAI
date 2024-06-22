from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import sqlite3


app = Flask(__name__)

def get_stock_tickers():
    with open('./data/stockData.csv') as data:
        data_ = data.readlines()
        
        tickers = []
        for line in data_[1:]:
            tickers.append(line.strip().split(',')[0])
        data.close()
    return tickers

def get_stock_info(ticker):
    with open('./data/stockData.csv') as file:
        data = file.readlines()
        data = data[1:]
        data = [line.strip().split(',') for line in data]
        file.close()
    for i in data:
        if i[0] == ticker:
            return i

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
    data = [list(i) for i in data]
    for i in range(len(data)):
        value = get_stock_price(data[i][0])
        data[i].append(float(value)*float(data[i][1]))
    tot_val = 0
    for i in data:
        tot_val+=i[2]
    return render_template('current_portfolio.html', data = data, tot_val=tot_val)

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

@app.route('/stock_info/<string:ticker>')
def stock_info(ticker):
    ticker = ticker.upper()
    info = get_stock_info(ticker)
    print(info)
    return render_template('stock_info.html', ticker=ticker, info=info)


if __name__ == '__main__':
    con = sqlite3.connect('myportfolio.db') 
    cur=con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS portfolio 
                (ticker text NOT NULL,
                 shares text NOT NULL)""")
    print("Successfully connected to database!")
    app.run(debug=True)
