# TransacaoFinanceira (Refatorado em Python)
Case original para refatoração de C# para Python.

## Passos Implementados:
1. Trabalhamos a camada de **Exceções de Domínio** (`SaldoInsuficienteError` e `ContaNaoEncontradaError`) em `domain/exceptions.py`.
2. Refatoramos a solução para **Arquitetura Limpa (Clean Architecture)** separando o projeto com **DIP (Dependency Inversion)** em `use_cases`, e aplicamos o **Design Pattern Strategy** para cálculo de taxas e regras extenśiveis de transferência.
3. Tratamento seguro de concorrência com Múltiplos **Locks Granulares** de *threads* direto no repositório simulado de infraestrutura, prevenindo _Race Conditions_ e Deadlocks (pegando a trava na mesma ordem algorítmica por IDs ordenados sequencialmente no `use_case`).
4. Implementação de suíte de Testes Unitários com `pytest` e mock de interfaces para testar domínio e casos de uso isolados.
5. Código `100% Typado` (Type Hints estritas) e otimizado com `__slots__` para menor Footprint de Memória.

## Arquitetura e Estrutura de Pastas

O projeto foi reescrito seguindo os princípios da **Clean Architecture**, dividindo as responsabilidades em camadas concêntricas, onde a regra de negócio não depende de detalhes de infraestrutura.

```text
TransacaoPython/
├── domain/                  # Entidades centrais e regras de negócio puras
│   ├── entities.py          # Classes Account/Conta (ricas em comportamento)
│   ├── exceptions.py        # Exceções customizadas de domínio (ex: SaldoInsuficiente)
│   └── strategies.py        # Implementação do Design Pattern Strategy (Cálculo de Taxas)
├── infrastructure/          # Camada de adaptadores externos (Banco de dados, APIs)
│   └── repositories.py      # Repositório de Contas mockado em memória com controle de Concorrência (Locks)
├── use_cases/               # Casos de uso da aplicação (Orquestração de regras)
│   ├── interfaces.py        # Portas (Interfaces) que a infraestrutura deve implementar
│   └── transferencia.py     # Lógica central da transferência entre contas
├── main.py                  # Entrypoint: Configura dependências e Injeta nos casos de uso
├── test_transacao.py        # Suíte de testes automatizados com Pytest
└── README.md                # Documentação atual
```

## Padrões de Projeto e Princípios Utilizados

Durante a refatoração, aplicamos os seguintes padrões para garantir um código limpo, testável e manutenível:

1. **SOLID Principles:**
   * **S (Single Responsibility):** Cada classe possui um único motivo para mudar. (ex: O `RealizarTransferenciaUseCase` apenas orquestra, não calcula saldo nem acessa banco diretamente).
   * **O (Open/Closed):** O sistema está aberto para extensões, mas fechado para modificações. Isso foi garantido com a injeção do Design Pattern Strategy ao invés de usar vários blocos de `if/else` para cálculo de taxas.
   * **D (Dependency Inversion):** O *Use Case* depende apenas de abstrações (`IContaRepository`), permitindo plugar qualquer banco de dados real no futuro sem alterar o domínio.
2. **Design Patterns:**
   * **Strategy Pattern (GoF):** Utilizado para isolar a lógica de cálculo de taxa (como a taxa de um PIX ou TED).
   * **Repository Pattern:** Abstração da lógica de persistência e acesso a dados, facilitando a troca futura para um banco relacional ou NoSQL.
   * **Dependency Injection (DI):** Instanciamos as dependências concretas no `main.py` e injetamos nos *Use Cases*, promovendo baixo acoplamento.
3. **Domain-Driven Design (DDD) - Conceitos Básicos:**
   * **Entidades Ricas:** Diferente de modelos anêmicos, a classe `Conta` possui tanto estado quanto as regras para se autovalidar dinamicamente (métodos `debitar` e `creditar`).
   * **Design by Contract:** O sucesso e a falha de estado são validados por Exceções claras criadas na própria camada de Domínio (`exceptions.py`).

## Execução
O código foi refatorado utilizando as bibliotecas nativas de threading do Python (`ThreadPoolExecutor`), simulando o paralelismo original do C#.

O Ponto de log (IO) passou a usar o módulo embutido `logging` na formatação da saída desejada original (INFO).

```bash
# Executando a Aplicação Principal
python main.py

# Testes com TDD
pytest test_transacao.py -v
```

### Detalhe de Arquitetura Sênior (Threads C# vs. Python GIL)
*Nota de System Design:* Diferente do `.NET / C#` onde as requisições teriam threads OS puras, o ecossistema CPython possui o **Global Interpreter Lock**. A escolha do `ThreadPoolExecutor(max_workers=8)` aqui, aliada aos locks de transações granulares (`conta_id`), serve para emular perfeitamente que essa aplicação será *IO-Bound* num cenário real (a operação da transação chamaria um bando de dados como Postgres via I/O Wait). Portanto, usar threads na orquestração é totalmente produtivo em Python, contanto que o código no repositório de dados cuide das travas contra _race conditions_. O uso de *AsyncIO* não foi incluído para manter total similaridade assíncrona com o desafio via *Parallel.ForEach* clássico, com menos refatoração imperativa.

### Visão de Futuro e Escalabilidade (O Cenário de um Grande Banco)
Para um sistema financeiro de grande porte (como Nubank ou Itaú) processando milhares de transações por segundo, o modelo de processamento e controle de concorrência em memória seria um gargalo. A evolução arquitetural ideal para essa base de código (beneficiada por estar em *Clean Architecture*) seria:

1. **Microsserviços e Mensageria (Event-Driven):** Enfileirar requisições de transferência em tópicos de **Apache Kafka** ou **RabbitMQ** ao invés de processá-las em tempo real no servidor principal.
2. **Workers Assíncronos:** Centenas de workers consumidores rodando assincronamente (ex: Celery + AsyncIO) puxariam eventos da fila para aplicar as regras de negócio de domínio sem gargalo.
3. **Delegação de Locks para Banco Relacional:** A trava lógica na memória (`self.repository.acquire_lock`) daria lugar a um *Locking Pessimista* gerenciado nativamente pelo banco de dados relacional (ex: `SELECT ... FOR UPDATE` no PostgreSQL), garantindo obediência estrita ACID transacional.
4. **Idempotência Garantida:** A presença do `correlation_id` (processado via chaves únicas no DB) preveniria reexecução da mesma transação em cenários de retry por falha de rede.
