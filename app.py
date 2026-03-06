from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import json
import os
import uuid  # usado para gerar IDs únicos (uuid4)
from werkzeug.security import generate_password_hash, check_password_hash
import re

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

def buscar_usuario():
    usuarios = carregar_usuarios()
    return usuarios

def buscar_usuario_por_cpf(cpf):
    usuarios = carregar_usuarios()
    for usuario in usuarios:
        if usuario.get("cpf") == cpf:
            return usuario
    return None

def buscar_usuario_por_nome(nome):
    usuarios = carregar_usuarios()
    for usuario in usuarios:
        if usuario.get("nome") == nome:
            return usuario
    return None

def salvar_todos_usuarios(usuarios):
    try:
        with open("usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(usuarios, arquivo, indent=4)
        return True
    except:
        return False

def validar_cpf(cpf_enviado):
    # Validar o formato: 000.000.000-00
    padrao = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
    if not re.match(padrao, cpf_enviado):
        return None

    # Remover pontuação apenas para o calculo matemático
    cpf_limpo = re.sub(r'[^0-9]', '', cpf_enviado)

    # Impedir CPFs com todos os números iguais
    if cpf_limpo == cpf_limpo[0] * 11:
        return None

    # Cálculo dos dígitos, impede cpfs falsos
    for i in range(9, 11):
        soma = sum(int(cpf_limpo[num]) * ((i + 1) - num) for num in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf_limpo[i]):
            return None
        
    return cpf_enviado  # Retorna o CPF formatado se for válido


# ROTAS

@app.route("/")
def home():
    # Renderiza a página inicial com o formulário de cadastro
    return render_template("home.html")

# LOGIN

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cpf_digitado = request.form.get("cpf")
        senha = request.form.get("senha")
        codigo_enviado = request.form.get("codigo_admin")
    
        cpf_validado = validar_cpf(cpf_digitado)
        
        if not cpf_validado:
            flash("CPF inválido! Use o formato 000.000.000-00", "erro")
            return render_template('login.html', form_data=request.form)
        
        usuarios = carregar_usuarios()
        usuario = next((u for u in usuarios if u.get("cpf") == cpf_validado), None)

        if usuario and check_password_hash(usuario["senha"], senha):
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["usuario_cpf"] = usuario["cpf"]

            if codigo_enviado == "admin123":
                session["nivel"] = "admin"
            else:
                session["nivel"] = "comum"

            flash(f"Bem-vindo, {usuario['nome']}!", "sucesso")
            return redirect(url_for('buscar_usuarios'))
        else:
            flash("CPF ou senha incorretos.", "erro")
            return render_template('login.html', form_data=request.form)

    return render_template("login.html")

# CADASTRO DE USUÁRIO

@app.route("/cadastro-usuario", methods=["GET", "POST"])
def cadastrar_usuario():
    # Recupera os dados enviados pelo formulário HTML
    if request.method == "GET":
        return render_template("cadastro-usuario.html")
    
    nome = request.form.get("nome")
    cpf_digitado = request.form.get("cpf")  # CPF do usuário (identificador único)
    email = request.form.get("email")
    idade = request.form.get("idade")
    senha = request.form.get("senha")
    senha_hash = generate_password_hash(senha) # Armazena a senha de forma segura usando hash
   
    cpf_validado = validar_cpf(cpf_digitado)
    # validação do CPF, impede cadastro de CPFs com formato errado ou falsos
    if not cpf_validado:
        flash("CPF inválido! Use o formato 000.000.000-00", "erro")
        return render_template('cadastro-usuario.html', form_data=request.form)
    
    
    # carrega usuários atuais para checar duplicatas
    usuarios = carregar_usuarios()

    # evita inserir CPF repetido
    if any(u.get("cpf") == cpf_validado for u in usuarios):
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
        "cpf": cpf_validado,
        "email": email,
        "idade": idade,
        "senha": senha_hash,
    }

    # tenta salvar usando a função auxiliar
    status = salvar_usuario(usuario)

    if status:
        session["usuario_id"] = usuario["id"]
        session["usuario_nome"] = usuario["nome"]
        session["usuario_cpf"] = usuario["cpf"]
        session["nivel"] = "comum"
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

