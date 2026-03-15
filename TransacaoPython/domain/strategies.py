from abc import ABC, abstractmethod

class TransferenciaStrategy(ABC):
    """
    Interface base do Padrão Strategy para calcular taxas e condições 
    específicas de cada tipo de transação (ex: Pix, TED, DOC).
    Isso respeita o Open/Closed Principle do SOLID.
    """
    
    @abstractmethod
    def calcular_taxa(self, valor: float) -> float:
        """Retorna o valor da taxa que deve ser cobrado na origem."""
        raise NotImplementedError()

class PixStrategy(TransferenciaStrategy):
    """Estratégia para Pix: Transferências instantâneas e gratuitas."""
    def calcular_taxa(self, valor: float) -> float:
        return 0.0

class TEDStrategy(TransferenciaStrategy):
    """Estratégia para TED: Pode ter uma taxa fixa independente do valor."""
    def calcular_taxa(self, valor: float) -> float:
        return 5.0  # Exemplo de taxa fixa de R$ 5,00
