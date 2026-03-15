from domain.exceptions import ContaNaoEncontradaError, SaldoInsuficienteError
from domain.strategies import TransferenciaStrategy, PixStrategy
from use_cases.interfaces import IContaRepository

class RealizarTransferenciaUseCase:
    def __init__(self, repository: IContaRepository):
        self.repository = repository

    def executar(
        self, 
        correlation_id: int, 
        conta_origem_id: int, 
        conta_destino_id: int, 
        valor: float,
        strategy: TransferenciaStrategy = PixStrategy()
    ) -> tuple[float, float]:
        # 1. Adquire lock para evitar deadlocks e race conditions na leitura/escrita
        # O lock precisa ser sempre adquirido na mesma ordem (ex: menor ID primeiro)
        # para evitar deadlocks entre threads tentando transferir cruzado.
        id1, id2 = min(conta_origem_id, conta_destino_id), max(conta_origem_id, conta_destino_id)
        
        self.repository.acquire_lock(id1, id2)
        try:
            conta_origem = self.repository.buscar_por_id(conta_origem_id)
            if not conta_origem:
                raise ContaNaoEncontradaError(f"Transacao numero {correlation_id} falhou: Conta Origem não encontrada")

            # 2. Verifica taxa através da Strategy fornecida
            taxa_transacao = strategy.calcular_taxa(valor)
            valor_total_debito = valor + taxa_transacao

            # 3. Verifica saldo e tenta debitar (regra de negócio na entidade baseada no valor + taxa)
            if not conta_origem.debitar(valor_total_debito):
                raise SaldoInsuficienteError(f"Transacao numero {correlation_id} foi cancelada por falta de saldo")

            conta_destino = self.repository.buscar_por_id(conta_destino_id)
            if not conta_destino:
                raise ContaNaoEncontradaError(f"Transacao numero {correlation_id} falhou: Conta Destino não encontrada")

            # 3. Credita no destino
            conta_destino.creditar(valor)

            # 4. Atualiza os dados através da interface do repositório
            self.repository.atualizar(conta_origem)
            self.repository.atualizar(conta_destino)

            # Retornamos os saldos novos pra formatar lá na Application Layer / Adapters
            return conta_origem.saldo, conta_destino.saldo
        
        finally:
            self.repository.release_lock(id1, id2)
        
        raise RuntimeError("Unreachable")
