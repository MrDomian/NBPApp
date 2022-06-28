import logging
import traceback

import mysql.connector
import requests
from pandas.io import sql


# Implement event logging system
logging.basicConfig(filename='currency.log',
                    level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')


# Connecting to the NPB API
class Currency:
    face_value = None

    def __init__(self, face_value):
        self.face_value = face_value

    def get_face_value(self):
        try:
            api_url = f"http://api.nbp.pl/api/exchangerates/rates/a/{self.face_value}"
            response = requests.get(url=api_url)
            return response.json()
        except Exception:
            logging.error('API: Connection error, status code: {}'.format(response.status_code))


try:
    # Downloading exchange rates: Dollar(USD) and Euro(EUR)
    usd = Currency("USD")
    euro = Currency("EUR")

    for item in usd.get_face_value().get('rates'):
        table_usd = item
    for item in euro.get_face_value().get('rates'):
        table_euro = item

    face_value_usd = table_usd.get('mid')
    face_value_euro = table_euro.get('mid')

    logging.debug('USD exchange rate: {}'.format(face_value_usd))
    logging.debug('EUR exchange rate: {}'.format(face_value_euro))

    # Connect with database: mydb
    connection = mysql.connector.connect(user='root',
                                         password='password',
                                         host='127.0.0.1',
                                         database='mydb',
                                         auth_plugin='mysql_native_password')

    # Add and Update new columns for product table: UnitPriceUSD and UnitPriceEuro
    cursor = connection.cursor()
    query = 'UPDATE product SET UnitPriceUSD = %s*UnitPrice, UnitPriceEuro = %s*UnitPrice'
    value = (face_value_usd, face_value_euro)
    cursor.execute(query, value)
    connection.commit()
    cursor.close()


    def generate_excel(name, db_connection):
        excel = sql.read_sql(
            'SELECT ProductID, DepartmentID, Category, IDSKU, ProductName, Quantity, UnitPrice, UnitPriceUSD, UnitPriceEuro, Ranking, ProductDesc, UnitsInStock, UnitsInOrder FROM product',
            db_connection)
        try:
            logging.debug("EXCEL: Successfully export the excel file".format(excel.to_excel(name + '.xls')))
        except:
            logging.debug('EXCEL: Error exporting to excel')

    # Generate excel file for product table
    generate_excel('product_excel', connection)

except AttributeError as err:
    logging.debug(err)
except mysql.connector.Error as err:
    logging.debug('DATABASE: Connection error, check that the database is turned on. {}. {}'.format(err.errno, err))
except Exception:
    logging.error(traceback.format_exc())
else:
    connection.close()
