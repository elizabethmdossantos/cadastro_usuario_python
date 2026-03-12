import uuid
from flask import session

class SessaoUsuario:

    def __init__(self, usuario_id, nome, perfil="comum"):
        self.id = str(uuid.uuid4())
        self.usuario_id = usuario_id
        self.nome = nome
        self.perfil = perfil
    
    def salvar_na_session(self):
        session['sessao_id'] = self.id
        session['usuario_id'] = self.usuario_id
        session['usuario_nome'] = self.nome
        session['usuario_perfil'] = self.perfil
        session.modified = True
    
    @classmethod
    def carregar_da_session(cls):
        if 'sessao_id' not in session:
            return None
        try:
            return cls(
                session['usuario_id'],
                session['usuario_nome'],
                session['usuario_perfil']
            )
        except KeyError:
            return None
    
    @classmethod
    def limpar_session(cls):
        session.clear()
