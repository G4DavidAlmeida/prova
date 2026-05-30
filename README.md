# FastAPI NoSQL Demo (Redis, MongoDB, Cassandra, Neo4j)

Demo academica para a disciplina de banco de dados nao relacional.

## Objetivo

Servidor FastAPI que implementa as 4 tarefas da plataforma de inteligencia de mercado:

1. Redis para cotacao atual com baixa latencia (cache hit/miss).
2. MongoDB para Data Lake com payload bruto e data_coleta.
3. Cassandra para serie temporal por moeda.
4. Neo4j para rede de investidores e consulta de alertas.

A API utilizada e a de mercado tradicional da AwesomeAPI:

- https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL

## Estrutura

- app/core: settings e logging
- app/db: conectores separados por banco
- app/services: provedor de mercado, ingestao, scheduler e seed com Faker
- app/api: rotas FastAPI
- tests/integration: testes de integracao com reset simples das bases

## Requisitos

- Python 3.11+
- uv - https://docs.astral.sh/uv/getting-started/installation/
- Docker + Docker Compose

## Subir bancos

```bash
docker compose up -d
```

## Ambiente Python com uv

```bash
uv venv
source .venv/bin/activate
uv sync
```

Opcional para compatibilidade com o enunciado:

```bash
uv pip install -r requirements.txt
```

## Rodar servidor FastAPI

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Swagger e teste da api:

- http://localhost:8000/docs

## Endpoints principais

- GET /saude
- POST /monitoramento/executar-ciclo
- GET /tarefa-1/cache/{simbolo}
- GET /tarefa-2/datalake/ultimos?simbolo=USD-BRL&limite=10
- GET /tarefa-3/serie-temporal/ultimos?simbolo=USD-BRL&limite=10
- GET /tarefa-4/alertas/{simbolo}

## Testes de integracao

Com os containers ativos:

```bash
uv run pytest tests/integration -v
```

### Reset de bases nos testes

- Redis: flushdb
- MongoDB: drop da collection
- Cassandra: truncate da tabela
- Neo4j: limpeza dos nos e relacionamentos de alerta

## Variaveis de ambiente

Copie .env.example para .env e ajuste se necessario.

Valores default recomendados:

- POLL_INTERVAL_SECONDS=20
- REDIS_TTL_SECONDS=45

## Observacoes

- O loop de monitoramento roda automaticamente no startup do FastAPI (MONITOR_ENABLED=true).
- Para demonstracao controlada, use POST /monitoramento/executar-ciclo.
- O arquivo monitor.py existe para compatibilidade com o formato pedido no enunciado.
