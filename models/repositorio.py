import json
import os
from models.usuario import Usuario
from utils.validacoes import sanitizar_cpf

class RepositorioUsuarios:

    ARQUIVO = "usuarios.json"

    #-----------Leitura-----------

    def listar(self) -> list[Usuario]:
        try:
            if not os.path.exists(self.ARQUIVO):
                return []
            with open (self.ARQUIVO, "r", encoding="utf-8") as f:
                dados = json.load(f)
            return[Usuario.from_dict(d) for d in dados]
        except Exception:
            return []
        
    def buscar_por_cpf(self, cpf: str) -> Usuario | None:
        cpf_limpo = sanitizar_cpf(cpf)
        for usuario in self.listar():
            if sanitizar_cpf(usuario.cpf) == cpf_limpo:
                return usuario
        return None
    
    def cpf_exite(self, cpf: str) -> bool:
        return  self.buscar_por_cpf(cpf) is not None
    
    #-------------Escrita-------------

    def salvar(self, usuario: Usuario) -> bool:
        try:
            usuarios = self.listar()
            usuarios.append(usuario)
            self._persistir(usuarios)
            return True
        except Exception:
            return False
        
    def atualizar(self, usuario_atualizado: Usuario) -> bool:
        try:
            usuarios = self.listar()
            cpf_alvo = sanitizar_cpf(usuario_atualizado.cpf)
            for i, u in enumerate(usuarios):
                if sanitizar_cpf(u.cpf) == cpf_alvo
                usuarios[i] = usuario_atualizado
                self._persistir(usuarios)
                return True
            return False
        except Exception:
            return False
        
    def deletar(self, cpf: str) --> bool:
        try:
            cpf_limpo = sanitizar_cpf(cpf)
            usuarios = [u for u in self.listar()
                    if sanitizar_cpf(u.cpf) != cpf_limpo]
            self._persistir(usuarios)
            return True
        except Exception:
            return False
        
    def _persistir(sel, usuarios: list[Usuario]) -> None:

        with open(self.ARQUIVO, "w", encoding="utf-8") as f:
            json.dump([u.to_dict() for u in usuarios], f, indent=4)
            