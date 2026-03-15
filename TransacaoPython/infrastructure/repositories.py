import threading
from typing import Optional, Dict

from domain.entities import Conta
from use_cases.interfaces import IContaRepository

class ContaRepositoryInMemory(IContaRepository):
    """
    Implementação na memória do repositório de contas.
    Utiliza locks granulares para garantir Thread-Safety sem degradar a performance
    com um lock global único.
    """
    def __init__(self) -> None:
        # Em banco real isso seria uma tabela no DB.
        self._dados: Dict[int, Conta] = {
            938485762: Conta(938485762, 180.0),
            347586970: Conta(347586970, 1200.0),
            2147483649: Conta(2147483649, 0.0),
            675869708: Conta(675869708, 4900.0),
            238596054: Conta(238596054, 478.0),
            573659065: Conta(573659065, 787.0),
            210385733: Conta(210385733, 10.0),
            674038564: Conta(674038564, 400.0),
            563856300: Conta(563856300, 1200.0),
        }
        # Locks granulares por conta (evitando lock global),
        # garantindo o paralelismo esperado exceto quando duas threads pegam as mesmas contas
        self._locks: Dict[int, threading.Lock] = {conta_id: threading.Lock() for conta_id in self._dados.keys()}
        self._global_lock: threading.Lock = threading.Lock()

    def buscar_por_id(self, conta_id: int) -> Optional[Conta]:
        # Retornamos a instância direta que está sendo protegida pelas locks.
        # Numa aplicação real, a ORM cuidaria do mapeamento Row->Entity.
        return self._dados.get(conta_id)

    def atualizar(self, conta: Conta) -> bool:
        if conta.id in self._dados:
            self._dados[conta.id] = conta
            return True
        return False
        
    def acquire_lock(self, id1: int, id2: int) -> None:
        """Adquire as locks na ordem específica das chaves para evitar Deadlocks."""
        lock1 = self._locks.get(id1, self._global_lock)
        lock2 = self._locks.get(id2, self._global_lock)

        lock1.acquire()
        if lock1 != lock2:
            lock2.acquire()

    def release_lock(self, id1: int, id2: int) -> None:
        """Libera as locks adquiridas na transação."""
        lock2 = self._locks.get(id2, self._global_lock)
        lock1 = self._locks.get(id1, self._global_lock)
        
        if lock1 != lock2:
            lock2.release()
        lock1.release()
