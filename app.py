from flask import Flask, request, jsonify
import psycopg2
import json
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env (solo para desarrollo local)
if os.path.exists('.env'):
    load_dotenv()

app = Flask(__name__)

# Configura la conexión a la base de datos usando variables de entorno
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    dbname=os.getenv('DB_NAME')
)

@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    name = data.get('name')
    category = data.get('category')
    details = data.get('details')

    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO products (name, category, details)
            VALUES (%s, %s, %s)
        """, (name, category, json.dumps(details)))
        conn.commit()

        cursor.execute("SELECT LASTVAL()")
        product_id = cursor.fetchone()[0]

        # Actualiza el archivo JSON
        with open('products.json', 'r') as file:
            json_data = json.load(file)
        
        json_data[str(product_id)] = details

        with open('products.json', 'w') as file:
            json.dump(json_data, file, indent=4)

        return jsonify(success=True, product_id=product_id)
    except Exception as e:
        conn.rollback()
        print(e)
        return jsonify(success=False)
    finally:
        cursor.close()

@app.route('/products', methods=['GET'])
def get_products():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()

    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True)
