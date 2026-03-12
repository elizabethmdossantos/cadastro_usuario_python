from models.usuario import Usuario
import json
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

class UsuarioService:
    
    def __init__(self):
        self.arquivo = "usuarios.json"
    
    def carregar_usuarios(self):
        try:
            if os.path.exists(self.arquivo):
                with open(self.arquivo, "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def salvar_usuario(self, usuario):
        usuarios = self.carregar_usuarios()
        usuarios.append(usuario)
        return self._salvar_todos(usuarios)
    
    def salvar_todos(self, usuarios):
        return self._salvar_todos(usuarios)
    
    def _salvar_todos(self, usuarios):
        try:
            with open(self.arquivo, "w", encoding="utf-8") as f:
                json.dump(usuarios, f, indent=4)
            return True
        except:
            return False
    
    def buscar_por_cpf(self, cpf):
        cpf_limpo = re.sub(r"[.\-]", "", cpf)
        usuarios = self.carregar_usuarios()
        return next((u for u in usuarios if re.sub(r"[.\-]", "", u.get("cpf", "")) == cpf_limpo), None)
    
    def cpf_existe(self, cpf):
        cpf_limpo = re.sub(r"[.\-]", "", cpf)
        return any(re.sub(r"[.\-]", "", u.get("cpf", "")) == cpf_limpo for u in self.carregar_usuarios())
    
    def validar_cpf_formato(self, cpf):
        return bool(re.match(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$", cpf))
    
    def validar_login(self, cpf, senha):
        usuario = self.buscar_por_cpf(cpf)
        if usuario and check_password_hash(usuario["senha"], senha):
            return usuario
        return None