# Rota para retornar a lista de usuários em formato JSON, protegida por autenticação
@app.route("/usuarios/json", methods=["GET"])
def buscar_usuarios_json():
    if "usuario_id" not in session:
        return jsonify({"erro": "Não autorizado"}, 401)
    usuarios = carregar_usuarios()
    return jsonify(usuarios)

# Rota para exibir a lista de usuários em uma página HTML, protegida por autenticação
@app.route("/usuarios", methods=["GET"])
def buscar_usuarios():
    if "usuario_id" not in session:
        flash("Você precisa estar logado.", "erro")
        return redirect(url_for("login"))
    
    usuarios = carregar_usuarios()
 
    termo_busca = request.args.get("busca") # Pega o valor do input 'name="busca"'
    if termo_busca:
        usuarios = [u for u in usuarios if termo_busca in u.get("cpf", "") or termo_busca in u.get("nome", "")]

 # NOVA PARTE: Ordenação por idade
    ordem = request.args.get("ordem", "asc")
    usuarios = sorted(
        usuarios,
        key=lambda u: int(u.get("idade", 0)),
        reverse=(ordem == "desc"))

    total = len(usuarios)
    return render_template("usuarios.html", usuarios=usuarios, total=total)



# EDITAR

@app.route("/usuarios/editar/<cpf>", methods=["GET", "POST"])
def editar_usuario(cpf):

    if "usuario_id" not in session:
        flash("Não autorizado.", "erro")
        return redirect(url_for("login"))
    
    e_dono_do_perfil = session.get("usuario_cpf") == cpf
    e_admin = session.get("nivel") == "admin"

    if not e_dono_do_perfil and not e_admin:
        flash("Apenas administradores ou o próprio usuário podem editar este perfil.", "erro")
        return redirect(url_for("buscar_usuarios"))
    
    usuarios = carregar_usuarios()

    usuario = next((u for u in usuarios if u["cpf"] == cpf), None)

    if not usuario:
        flash("Usuário não encontrado.", "erro")
        return redirect(url_for("buscar_usuarios"))
    
    if request.method == "GET":
        return render_template("editar_usuario.html", usuario=usuario)

    nome = request.form.get("nome")
    email = request.form.get("email")
    idade = int(request.form.get("idade"))
    senha = request.form.get("senha")
    
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
        return redirect(url_for("buscar_usuarios"))
    else:
        flash("Erro ao atualizar usuário.", "erro")
        return redirect(url_for("buscar_usuarios"))


# DELETAR

@app.route("/usuarios/deletar", methods=["POST"])
def deletar_usuario():
    # Verifica se está logado
    if "usuario_id" not in session:
        flash("Você precisa estar logado.", "erro")
        return redirect(url_for("login"))

    # Apenas Admin deleta
    if session.get("nivel") != "admin":
        flash("Acesso negado! Apenas administradores podem deletar usuários.", "erro")
        return redirect(url_for("buscar_usuarios"))
    
    cpf_para_deletar = request.form.get("cpf")
    if not cpf_para_deletar:
        flash("CPF não fornecido.", "erro")
        return redirect(url_for("buscar_usuarios"))
    
    usuarios = carregar_usuarios()
    # Cria a nova lista sem o usuário deletado
    novos_usuarios = [u for u in usuarios if u.get("cpf") != cpf_para_deletar]
    
    if salvar_todos_usuarios(novos_usuarios):
        flash("Usuário deletado com sucesso.", "sucesso")
    else:
        flash("Erro ao salvar alterações no banco de dados.", "erro")
        
    return redirect(url_for("buscar_usuarios"))


if __name__ == "__main__":

    app.run(debug=True, port=8000)
