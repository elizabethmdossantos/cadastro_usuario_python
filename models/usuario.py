import uuid

class Usuario:

        def __init__(self, nome: str, cpf: str, email: str, idade: int, senha: str, perfil="comum"):
                self.id = str(uuid.uuid4())
                self.nome = nome
                self.cpf = cpf
                self.email = email
                self.idade = idade
                self.senha = senha
                self.perfil = perfil

        def eh_maior_de_idade(self):
                return self.idade >= 18
                
        def eh_admin(self):
                return self.perfil == "admin"
                
        def to_dict(self):
                return {
                        "id" :self.id,
                        "nome" : self.nome,
                        "cpf" : self.cpf,
                        "email" : self.email,
                        "idade" : self.idade,
                        "senha" : self.senha,
                        "perfil" : self.perfil
                }
        @classmethod
        def from_dict(cls, dados:dict) -> "Usuario":
                usuario = cls.__new__(cls)
                usuario.id = dados.get("id", str(uuid.uuid4()))
                usuario.nome = dados.get("nome", " ")
                usuario.cpf = dados.get("cpf", " ")
                usuario.email = dados.get("email", " ")
                usuario.idade = dados.get("idade", 0)
                usuario.perfil = dados.get("perfil", "comum")
                return usuario
        
        def __repr__(self) -> str:
                return f"<Usuario nome={self.nome} cpf={self.cpf} perfil={self.perfil}"
