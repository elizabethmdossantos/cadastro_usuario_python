from flask import Flask
from controllers.auth_controller import auth_bp

app = Flask(__name__)
app.secret_key = "chave-super-secreta"

if __name__ == "__main__":
    app.run(debug=True, port=8000)