from flask import Flask, jsonify

import config  # garante que .env é carregado antes de tudo
from controllers import auth_controller, usuario_controller, auditoria_controller, termo_controller

app = Flask(__name__)
app.register_blueprint(auth_controller.bp)
app.register_blueprint(usuario_controller.bp)
app.register_blueprint(auditoria_controller.bp)
app.register_blueprint(termo_controller.bp)


@app.errorhandler(404)
def nao_encontrado(_):
    return jsonify(erro="Rota não encontrada"), 404


if __name__ == "__main__":
    app.run(port=5000, debug=True)