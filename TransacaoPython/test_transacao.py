import sys
import os
import threading
import pytest

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from domain.entities import Conta
from domain.exceptions import SaldoInsuficienteError, ContaNaoEncontradaError
from use_cases.transferencia import RealizarTransferenciaUseCase
from use_cases.interfaces import IContaRepository

class MockContaRepository(IContaRepository):
    def __init__(self, contas):
        self._dados = contas
        self._lock = threading.Lock()

    def buscar_por_id(self, id: int):
        return self._dados.get(id)

    def atualizar(self, conta: Conta) -> bool:
        if conta.id in self._dados:
            self._dados[conta.id] = conta
            return True
        return False
        
    def acquire_lock(self, id1: int, id2: int):
        self._lock.acquire()

    def release_lock(self, id1: int, id2: int):
        self._lock.release()

def test_conta_debitar_sucesso():
    conta = Conta(1, 100.0)
    assert conta.debitar(50.0) is True
    assert conta.saldo == 50.0

def test_conta_debitar_falha_saldo_insuficiente():
    conta = Conta(1, 100.0)
    assert conta.debitar(150.0) is False
    assert conta.saldo == 100.0

def test_conta_debitar_falha_valor_invalido():
    conta = Conta(1, 100.0)
    assert conta.debitar(-10.0) is False
    assert conta.saldo == 100.0

def test_conta_creditar_sucesso():
    conta = Conta(1, 100.0)
    conta.creditar(50.0)
    assert conta.saldo == 150.0

def test_transferencia_sucesso():
    repositorio = MockContaRepository({
        1: Conta(1, 100.0),
        2: Conta(2, 50.0)
    })
    use_case = RealizarTransferenciaUseCase(repositorio)
    
    saldo_origem, saldo_destino = use_case.executar(correlation_id=99, conta_origem_id=1, conta_destino_id=2, valor=40.0)
    
    assert saldo_origem == 60.0
    assert saldo_destino == 90.0
    assert repositorio.buscar_por_id(1).saldo == 60.0
    assert repositorio.buscar_por_id(2).saldo == 90.0

def test_transferencia_conta_origem_sem_saldo():
    repositorio = MockContaRepository({
        1: Conta(1, 10.0),
        2: Conta(2, 50.0)
    })
    use_case = RealizarTransferenciaUseCase(repositorio)
    
    with pytest.raises(SaldoInsuficienteError, match="cancelada por falta de saldo"):
        use_case.executar(correlation_id=100, conta_origem_id=1, conta_destino_id=2, valor=40.0)
    
    assert repositorio.buscar_por_id(1).saldo == 10.0
    assert repositorio.buscar_por_id(2).saldo == 50.0

def test_transferencia_conta_nao_encontrada():
    repositorio = MockContaRepository({
        1: Conta(1, 100.0)
    })
    use_case = RealizarTransferenciaUseCase(repositorio)
    
    with pytest.raises(ContaNaoEncontradaError, match="Conta Destino não encontrada"):
        use_case.executar(correlation_id=101, conta_origem_id=1, conta_destino_id=999, valor=40.0)
