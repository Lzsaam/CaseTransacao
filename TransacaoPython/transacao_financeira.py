import threading
from concurrent.futures import ThreadPoolExecutor

class ContasSaldo:
    def __init__(self, conta, valor):
        self.conta = conta
        self.saldo = float(valor)

class AcessoDados:
    def __init__(self):
        self.tabela_saldos = [
            ContasSaldo(938485762, 180),
            ContasSaldo(347586970, 1200),
            ContasSaldo(2147483649, 0),
            ContasSaldo(675869708, 4900),
            ContasSaldo(238596054, 478),
            ContasSaldo(573659065, 787),
            ContasSaldo(210385733, 10),
            ContasSaldo(674038564, 400),
            ContasSaldo(563856300, 1200),
        ]
        self.saldos = {938485762: 180.0}
        
    def get_saldo(self, id):
        for c in self.tabela_saldos:
            if c.conta == id:
                return c
        return None
        
    def atualizar(self, dado):
        try:
            self.tabela_saldos = [x for x in self.tabela_saldos if x.conta != dado.conta]
            self.tabela_saldos.append(dado)
            return True
        except Exception as e:
            print(e)
            return False

class ExecutarTransacaoFinanceira(AcessoDados):
    def transferir(self, correlation_id, conta_origem, conta_destino, valor):
        conta_saldo_origem = self.get_saldo(conta_origem)
        
        # Simulando exatamente a lógica original onde saldos são checados sem verificar None, o que dá erro às vezes lá
        # mas aqui protegeremos parcialmente para focar na falha de negócio de saldo < valor.
        if conta_saldo_origem is None or conta_saldo_origem.saldo < valor:
            print(f"Transacao numero {correlation_id} foi cancelada por falta de saldo")
        else:
            conta_saldo_destino = self.get_saldo(conta_destino)
            if conta_saldo_destino is not None:
                conta_saldo_origem.saldo -= valor
                conta_saldo_destino.saldo += valor
                print(f"Transacao numero {correlation_id} foi efetivada com sucesso! Novos saldos: Conta Origem:{conta_saldo_origem.saldo} | Conta Destino: {conta_saldo_destino.saldo}")

def main():
    transacoes = [
        {"correlation_id": 1, "datetime": "09/09/2023 14:15:00", "conta_origem": 938485762, "conta_destino": 2147483649, "valor": 150},
        {"correlation_id": 2, "datetime": "09/09/2023 14:15:05", "conta_origem": 2147483649, "conta_destino": 210385733, "valor": 149},
        {"correlation_id": 3, "datetime": "09/09/2023 14:15:29", "conta_origem": 347586970, "conta_destino": 238596054, "valor": 1100},
        {"correlation_id": 4, "datetime": "09/09/2023 14:17:00", "conta_origem": 675869708, "conta_destino": 210385733, "valor": 5300},
        {"correlation_id": 5, "datetime": "09/09/2023 14:18:00", "conta_origem": 238596054, "conta_destino": 674038564, "valor": 1489},
        {"correlation_id": 6, "datetime": "09/09/2023 14:18:20", "conta_origem": 573659065, "conta_destino": 563856300, "valor": 49},
        {"correlation_id": 7, "datetime": "09/09/2023 14:19:00", "conta_origem": 938485762, "conta_destino": 2147483649, "valor": 44},
        {"correlation_id": 8, "datetime": "09/09/2023 14:19:01", "conta_origem": 573659065, "conta_destino": 675869708, "valor": 150},
    ]

    executor = ExecutarTransacaoFinanceira()
    
    # ThreadPoolExecutor com várias threads simula o Parallel.ForEach e os bugs de concorrência
    with ThreadPoolExecutor(max_workers=8) as pool:
        for item in transacoes:
            pool.submit(executor.transferir, item["correlation_id"], item["conta_origem"], item["conta_destino"], item["valor"])

if __name__ == "__main__":
    main()
