import os
import time

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

load_dotenv()

app = Flask(__name__)

CORS(app)
metrics = PrometheusMetrics(app)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "my_postgres"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "mydatabase"),
        user=os.getenv("DB_USERNAME", "admin"),
        password=os.getenv("DB_PASSWORD", "12345"),
        sslmode=os.getenv("DB_SSLMODE", "prefer"),
        connect_timeout=5
    )


def query_inventory():
    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, product_name, category, quantity, price, created_at
                FROM inventory
                ORDER BY id DESC
            """)
            return cursor.fetchall()
    finally:
        conn.close()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "inventory-backend"
    }), 200


@app.route("/ready", methods=["GET"])
def ready():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        conn.close()

        return jsonify({
            "status": "ready",
            "database": "connected"
        }), 200

    except Exception as error:
        app.logger.error("Readiness check failed: %s", error)
        return jsonify({
            "status": "not ready",
            "database": "disconnected"
        }), 503


@app.route("/api/items", methods=["GET"])
def get_items():
    try:
        items = query_inventory()

        for item in items:
            if item.get("created_at"):
                item["created_at"] = item["created_at"].isoformat()
            item["price"] = float(item["price"])

        return jsonify(items), 200

    except Exception:
        app.logger.exception("Failed to retrieve inventory")
        return jsonify({"error": "Unable to retrieve inventory"}), 500


@app.route("/api/items", methods=["POST"])
def create_item():
    data = request.get_json(silent=True) or {}

    product_name = str(data.get("product_name", "")).strip()
    category = str(data.get("category", "")).strip()

    if not product_name or not category:
        return jsonify({
            "error": "Product name and category are required"
        }), 400

    try:
        quantity = int(data.get("quantity", 0))
        price = float(data.get("price", 0))

        if quantity < 0 or price < 0:
            raise ValueError("Quantity and price cannot be negative")

    except (ValueError, TypeError):
        return jsonify({
            "error": "Quantity must be a non-negative integer and price must be non-negative"
        }), 400

    conn = None

    try:
        conn = get_db_connection()

        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                INSERT INTO inventory
                    (product_name, category, quantity, price)
                VALUES (%s, %s, %s, %s)
                RETURNING id, product_name, category, quantity, price, created_at
            """, (product_name, category, quantity, price))

            item = cursor.fetchone()
            conn.commit()

        item["price"] = float(item["price"])
        item["created_at"] = item["created_at"].isoformat()

        return jsonify(item), 201

    except Exception:
        if conn:
            conn.rollback()
        app.logger.exception("Failed to create inventory item")
        return jsonify({"error": "Unable to create inventory item"}), 500

    finally:
        if conn:
            conn.close()


@app.route("/api/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json(silent=True) or {}

    product_name = str(data.get("product_name", "")).strip()
    category = str(data.get("category", "")).strip()

    if not product_name or not category:
        return jsonify({
            "error": "Product name and category are required"
        }), 400

    try:
        quantity = int(data.get("quantity", 0))
        price = float(data.get("price", 0))

        if quantity < 0 or price < 0:
            raise ValueError("Negative values are not allowed")

    except (ValueError, TypeError):
        return jsonify({
            "error": "Enter a valid quantity and price"
        }), 400

    conn = None

    try:
        conn = get_db_connection()

        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                UPDATE inventory
                SET product_name = %s,
                    category = %s,
                    quantity = %s,
                    price = %s
                WHERE id = %s
                RETURNING id, product_name, category, quantity, price, created_at
            """, (product_name, category, quantity, price, item_id))

            item = cursor.fetchone()

            if item is None:
                conn.rollback()
                return jsonify({"error": "Item not found"}), 404

            conn.commit()

        item["price"] = float(item["price"])
        item["created_at"] = item["created_at"].isoformat()

        return jsonify(item), 200

    except Exception:
        if conn:
            conn.rollback()
        app.logger.exception("Failed to update inventory item")
        return jsonify({"error": "Unable to update inventory item"}), 500

    finally:
        if conn:
            conn.close()


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    conn = None

    try:
        conn = get_db_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM inventory WHERE id = %s",
                (item_id,)
            )
            deleted = cursor.rowcount
            conn.commit()

        if deleted == 0:
            return jsonify({"error": "Item not found"}), 404

        return jsonify({"message": "Inventory item deleted"}), 200

    except Exception:
        if conn:
            conn.rollback()
        app.logger.exception("Failed to delete inventory item")
        return jsonify({"error": "Unable to delete inventory item"}), 500

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "5000"))
    )