from flask import Flask, redirect, render_template, request, url_for
import requests
from bs4 import BeautifulSoup
import sqlite3
from pymongo import MongoClient
from marshmallow import Schema, fields, validate

class StockSchema(Schema):
    ticker = fields.Str(required=True, validate=validate.Length(min=1))
    shares = fields.Int(required=True, validate=validate.Range(min=1))

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, validate=validate.Length(min=1))
    portfolio = fields.List(fields.Nested(StockSchema), required=True)

MONGO_CONNECTION_STRING = "mongodb+srv://pranav:DX62cnA2hE0qsl0U@stockmarket.mvwzddk.mongodb.net/"

client = MongoClient(MONGO_CONNECTION_STRING)
db = client['UserData']
users_collection = db['users']

user_schema = UserSchema()
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

@app.route('/add_stock', methods=['GET', 'POST'])
def add_stock():
    if request.method == 'POST':
        ticker = request.form['ticker']
        shares = request.form['shares']
        conn = sqlite3.connect('myportfolio.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM portfolio WHERE ticker = ?", (ticker,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO portfolio (ticker, shares) VALUES (?, ?)", (ticker, shares))
        else:
            cursor.execute("UPDATE portfolio SET shares = shares + ? WHERE ticker = ?", (shares, ticker))
        conn.commit()
        conn.close()
        return redirect(url_for('current_portfolio'))
    return render_template('add_stock.html')

@app.route('/delete_stock', methods=['POST'])
def delete_stock():
    ticker = request.form['id']
    shares_to_delete = int(request.form['shares'])
    current_shares = int(request.form['current_shares'])
    
    conn = sqlite3.connect('myportfolio.db')
    cursor = conn.cursor()
    
    if shares_to_delete >= current_shares:
        cursor.execute("DELETE FROM portfolio WHERE ticker = ?", (ticker,))
    else:
        cursor.execute("UPDATE portfolio SET shares = shares - ? WHERE ticker = ?", (shares_to_delete, ticker))
    
    conn.commit()
    conn.close()
    return redirect(url_for('current_portfolio'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')
if __name__ == '__main__':
    con = sqlite3.connect('myportfolio.db') 
    cur=con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS portfolio 
                (ticker text NOT NULL,
                 shares text NOT NULL)""")
    print("Successfully connected to database!")
    app.run(debug=True)
    