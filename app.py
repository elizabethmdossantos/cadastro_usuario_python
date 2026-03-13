from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.security import generate_password_hash

#Models
from models.usuario import Usuario
from models.sessao_usuario import SessaoUsuario
from models.service import UsuarioService

app = Flask(__name__)
app.secret_key = "chave-super-secreta"

sessao = SessaoUsuario(session)
service = UsuarioService()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/cadastro-usuario", methods=["GET", "POST"])
def cadastrar_usuario():
    if request.method == "GET":
        return render_template("cadastro-usuario.html")
    
    nome  = request.form.get("nome", "")
    cpf   = request.form.get("cpf", "")
    email = request.form.get("email", "")
    idade = int(request.form.get("idade", 0))
    senha = request.form.get("senha", "")

    senha_hash = generate_password_hash(senha)
    usuario = Usuario(nome, cpf, email, idade, senha_hash)

    if service.salvar_usuario(usuario.to_dict()):
        sessao = SessaoUsuario(
            usuario.id,
            usuario.nome,
            usuario.perfil
        )
        sessao.salvar_na_session()
        
        flash("Usuário cadastrado com sucesso!", "sucesso")
        return redirect(url_for("buscar_usuarios"))
    
    flash("Erro ao salvar no arquivo.", "erro")
    return redirect(url_for("cadastrar_usuario"))
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = service.validar_login(request.form["cpf"], request.form["senha"])
        if usuario:
            sessao = SessaoUsuario(
                usuario["id"],
                usuario["nome"],
                usuario.get("perfil", "comum")
            )
            sessao.salvar_na_session()
            flash(f"Bem-vindo, {usuario['nome']}!", "sucesso")
            return redirect(url_for("buscar_usuarios"))

        flash("CPF ou senha inválidos.", "erro")
        return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
def logout():
    SessaoUsuario.limpar_session() #session.encerrar()
    flash("Logout realizado com sucesso.", "sucesso")
    return redirect(url_for("login"))

@app.route("/usuarios", methods=["GET"])
def buscar_usuarios():
    sessao = SessaoUsuario.carregar_da_session()
    if not sessao:
        return redirect(url_for("login"))
    
    usuarios = service.carregar_usuarios()
    busca = request.args.get("q", "").strip().lower()
    ordem = request.args.get("ordem", "")
    
    if busca:
        usuarios = [u for u in usuarios if busca in u.get("nome", "").lower() or busca in u.get("cpf", "").lower()]
    
    if ordem == "asc":
        usuarios = sorted(usuarios, key=lambda u: u.get("idade", 0))
    elif ordem == "desc":
        usuarios = sorted(usuarios, key=lambda u: u.get("idade", 0), reverse=True)
    
    return render_template("usuarios.html", usuarios=usuarios, total=len(usuarios), busca=busca, ordem=ordem)

@app.route("/usuarios/json", methods=["GET"])
def buscar_usuarios_json():
    if not SessaoUsuario.carregar_da_session():
        return jsonify({"erro": "Não autorizado"}), 401
    return jsonify(service.carregar_usuarios())

@app.route("/usuarios/editar/<cpf>", methods=["GET", "POST"])
def editar_usuario(cpf):
    sessao = SessaoUsuario.carregar_da_session()
    if not sessao:
        return redirect(url_for("login"))
    
    usuarios = service.carregar_usuarios()
    indice = next((i for i, u in enumerate(usuarios) if u["cpf"] == cpf), None)
    
    if indice is None:
        flash("Usuário não encontrado.", "erro")
        return redirect(url_for("buscar_usuarios"))
    
    if sessao.perfil != "admin" and sessao.usuario_id != usuarios[indice]["id"]:
        flash("Permissão negada.", "erro")
        return redirect(url_for("buscar_usuarios"))
    
    if request.method == "GET":
        return render_template("editar_usuario.html", usuario=usuarios[indice])
    
    usuarios[indice]["nome"] = request.form.get("nome", "")
    usuarios[indice]["email"] = request.form.get("email", "")
    usuarios[indice]["idade"] = int(request.form.get("idade", 0))
    
    if request.form.get("senha"):
        usuarios[indice]["senha"] = generate_password_hash(request.form["senha"])
    
    service.salvar_todos(usuarios)
    flash("Usuário atualizado!", "sucesso")
    return redirect(url_for("buscar_usuarios"))

@app.route("/usuarios/deletar", methods=["POST"])
def deletar_usuario():
    sessao = SessaoUsuario.carregar_da_session()
    if not sessao or sessao.perfil != "admin":
        flash("Não autorizado.", "erro")
        return redirect(url_for("buscar_usuarios"))
    
    cpf = request.form.get("cpf")
    usuarios = service.carregar_usuarios()
    usuarios = [u for u in usuarios if service.buscar_por_cpf(cpf) != u]
    
    service.salvar_todos(usuarios)
    flash("Usuário removido.", "sucesso")
    return redirect(url_for("buscar_usuarios"))

if __name__ == "__main__":
    app.run(debug=True, port=8000)