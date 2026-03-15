class DomainException(Exception):
    """Classe base para todas as exceções de domínio."""
    pass

class ContaNaoEncontradaError(DomainException):
    """Lançada quando uma conta origem ou destino não é encontrada."""
    pass

class SaldoInsuficienteError(DomainException):
    """Lançada quando a conta origem não possui saldo suficiente para a transação."""
    pass
