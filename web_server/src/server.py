from os import environ
from flask import Flask, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
from portfolio import *

app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)
app.config['MYSQL_DATABASE_HOST'] = environ.get('MYSQL_HOST')
app.config['MYSQL_DATABASE_USER'] = environ.get('MYSQL_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = environ.get('MYSQL_DB')
mysql = MySQL()
mysql.init_app(app)


@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
   header = ['Ticker', 'Last Price', 'Shares', 'Market Value']
   col_type = ['row_header', 'usd', 'int', 'usd']
   rows = []

   portfolio = Portfolio(positions=[Position(ticker, no_share) for ticker, no_share in request.args.items()], db=mysql.get_db())

   for pos in portfolio.positions:
      price = portfolio.prices[pos.ticker]
      market_value = price * pos.no_share
      rows.append((pos.ticker, price, pos.no_share, market_value))

   return render_template('portfolio.html', cols=header, rows=rows, cash=portfolio.cash, total=portfolio.evaluate_market_value(), col_type=col_type)
