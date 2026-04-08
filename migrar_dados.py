import json
from models.repositorio import RepositorioUsuarios
from models.usuario import Usuario

def migrar_dados():
    try:
        with open('usuarios.json', 'r', encoding='utf-8') as f:
            dados_json = json.load(f)
    except FileNotFoundError:
        print("Arquivo usuarios.json não encontrado")
        return
    
    repo = RepositorioUsuarios

    for dados_usuario in dados_json:
        usuario = Usuario.from.dict(dados_usuario)
        if repo.salvar(usuario):
            print(f"Usuario {usuario.nome} migrado com sucesso")
        else:
            print(f"Erro ao migrar usuário {usuario.nome}")

        print("Migração concluída!")

    if __name__ == "__main__":
        migrar_dados()