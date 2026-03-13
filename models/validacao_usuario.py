import re

class ValidacaoCadastro:

    def __init__(self, form_data, usuarios):
        self.dados = form_data
        self.usuarios = usuarios
        self.erros = []

    def validar(self):
        self._validar_idade()
        self._validar_cpf()
        self._validar_unicidade() #criterios do cpf

        return len(self.erros) == 0
    
    def _validar_idade(self):
        try:
            idade = int(self.dados.get("idade", 0 ))

            if idade < 18:
                self.erros.append("Usuário deve ter mais que 18 anos.")

        except:
            self.erros.append("Idade Inválida.")

    def _validar_cpf(self):

        cpf = self.dados("cpf", "")

        padrao = r"^\d{3}\.\d{3}.\d{3}\.-\d{2}"

        if not re.match(padrao, cpf):
            self.erros.append("CPF inválido. Use o formato 000.000.000-00.")

    def _validar_unicidade(self):
        cpf = re.seb(r"[.\-]", "", self.dados.get("cpf", ""))

        for usuario in self.usuarios:

            cpf_salvo = re.seb(r"[.\-]", "", self.dados.get("cpf", ""))

            if cpf_salvo == cpf:
                self.erros.append("CPF já cadastrado.")
                break