import os
import asyncio
import mysql.connector
from mysql.connector import errorcode
from mysql.connector.errors import Error
import time
import FinanceDataReader as fdr
from dateutil.relativedelta import relativedelta
from datetime import datetime


MYSQL_HOST = os.environ.get('MYSQL_HOST')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_DB = os.environ.get('MYSQL_DB')

TABLES = {}
TABLES['tickers'] = (
    "CREATE TABLE `tickers` ("
    "  `ticker_no` int(11) NOT NULL AUTO_INCREMENT,"
    "  `ticker` varchar(10) NOT NULL UNIQUE,"
    "  `last_price` double NULL,"
    "  `ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
    "  PRIMARY KEY (`ticker_no`)"
    ") ENGINE=InnoDB"
)


async def get_last_price(ticker: str):
    end_date = datetime.today()
    start_date = end_date - relativedelta(days=7)
    try:
        data = fdr.DataReader(ticker, start_date, end_date)
    except ValueError as e:
        return None
    except Exception as e:
        print(f"[Exception] Symbol: {ticker}\n")
        print(e)
        return None
    price = float(data['Close'][-1])
    preview_price = data['Close'][-2]
    time = data.index[0]
    return price, time, preview_price


async def price_updater(name: int, ticker_q: asyncio.Queue) -> None:
    update_price = (
        "UPDATE tickers SET "
        "   last_price = %s, "
        "   ts = TIME(NOW()) "
        "WHERE ticker = %s"
    )
    cnx = get_db_connection()
    while True:
        ticker = str(await ticker_q.get())
        result = await get_last_price(ticker)
        if result:
            cursor = cnx.cursor()
            price = result[0]
            cursor.execute(update_price, (price, ticker))
            cnx.commit()
            cursor.close()
        ticker_q.task_done()


def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


def get_db_connection():
    while True:
        try:
            cnx = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PASSWORD, host=MYSQL_HOST, database=MYSQL_DB)
            print(f"MYSQL connection established")
            break
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            elif err.errno == errorcode.CR_CONN_HOST_ERROR:
                print(f"MYSQL not responds.. waiting for mysql up")
                time.sleep(1)
            else:
                print(err)
    return cnx


def create_tables(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("USE {}".format(MYSQL_DB))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(MYSQL_DB))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(MYSQL_DB))
            cnx.database = MYSQL_DB
        else:
            print(err)
            exit(1)
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")
    cursor.close()


async def main():
    number_of_updaters = 10
    ticker_q = asyncio.Queue(maxsize=50)
    tickers_to_be_updated = (
        "SELECT ticker from tickers "
        "WHERE last_price is NULL "
        "      OR ts < TIME(DATE_SUB(NOW(), INTERVAL 1 MINUTE))"
    )
    price_updaters = [asyncio.create_task(price_updater(i, ticker_q)) for i in range(number_of_updaters)]
    cnx = get_db_connection()
    create_tables(cnx)
    while True:
        cursor = cnx.cursor()
        cursor.execute(tickers_to_be_updated)
        tickers = [_[0] for _ in cursor.fetchall()]
        cnx.commit()
        cursor.close()
        for ticker in tickers:
            await ticker_q.put(ticker)
        await ticker_q.join()
        await asyncio.sleep(1)
    cnx.close()


if __name__ == "__main__":
    asyncio.run(main())
