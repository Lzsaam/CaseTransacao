from dataclasses import dataclass

@dataclass(slots=True)
class Conta:
    """
    Entidade de Domínio representando a Conta Bancária.
    Utiliza __slots__ (via slots=True no Python 3.10+) para otimização extrema de memória,
    impedindo a criação dinâmica do __dict__ para cada instância.
    """
    id: int
    saldo: float

    def debitar(self, valor: float) -> bool:
        """
        Tenta realizar o débito na conta aplicando a regra de negócio de não permitir
        saques maiores que o saldo ou valores zerados/negativos.
        """
        if valor <= 0:
            return False
        
        # Uso consciente de float puro - em aplicações maduras (fintechs),
        # preferimos 'decimal.Decimal' ao em vez de float para evitar bugs de arredondamento IEEE 754.
        if self.saldo >= valor:
            self.saldo -= valor
            return True
        return False

    def creditar(self, valor: float) -> None:
        """
        Realiza o crédito na conta para valores válidos.
        """
        if valor > 0:
            self.saldo += valor
