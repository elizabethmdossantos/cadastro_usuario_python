from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import json
import os
import uuid
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "chave-super-secreta"


# ==========================
# FUNÇÕES AUXILIARES
# ==========================

def carregar_usuarios():
    try:
        if os.path.exists("usuarios.json"):
            with open("usuarios.json", "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        else:
            return []
    except:
        return []


def salvar_usuario(usuario):
    usuarios = carregar_usuarios()
    try:
        usuarios.append(usuario)
        with open("usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(usuarios, arquivo, indent=4)
        return True
    except:
        return False


def salvar_todos_usuarios(usuarios):
    try:
        with open("usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(usuarios, arquivo, indent=4)
        return True
    except:
        return False


def buscar_usuario_por_email(email):
    usuarios = carregar_usuarios()
    for usuario in usuarios:
        if usuario.get("email") == email:
            return usuario
    return None


# ==========================
# ATIVIDADE 2 — ITEM 1
# Validação de CPF com Regex
# ==========================

def validar_formato_cpf(cpf):
    """
    Verifica se o CPF está no formato 000.000.000-00
    usando expressão regular (Regex).
    """
    padrao = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
    return re.match(padrao, cpf) is not None


def sanitizar_cpf(cpf):
    """
    Remove pontos e traço do CPF antes de salvar.
    Ex: 123.456.789-09 → 12345678909
    """
    return re.sub(r"[.\-]", "", cpf)


# ==========================
# ROTAS
# ==========================

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------
# CADASTRO
# --------------------------

@app.route("/cadastro-usuario", methods=["GET", "POST"])
def cadastrar_usuario():
    if request.method == "GET":
        return render_template("cadastro-usuario.html")

    nome  = request.form.get("nome", "").strip()
    cpf   = request.form.get("cpf", "").strip()
    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "")

    # ATIVIDADE 1 — ITEM 3: Validação de idade
    try:
        idade = int(request.form.get("idade", 0))
    except ValueError:
        flash("Idade inválida.", "erro")
        return redirect(url_for("cadastrar_usuario"))

    if idade < 18:
        flash("Cadastro permitido apenas para maiores de 18 anos.", "erro")
        # ATIVIDADE 1 — ITEM 4: redireciona mantendo dados via request.form
        return redirect(url_for("cadastrar_usuario"))

    # ATIVIDADE 2 — ITEM 1: Validação de formato do CPF
    if not validar_formato_cpf(cpf):
        flash("CPF inválido. Use o formato 000.000.000-00.", "erro")
        return redirect(url_for("cadastrar_usuario"))

    # ATIVIDADE 2 — ITEM 1: Sanitização — remove pontos e traço antes de salvar
    cpf_salvo = sanitizar_cpf(cpf)

    usuarios = carregar_usuarios()

    # Unicidade do CPF (compara sem formatação)
    if any(sanitizar_cpf(u.get("cpf", "")) == cpf_salvo for u in usuarios):
        flash("CPF já cadastrado no sistema.", "erro")
        return redirect(url_for("cadastrar_usuario"))

    senha_hash = generate_password_hash(senha)

    usuario = {
        "id":     str(uuid.uuid4()),
        "nome":   nome,
        "cpf":    cpf_salvo,   # salvo sem formatação
        "email":  email,
        "idade":  idade,
        "senha":  senha_hash,
        # ATIVIDADE 2 — ITEM 4: perfil escolhido no formulário (admin ou comum)
        "perfil": request.form.get("perfil", "comum"),
    }

    if salvar_usuario(usuario):
        flash("Usuário cadastrado com sucesso.", "sucesso")
        return redirect(url_for("login"))
    else:
        flash("Não foi possível cadastrar o usuário.", "erro")
        return redirect(url_for("cadastrar_usuario"))


# --------------------------
# LOGIN
# --------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cpf_digitado = sanitizar_cpf(request.form.get("cpf", ""))
        senha        = request.form.get("senha", "")
        usuarios     = carregar_usuarios()

        for usuario in usuarios:
            cpf_salvo = sanitizar_cpf(usuario.get("cpf", ""))
            if cpf_salvo == cpf_digitado and check_password_hash(usuario["senha"], senha):
                # ✅ CORREÇÃO DO BUG: salva dados do usuário na sessão
                session["usuario_id"]     = usuario["id"]
                session["usuario_nome"]   = usuario["nome"]
                # ATIVIDADE 2 — ITEM 4: perfil na sessão
                session["usuario_perfil"] = usuario.get("perfil", "comum")

                flash(f"Bem-vindo, {usuario['nome']}!", "sucesso")
                return redirect(url_for("buscar_usuarios"))

        flash("CPF ou senha inválidos.", "erro")

    return render_template("login.html")


# --------------------------
# LOGOUT
# --------------------------

@app.route("/logout")
def logout():
    session.clear()
    flash("Logout realizado com sucesso.", "sucesso")
    return redirect(url_for("login"))


# --------------------------
# LISTAGEM (PROTEGIDA)
# ATIVIDADE 2 — ITENS 2 e 3: busca e ordenação
# --------------------------

@app.route("/usuarios", methods=["GET"])
def buscar_usuarios():
    if "usuario_id" not in session:
        flash("Você precisa estar logado.", "erro")
        return redirect(url_for("login"))

    usuarios = carregar_usuarios()

    # ATIVIDADE 2 — ITEM 2: Busca por nome ou CPF via query string (?q=...)
    busca = request.args.get("q", "").strip().lower()
    if busca:
        usuarios = [
            u for u in usuarios
            if busca in u.get("nome", "").lower()
            or busca in u.get("cpf", "").lower()
        ]

    # ATIVIDADE 2 — ITEM 3: Ordenação por idade via query string (?ordem=asc ou ?ordem=desc)
    ordem = request.args.get("ordem", "")
    if ordem == "asc":
        usuarios = sorted(usuarios, key=lambda u: u.get("idade", 0))
    elif ordem == "desc":
        usuarios = sorted(usuarios, key=lambda u: u.get("idade", 0), reverse=True)

    total = len(usuarios)

    return render_template(
        "usuarios.html",
        usuarios=usuarios,
        total=total,
        busca=busca,
        ordem=ordem,
    )


@app.route("/usuarios/json", methods=["GET"])
def buscar_usuarios_json():
    if "usuario_id" not in session:
        return jsonify({"erro": "Não autorizado"}), 401
    usuarios = carregar_usuarios()
    return jsonify(usuarios)


# --------------------------
# UPDATE (EDITAR USUÁRIO)
# ATIVIDADE 2 — ITEM 4: permissão por perfil
# --------------------------

@app.route("/usuarios/editar/<cpf>", methods=["GET", "POST"])
def editar_usuario(cpf):
    if "usuario_id" not in session:
        flash("Não autorizado.", "erro")
        return redirect(url_for("login"))

    usuarios  = carregar_usuarios()
    usuario   = next((u for u in usuarios if sanitizar_cpf(u["cpf"]) == sanitizar_cpf(cpf)), None)

    if not usuario:
        flash("Usuário não encontrado.", "erro")
        return redirect(url_for("buscar_usuarios"))

    # ATIVIDADE 2 — ITEM 4:
    # Admin pode editar qualquer um; comum só edita o próprio perfil
    perfil_logado = session.get("usuario_perfil", "comum")
    eh_proprio    = session.get("usuario_id") == usuario.get("id")

    if perfil_logado != "admin" and not eh_proprio:
        flash("Você só pode editar o seu próprio perfil.", "erro")
        return redirect(url_for("buscar_usuarios"))

    if request.method == "GET":
        return render_template("editar_usuario.html", usuario=usuario)

    nome  = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "")

    try:
        idade = int(request.form.get("idade", 0))
    except ValueError:
        flash("Idade inválida.", "erro")
        return redirect(url_for("editar_usuario", cpf=cpf))

    if idade < 18:
        flash("Usuário deve ser maior de 18 anos.", "erro")
        return redirect(url_for("editar_usuario", cpf=cpf))

    usuario["nome"]  = nome
    usuario["email"] = email
    usuario["idade"] = idade

    if senha:
        usuario["senha"] = generate_password_hash(senha)

    if salvar_todos_usuarios(usuarios):
        flash("Usuário atualizado com sucesso.", "sucesso")
    else:
        flash("Erro ao atualizar usuário.", "erro")

    return redirect(url_for("buscar_usuarios"))


# --------------------------
# DELETAR (PROTEGIDA)
# ATIVIDADE 2 — ITEM 4: apenas Admin pode deletar
# --------------------------

@app.route("/usuarios/deletar", methods=["POST"])
def deletar_usuario():
    if "usuario_id" not in session:
        flash("Não autorizado.", "erro")
        return redirect(url_for("login"))

    # ATIVIDADE 2 — ITEM 4: bloqueia usuário comum de deletar
    if session.get("usuario_perfil") != "admin":
        flash("Apenas administradores podem excluir usuários.", "erro")
        return redirect(url_for("buscar_usuarios"))

    cpf = request.form.get("cpf")
    if not cpf:
        flash("CPF necessário para exclusão.", "erro")
        return redirect(url_for("buscar_usuarios"))

    usuarios = carregar_usuarios()
    novos    = [u for u in usuarios if sanitizar_cpf(u.get("cpf", "")) != sanitizar_cpf(cpf)]

    try:
        with open("usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(novos, arquivo, indent=4)
        flash("Usuário removido.", "sucesso")
    except Exception as e:
        flash(f"Erro ao deletar: {e}", "erro")

    return redirect(url_for("buscar_usuarios"))


if __name__ == "__main__":
    app.run(debug=True, port=8000)