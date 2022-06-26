import logging
import requests
import mysql.connector
from pandas.io import sql

logging.basicConfig(filename='currency.log',
                    level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')


class Currency:
    face_value = None

    def __init__(self, face_value):
        self.face_value = face_value

    def get_face_value(self):
        try:
            response = requests.get(url=f"http://api.nbp.pl/api/exchangerates/rates/a/asd/{self.face_value}")
            return response.json()
        except:
            text = 'Some problems'
            return text


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

try:
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
        excel.to_excel(name + '.xls')


    # Generate excel file for product table
    generate_excel('product_excel', connection)

except mysql.connector.Error as err:
    print('Connection error, check that the database is turned on.', err.errno, 'n', err)
except:
    print('Connection error, please contact the administrator', 'n')
else:
    connection.close()
