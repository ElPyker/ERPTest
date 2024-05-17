from flask import Flask, request, jsonify, render_template
import psycopg2
import json
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env (solo para desarrollo local)
if os.path.exists('.env'):
    load_dotenv()

app = Flask(__name__)

# Usa la URL de conexión completa proporcionada por Render.com
DATABASE_URL = os.getenv('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)

@app.route('/')
def index():
    return render_template('index.html')

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
        if os.path.exists('products.json'):
            with open('products.json', 'r') as file:
                json_data = json.load(file)
        else:
            json_data = {}

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
