from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import json
import os
import uuid  # usado para gerar IDs únicos (uuid4)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# chave necessária para utilizar `flash` e sessões
app.secret_key = "chave-super-secreta"

# FUNÇÕES AUXILIARES

def carregar_usuarios():
    # Verifica se o arquivo 'usuarios.json' existe e carrega os dados
    try:
        if os.path.exists("usuarios.json"):
            with open("usuarios.json", "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        else:
            return []  # Retorna uma lista vazia se o arquivo não existir
    except:
        return []  # Retorna uma lista vazia se ocorrer algum erro ao ler o arquivo

def salvar_usuario(usuario):
    # Carrega os usuários existentes
    usuarios = carregar_usuarios()
    try:
        # Adiciona o novo usuário à lista
        usuarios.append(usuario)

        # Salva a lista atualizada de usuários no arquivo 'usuarios.json'
        with open("usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(usuarios, arquivo, indent=4)

        return True  # Retorna True se o salvamento for bem-sucedido
    except:
        return False  # Retorna False se ocorrer um erro ao salvar

def buscar_usuario_por_email(cpf):
    usuarios = carregar_usuarios()
    for usuario in usuarios:
        if usuario.get("cpf") == cpf:
            return usuario
    return None

def salvar_todos_usuarios(usuarios):
    try:
        with open("usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(usuarios, arquivo, indent=4)
        return True
    except:
        return False


# ROTAS

@app.route("/")
def home():
    # Renderiza a página inicial com o formulário de cadastro
    return render_template("home.html")

@app.route("/login", methods=["GET"])
def mostrar_login():
    return render_template("login.html")

@app.route("/cadastro-usuario", methods=["GET"])
def mostrar_cadastro():
    return render_template("cadastro-usuario.html")


# LOGIN

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cpf = request.form.get("cpf")
        senha = request.form.get("senha")
    
    usuarios = carregar_usuarios()
    usuario = next((u for u in usuarios if u.get("cpf") == cpf), None) # Busca o usuário com o CPF fornecido, ou None se não encontrado

    if usuario ["cpf"] == cpf and check_password_hash(usuario["senha"], senha): # Verifica se o usuário existe e se a senha fornecida corresponde ao hash armazenado
        session ["usuario_id"] = usuario["id"]
        session ["usuario_nome"] = usuario["nome"]

        flash("Login bem-sucedido!",  "sucesso")
        return redirect(url_for('buscar_usuarios'))
    
    else:
        flash("CPF ou senha incorretos.", "erro")
        return render_template('login.html', form_data=request.form)# Mantém os dados do formulário para facilitar correção pelo usuário


# CADASTRO DE USUÁRIO

@app.route("/cadastro-usuario", methods=["GET", "POST"])
def cadastrar_usuario():
    # Recupera os dados enviados pelo formulário HTML
    if request.method == "GET":
        return render_template("cadastro-usuario.html")
    nome = request.form.get("nome")
    cpf = request.form.get("cpf")            # CPF do usuário (identificador único)
    email = request.form.get("email")
    idade = request.form.get("idade")
    senha = request.form.get("senha")
    senha_hash = generate_password_hash(senha) # Armazena a senha de forma segura usando hash

    # carrega usuários atuais para checar duplicatas
    usuarios = carregar_usuarios()

    # evita inserir CPF repetido
    if any(u.get("cpf") == cpf for u in usuarios):
        flash("CPF já cadastrado no sistema.", "erro")
        '''return redirect(url_for("home")) #antes'''
        return render_template('cadastro-usuario.html', form_data=request.form) # Mantém os dados do formulário para facilitar correção pelo usuário
    
    if not idade or int(idade) < 18:
        flash("Idade mínima para cadastro é 18 anos.", "erro")
        return render_template('cadastro-usuario.html', form_data=request.form)

    # cria o objeto do usuário, incluindo um id UUID
    usuario = {
        "id": str(uuid.uuid4()),  # identificador global para uso interno
        "nome": nome,
        "cpf": cpf,
        "email": email,
        "idade": idade,
        "senha": senha_hash,
    }

    # tenta salvar usando a função auxiliar
    status = salvar_usuario(usuario)

    if status:
        # após cadastro redireciona para a lista de usuários
        flash("Usuário cadastrado com sucesso.", "sucesso")
        return redirect(url_for('buscar_usuarios'))
    else:
        # caso de erro de escrita
        flash("Não foi possível cadastrar o usuário.", "erro")
        return redirect(url_for('home'))


# LOGOUT

@app.route("/logout")
def logout():
    session.clear()
    flash("Logout realizado com sucesso!", "sucesso")
    return redirect(url_for("login"))


# USUÁRIOS

@app.route("/usuarios", methods=["GET"])
def buscar_usuarios():
    usuarios = carregar_usuarios()
    if "usuario_id" not in session:
        flash("Você precisa estar logado.", "erro")
        return redirect(url_for("login"))
    
    usuarios = carregar_usuarios()
    total = len(usuarios)
    return render_template("usuarios.html", usuarios=usuarios, total=total)

@app.route("/usuarios/json", methods=["GET"])
def buscar_usuarios_json():
    if "usuario_id" not in session:
        return jsonify({"erro": "Não autorizado"}, 401)
    usuarios = carregar_usuarios()
    return jsonify(usuarios)


# EDITAR

@app.route("/usuarios/editar/<cpf>", methods=["GET", "POST"])
def editar_usuario(cpf):

    if "usuario_id" not in session:
        flash("Não autorizado.", "erro")
        return redirect(url_for("login"))
    
    usuarios = carregar_usuarios()

    # aqui vai buscar o usuário pelo cpf
    usuario = next((u for u in usuarios if u["cpf"] == cpf), None)

    if not usuario:
        flash("Usuário não encontrado.", "erro")
        return redirect(url_for("buscar_usuarios"))
    
    # GET - carrega o formulário
    if request.method == "GET":
        return render_template("editar_usuario.html", usuario=usuario)
    
    # POST - atualiza os dados
    nome = request.form.get("nome")
    email = request.form.get("email")
    idade = int(request.form.get("idade"))
    senha = request.form.get("senha")
    
    # validação de idade também no update
    if not idade or int(idade) < 18:
        flash("Idade mínima para cadastro é 18 anos.", "erro")
        return render_template('cadastro-usuario.html', form_data=request.form)

    usuario["nome"] = nome
    usuario["email"] = email
    usuario["idade"] = idade

    # atualiza senha somente se for preenchida
    if senha:
        usuario["senha"] = generate_password_hash(senha)

    status = salvar_todos_usuarios(usuarios)

    if status:
        flash("Usuário atualizado com sucesso!", "sucesso")
    else:
        flash("Erro ao atualizar usuário.", "erro")
        return redirect(url_for("buscar_usuários"))


# DELETAR

@app.route("/usuarios/deletar", methods=["POST"])
def deletar_usuario(cpf):
    if "usuario_id" not in session:
        flash("Não autorizado.", "erro")
        return redirect(url_for("login"))
    
    cpf = request.form.get("cpf")
    if not cpf:
        flash("CPF necessário para deletar usuário.", "erro")
        return redirect(url_for("buscar_usuarios"))
    
    usuarios = carregar_usuarios()
    novos_usuarios = [u for u in usuarios if u.get("cpf") != cpf]
    
    try:
        with open("usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(novos_usuarios, arquivo, indent=4)
        flash("Usuário deletado com sucesso.", "sucesso")
        return redirect(url_for("buscar_usuarios"))
    except Exception as e:
        flash(f"Erro ao deletar: {e}", "erro")
        return redirect(url_for("buscar_usuarios"))


if __name__ == "__main__":

    app.run(debug=True, port=8000)
