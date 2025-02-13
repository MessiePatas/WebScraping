from flask import Flask, request, jsonify

from Godaddy import obtener_precio_godaddy
from Godaddy import obtener_precio_hostinger
app = Flask(__name__)


@app.route("/scrape", methods=["GET"])
def scrape():
    dominio = request.args.get("dominio")
    proveedor = request.args.get("proveedor")  # 'godaddy', 'hostinger' o 'todos'

    if not dominio:
        return jsonify({"error": "Debe proporcionar un dominio"}), 400

    resultados = {}
    if proveedor == "godaddy" or proveedor == "todos":
        resultados["godaddy"] = obtener_precio_godaddy(dominio)
    if proveedor == "hostinger" or proveedor == "todos":
        resultados["hostinger"] = obtener_precio_hostinger(dominio)

    return jsonify({"dominio": dominio, "precios": resultados})


if __name__ == "__main__":
    app.run(debug=True, port=5000)