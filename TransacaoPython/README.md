# TransacaoFinanceira (Refatorado em Python)
Case original para refatoração de C# para Python.

## Passos Implementados:
1. Trabalhamos a camada de **Exceções de Domínio** (`SaldoInsuficienteError` e `ContaNaoEncontradaError`) em `domain/exceptions.py`.
2. Refatoramos a solução para **Arquitetura Limpa (Clean Architecture)** separando o projeto com **DIP (Dependency Inversion)** em `use_cases`.
3. Tratamento seguro de concorrência com Múltiplos **Locks Granulares** de *threads* direto no repositório simulado de infraestrutura, prevenindo _Race Conditions_ e Deadlocks (pegando a trava na mesma ordem algorítmica por IDs ordenados sequencialmente no `use_case`).
4. Implementação de suíte de Testes Unitários com `pytest` e mock de interfaces para testar domínio e casos de uso isolados.
5. Código `100% Typado` (Type Hints estritas) e otimizado com `__slots__` para menor Footprint de Memória.

## Execução
O código foi refatorado utilizando as bibliotecas nativas de threading do Python (`ThreadPoolExecutor`), simulando o paralelismo original do C#.

O Ponto de log (IO) passou a usar o módulo embutido `logging` na formatação da saída desejada original (INFO).

```bash
# Executando a Aplicação Principal
python main.py

# Testes com TDD
pytest test_transacao.py -v
```

### Threads C# vs. Python GIL
*Nota de System Design:* Diferente do `.NET / C#` onde as requisições teriam threads OS puras, o ecossistema CPython possui o **Global Interpreter Lock**. A escolha do `ThreadPoolExecutor(max_workers=8)` aqui, aliada aos locks de transações granulares (`conta_id`), serve para emular perfeitamente que essa aplicação será *IO-Bound* num cenário real (a operação da transação chamaria um bando de dados como Postgres via I/O Wait). Portanto, usar threads na orquestração é totalmente produtivo em Python, contanto que o código no repositório de dados cuide das travas contra _race conditions_. O uso de *AsyncIO* não foi incluído para manter total similaridade assíncrona com o desafio via *Parallel.ForEach* clássico, com menos refatoração imperativa.
