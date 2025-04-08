# server.py
from flask import Flask


app = Flask(__name__)


@app.route('/api/teste', methods=['GET'])
def teste():
    return {"mensagem": "Está funcionando"}, 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)