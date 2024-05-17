from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import psycopg2
import json
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env (solo para desarrollo local)
if os.path.exists('.env'):
    load_dotenv()

app = Flask(__name__)

# Configuración de la conexión a PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)

# Configuración de la conexión a MongoDB
MONGO_URL = os.getenv('MONGO_URL', 'mongodb+srv://BrewIt:uDd3StzXJ2EdOhG5@cluster0.yvhgb38.mongodb.net/?retryWrites=true&w=majority')

client = MongoClient(MONGO_URL)
db = client.SmartPipes
products_collection = db.Products

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
        # Insertar en PostgreSQL
        cursor.execute("""
            INSERT INTO products (name, category)
            VALUES (%s, %s)
            RETURNING product_id
        """, (name, category))
        conn.commit()
        product_id = cursor.fetchone()[0]

        # Insertar en MongoDB
        product_details = {
            "product_id": product_id,
            "details": details
        }
        result = products_collection.insert_one(product_details)

        return jsonify(success=True, product_id=product_id, mongo_id=str(result.inserted_id))
    except Exception as e:
        conn.rollback()
        print(e)
        return jsonify(success=False)
    finally:
        cursor.close()

@app.route('/products', methods=['GET'])
def get_products():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        
        # Convertir los productos a un diccionario
        products_dict = []
        for product in products:
            product_dict = {
                "product_id": product[0],
                "name": product[1],
                "category": product[2],
                "details": []
            }
            # Buscar detalles en MongoDB
            mongo_product = products_collection.find_one({"product_id": product[0]})
            if mongo_product:
                product_dict["details"] = mongo_product["details"]
            products_dict.append(product_dict)
        
        return jsonify(products_dict)
    except Exception as e:
        print(e)
        return jsonify(success=False)
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(debug=True)
