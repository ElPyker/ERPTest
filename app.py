from flask import Flask, request, jsonify
import mysql.connector
import json
from dotenv import load_dotenv
import os

# Cargar variables de entorno si existe un archivo .env (útil para desarrollo local)
if os.path.exists('.env'):
    load_dotenv()

app = Flask(__name__)

# Configura la conexión a MySQL usando variables de entorno
db = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    name = data.get('name')
    category = data.get('category')
    details = data.get('details')

    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO products (name, category, details)
            VALUES (%s, %s, %s)
        """, (name, category, json.dumps(details)))
        db.commit()

        product_id = cursor.lastrowid

        # Actualiza el archivo JSON
        with open('products.json', 'r') as file:
            json_data = json.load(file)
        
        json_data[str(product_id)] = details

        with open('products.json', 'w') as file:
            json.dump(json_data, file, indent=4)

        return jsonify(success=True, product_id=product_id)
    except Exception as e:
        db.rollback()
        print(e)
        return jsonify(success=False)
    finally:
        cursor.close()

@app.route('/products', methods=['GET'])
def get_products():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True)
