class SessaoUsuario:

    def __init__(self, session):
        self._session = session

    def iniciar(self, usuario):
        self._session["usuario_id"] = usuario["id"]
        self._session["usuario_nome"] = usuario["nome"]
        self._session["usuario_perfil"] = usuario["perfil", "comum"]

    def encerrar(self):
        self._session.clear()

    def esta_logado(self):
        return "usuario_id" in self._session
    
    def eh_admin(self):
        return self._session.get("usuario_perfil") == "admin"
    
    def usuario_id(self):
        return self._session.get("usuario_id")