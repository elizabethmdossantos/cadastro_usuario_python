from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
# Models
from models.repositorio import RepositorioUsuarios
from utils.validacoes import sanitizar_cpf

# Blueprint agrupa rotas relaconadas autenticiade
usuario_bp = Blueprint("usuario", __name__)

repo = RepositorioUsuarios()

def _usuario_logado() -> bool:
    return "usuario_id" in session

def _eh_admin() -> bool:
    return session.get("usuario_perfil") == "admin"

# Listagem --------------
@usuario_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    if not _usuario_logado():
        flash("Você precisa estar logado.", "erro")
        return redirect(url_for("auth.login"))
    
    usuarios = repo.listar()

    # Buscar por nome ou CPF
    busca = request.args.get("q", "").strip().lower()
    if busca:
        usuarios = [u for u in usuarios
                    if busca in u.nome.lower()
                    if busca in u.cpf.lower()
                    ]
        
    # Ordenação de idade
    ordem = request.args.get("ordem", "")
    if ordem == "asc":
        usuarios = sorted(usuarios, key=lambda u: u.idade)
    if ordem == "desc":
        usuarios = sorted(usuarios, key=lambda u: u.idade, reverse=True)

        return render_template(
            "usuarios.html",
            usuarios = usuarios,
            total=len(usuarios),
            busca=busca,
            ordem=ordem,
        )
@usuario_bp.route("/usuarios/json", methods=["GET"])
def listar_usuarios_json():
    if not _usuario_logado:
        return jsonify({"erro" : "Não autorizado"}), 401
    
    usuarios = repo.listar()
    return jsonify([u.to_dict() for u in usuarios])

# Edição ---------------------
@usuario_bp.route("/usuarios/editar<cpf>", methods=["GET", "POST"])
def editar_usuario(cpf):
    if not _usuario_logado():
        flash("Não autorizado.", "erro")
        return redirect(url_for("auth.login"))
    
    usuario = repo.buscar_por_cpf(cpf)

    if not usuario:
        flash("Usuário não encontrado", "erro")
        return redirect(url_for("usuario.listar_usuarios"))
    
    # Permissão: adm edita qualquer um; comum edita o próprio
    eh_proprio = session.get("usuario_id") == usuario.id
    if not _eh_admin() and not eh_proprio:
        flash("Você só pode editar seu próprio perfil", "erro")
        return redirect(url_for("usuario.listar_usuarios"))
    
    if request.method == "GET":
        return render_template("edita_usuario.html", usuario=usuario)
    
    # Atualizar dados
    try:
        idade = int(request.form.get("idade", 0))
    except ValueError:
        flash("Idade inválida", "erro")
        return redirect(url_for("usuario.editar_usuario", cpf=cpf))
    
    if idade < 18:
        flash("Usuário deve ser maior de 18 anos", "erro")
        return redirect(url_for("usuario.editar_usuario", cpf=cpf))
    
    usuario.nome = request.form.get("nome", "").strip()
    usuario.email = request.form.get("email", "").strip()
    usuario.idade = idade

    senha = request.form.get("senha", "")
    if senha:
        usuario.senha = generate_password_hash(senha)

    if repo.atualizar(usuario):
        flash("Usuário atualizado com sucesso", "sucesso")
    else:
        flash("Erro ao atualizar usuário", "erro")

    return redirect(url_for("usuario.editar_usuario"))

# Exclusão -------------------
@usuario_bp.route("/usuarios/deletar", methods=["POST"])
def deletar_usuario():
    if not _usuario_logado():
        flash("Não autorizado.", "erro")

    if not _eh_admin():
        flash("Apenas administradores podem excluir usuários.", "erro")
        return redirect(url_for("usuario.listar_usuarios"))
    
    cpf = request.form.get("cpf")
    if not cpf:
        flash("CPF neessário para exclusão", "erro")
        return redirect(url_for("usuario.listar_usuarios"))
    
    if repo.deletar(cpf):
        flash("Usuário removido", "sucesso")
    else:
        flash("Erro ao deletar o usuário", "erro")

    return redirect(url_for("usuario.listar_usuarios"))