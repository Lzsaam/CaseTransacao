from abc import ABC, abstractmethod
from typing import Optional
from domain.entities import Conta

class IContaRepository(ABC):
    """
    Interface (Porta) para acesso aos dados da Conta, seguindo o Princípio da Inversão de Dependência (DIP).
    """

    @abstractmethod
    def buscar_por_id(self, conta_id: int) -> Optional[Conta]:
        """Obtém uma conta pelo seu identificador único."""
        raise NotImplementedError()

    @abstractmethod
    def atualizar(self, conta: Conta) -> bool:
        """Persiste as alterações feitas na entidade Conta."""
        raise NotImplementedError()
    
    @abstractmethod
    def acquire_lock(self, id1: int, id2: int) -> None:
        """
        Adquire uma trava de concorrência para as duas contas envolvidas na transação.
        Garante que operações assíncronas não sobrescrevam saldos indevidamente (Race Conditions).
        """
        pass

    @abstractmethod
    def release_lock(self, id1: int, id2: int) -> None:
        """Libera a trava de concorrência das contas."""
        pass
