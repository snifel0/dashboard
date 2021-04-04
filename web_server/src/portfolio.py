def partition(pred, ls):
    f_list = []
    t_list = []
    for e in ls:
        if pred(e):
            t_list.append(e)
        else:
            f_list.append(e)
    return f_list, t_list

class Position:

    def __init__(self, ticker: str, no_share: float):
        self.ticker = str(ticker)
        self.no_share = float(no_share)
        if self.ticker == '$$CASH$$':
            self.is_cash = True
        else:
            self.is_cash = False

    def __str__():
        return f"A position of {no_share} shares of {ticker}"

    def __repr__():
        return f"Position(ticker={ticker}, no_share={no_share})"

class Portfolio:

    def __init__(self, positions=[], db=None):
        self.positions, cash_positions = partition(lambda pos: pos.is_cash, positions)
        self.cash = self.get_cash(cash_positions)
        self.db = db
        self.ensure_all_tickers_are_registered()
        self.prices = {}
        self.update_prices()

    def get_tickers(self):
        return [pos.ticker for pos in self.positions]

    def get_cash(self, positions):
        for pos in positions:
            if pos.is_cash:
                return pos.no_share
        return 0

    def ensure_all_tickers_are_registered(self):
        tickers = self.get_tickers()
        find_registered_tickers = (
            "SELECT ticker from tickers "
            "WHERE ticker in (%s)" % ','.join(['%s'] * len(tickers))
        )
        add_ticker = "INSERT INTO tickers (ticker) VALUES (%s)"
        cursor = self.db.cursor()
        cursor.execute(find_registered_tickers, tickers)
        registered_tickers = cursor.fetchall()
        unregistered_tickers = [(ticker,) for ticker in tickers if (ticker,) not in registered_tickers]
        cursor.executemany(add_ticker, unregistered_tickers)
        cursor.close()
        self.db.commit()

    def get_last_price(self, ticker):
        price = None
        cursor = self.db.cursor()
        while price is None:
            cursor.execute('SELECT last_price, ts from tickers WHERE ticker = %s', (ticker,))
            price, time = cursor.fetchall()[0]
            self.db.commit()
        cursor.close()
        return float(price)

    def update_prices(self):
        for pos in self.positions:
            self.prices[pos.ticker] = self.get_last_price(pos.ticker)

    def evaluate_market_value(self):
        market_value = self.cash
        for pos in self.positions:
            market_value += pos.no_share * self.prices[pos.ticker]
        return market_value
