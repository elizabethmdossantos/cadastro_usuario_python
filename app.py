from flask import Flask
from controllers.auth_controller import auth_bp
from controllers.usuario_controller import usuario_bp

app = Flask(__name__)
app.secret_key = "chave-super-secreta"

app.register_blueprint(auth_bp)
app.register_blueprint(usuario_bp)

if __name__ == "__main__":
    app.run(debug=True, port=8000)