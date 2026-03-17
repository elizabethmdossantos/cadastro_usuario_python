from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

#Models
from models.usuario import Usuario
from models.repositorio import RepositorioUsuarios
from utils.validacoes import _validar_formato_cpf, sanitizar_cpf

# Blueprint agrupa rotas relacionadas a autenticação
auth_bp = Blueprint("auth", __name__)

repo = RepositorioUsuarios()

# ------------- Página inicial ------------
@auth_bp.route("/")
def home():
    return render_template("index.html")

# ------------ Cadastro -------------
@auth_bp.route("/cadastro-usuario", methods=["GET", "POST"])
def cadastrar_usuario():
    if request.method == "GET":
        return render_template("cadastro-usuario.html")
    
    # 1 - Coleta od dados do formulário
    nome  = request.form.get("nome", "").strip
    cpf   = request.form.get("cpf", "").strip
    email = request.form.get("email", "").strip
    senha = request.form.get("senha", "")
    perfil = request.form.get("perfil", "comum")

    # 2 - validar idade
    try:
        idade = int(request.form.get("idade", 0 ))
    except ValueError:
        flash("Idade inválida", "erro")
        return redirect(url_for("auth.cadastrar_usuario"))
    
    if idade < 18:
        flash("Cadastro permitido apenas para maiotres de 18 anos.", "erro")
        return redirect(url_for("auth.cadastrar_usuario"))
    
    # 3 - validar pelo cpf
    if not _validar_formato_cpf(cpf):
        flash("CPF inválido", "erro")
        return redirect(url_for("auth.cadastrar_usuario"))

    # 4 - unicidade do cpf
    if repo.cpf_exite(cpf):
        flash("CPF já cadastrado", "erro")
        return redirect(url_for("auth.cadastrar_usuario"))

    # 5 - criação objeto de persistencia
    senha_hash = generate_password_hash(senha)
    cpf_salvo = sanitizar_cpf(cpf)

    novo_usuario = Usuario(nome, cpf_salvo, email, idade, senha_hash, perfil)

    if repo.salva(novo_usuario):
        flash("Usuario cadastrado", "sucesso")
        return redirect(url_for("auth.login"))
    
    else:
        flash("Não foi possivel cadastrar usuario", "erro")
        return redirect(url_for("auth.cadastrar_usuario"))

#--------- Login --------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cpf_digitado = sanitizar_cpf(request.form.get("cpf", ""))
        senha     = request.form.get("senha", "")

        usuario = repo.buscar_por_cpf(cpf_digitado)

        if usuario and check_password_hash(usuario.senha, senha):
            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.nome
            session["usuario_perfil"] = usuario.perfil
            flash(f"Bem-vindo, {usuario.nome}!", "sucesso")
        return redirect(url_for("usuario.listar_usuarios"))

    flash("CPF ou senha inválidos", "erro")

    return render_template("login.html")

#------------Logout--------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logout realizado com sucesso.", "sucesso")
    return redirect(url_for("auth.login"))
