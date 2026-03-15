import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from concurrent.futures import ThreadPoolExecutor
from infrastructure.repositories import ContaRepositoryInMemory
from use_cases.transferencia import RealizarTransferenciaUseCase
from domain.exceptions import DomainException

from typing import Dict, Any

def setup_logging() -> None:
    """Configura o logger padrão da aplicação para exibição no console."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def processar_transacao(use_case: RealizarTransferenciaUseCase, tx: Dict[str, Any]) -> None:
    """
    Tenta executar a transferência bancária e captura Exceptions de Domínio
    esperadas, ou reporta de forma segura Exceptions Críticas imprevistas.
    """
    correlation_id = tx["correlation_id"]
    try:
        saldo_origem, saldo_destino = use_case.executar(
            correlation_id, 
            tx["conta_origem"], 
            tx["conta_destino"], 
            tx["valor"]
        )
        logging.info(f"Transacao numero {correlation_id} foi efetivada com sucesso! Novos saldos: Conta Origem:{saldo_origem} | Conta Destino: {saldo_destino}")
    except DomainException as e:
        # Pega qualquer erro de negócio (SaldoInsuficiente, ContaNaoEncontrada, etc)
        logging.info(str(e))
    except Exception as e:
        # Erros inesperados globais
        logging.error(f"Erro inesperado na transacao {correlation_id}: {e}")

def main():
    setup_logging()
    
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

    repository = ContaRepositoryInMemory()
    use_case = RealizarTransferenciaUseCase(repository)
    
    with ThreadPoolExecutor(max_workers=8) as pool:
        for item in transacoes:
            pool.submit(processar_transacao, use_case, item)

if __name__ == "__main__":
    main()
