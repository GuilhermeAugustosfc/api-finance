
class OperacaoModel:
    def __init__(self, db):
        self.collection = db["operacao"]

    def criar_operacao(self, operacao):
        # Insere um novo documento na coleção
        self.collection.insert_one(operacao)

    def buscar_operacao_por_id(self, operacao_id):
        # Busca um documento pelo ID
        return self.collection.find_one({"_id": operacao_id})

    def buscar_todas_operacoes(self):
        # Busca todos os documentos da coleção
        return self.collection.find()

    def atualizar_operacao(self, operacao_id, operacao_atualizada):
        # Atualiza um documento existente
        self.collection.update_one({"_id": operacao_id}, {"$set": operacao_atualizada})

    def deletar_operacao(self, operacao_id):
        # Remove um documento da coleção
        self.collection.delete_one({"_id": operacao_id})
