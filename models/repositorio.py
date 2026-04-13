import mysql.connector # conectar Python ao MySQL

from mysql.connector import Error # classe para capturar exceções de banco de dados
from models.usuario import Usuario 
from utils.validacoes import sanitizar_cpf

class RepositorioUsuarios:

    def __init__(self):
        # dicionário com as credenciais de acesso ao banco de dados
        # onde o banco está e como entrar nele
        self.connection_config = {
            'host': 'localhost',
            'user': 'mickey',
            'password': 'admin',
            'database': 'crud_flask'
        }

    def _get_connection(self):
        try:
            # tenta estabelecer a conexão usando o desempacotamento (**) do dicionário de configurações
            connection = mysql.connector.connect(**self.connection_config)
            return connection
        except Error as e:
            print(f"Erro ao conectar mysql {e}") # em caso de erro (não encontrar o banco)

    #-----------Leitura-----------
    def listar(self) -> list[Usuario]:
        connection = self._get_connection() # chama o método de conexão acima
        if not connection:
            return [] # se falhar retorna uma lista vazia
        
        try:
            cursor = connection.cursor(dictionary=True) # retorna as informações do banco organizadas em linhas e colunas
            cursor.execute("SELECT * FROM usuarios") # executa o comando sql
            rows = cursor.fetchall() # fetchall - recupera todos os registros encontrados
            return [Usuario.from_dict(row) for row in rows] 
        except Error as e:
            print(f"Erro ao listar usuários: {e}")
            return[]
        finally:
            if connection.is_connected():
                cursor.close() # fecha o cursor
                connection.close() # fecha a conexão com o servidor


    def buscar_por_cpf(self, cpf: str) -> Usuario | None:
        connection = self._get_connection()
        if not  connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cpf_limpo = sanitizar_cpf(cpf)
            cursor.execute("SELECT * FROM usuarios WHERE cpf = %s", (cpf_limpo))
            row = cursor.fetchone() # fetchone - unico
            return Usuario.from_dict(row) if row else None
        except Error as e:
            print(f"Erro ao buscar usuário pelo CPF {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def cpf_exite(self, cpf: str) -> bool: 
        return  self.buscar_por_cpf(cpf) is not None



    #-------------Escrita-------------
    def salvar(self, usuario: Usuario) -> bool:
        connection = self._get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            sql = """INSERT INTO usuarios (id, nome, cpf, email, idade, senha, perfil)
            VALUES(%s, %s, %s, %s, %s, %s, %s)"""
            valores = (
                usuario.id, 
                usuario.nome, 
                usuario.cpf, 
                usuario.email,
                usuario.idade, 
                usuario.senha, 
                usuario.perfil
                )
            cursor.execute(sql, valores)
            connection.commit()
            return True
        except Error as e:
            print(f"Error ao salvar usuário: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()



    def atualizar(self, usuario_atualizado: Usuario) -> bool:
        connection = self._get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            sql = """UPDATE usuarios SET nome=%s, cpf=%s, email=%s, idade=%s, senha=%s, perfil=%s
            WHERE cpf=%s """
            valores = (
                        usuario_atualizado.nome,
                        usuario_atualizado.cpf,
                        usuario_atualizado.email,
                        usuario_atualizado.idade,
                        usuario_atualizado.senha,
                        usuario_atualizado.perfil
                )
            cursor.execute(sql, valores)
            connection.commit()         
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error ao atualizar usuário: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


        
    def deletar(self, cpf: str) -> bool:
        connection = self._get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            cpf_limpo = sanitizar_cpf(cpf)
            cursor.execute("DELETE FROM usuarios WHERE cpf = %s", (cpf_limpo,))
            connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Erro ao deletar usuário: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
