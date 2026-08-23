# Arquitetura AETERNUM

## Princípios

1. Sobrevivência financeira e preservação de capital vêm antes de retorno.
2. Agentes analisam e recomendam; nenhuma análise gera ordem diretamente.
3. PAPER é o único modo permitido durante o desenvolvimento.
4. Ações sensíveis exigem confirmação explícita, autenticação forte e auditoria.
5. Dados e inferências devem manter origem, timestamps e nível de confiança.

## Componentes

`frontend/` é uma interface web responsiva. `backend/app/` concentra domínio, API e persistência local. Workers serão processos separados quando o monitoramento contínuo for implementado; endpoints HTTP não conterão loops infinitos.

Fluxo futuro: Frontend → API → Orchestrator → Workers → providers → PostgreSQL/queue. O provider inicial de mercado é `DadosDeMercadoProvider`; seus dados só entram no produto quando há token, valor, timestamp e origem válidos.

## Estado atual

O backend usa SQLite por simplicidade local e SQLAlchemy. O seed idempotente cria AURION e sete agentes especializados como descendentes. `MarketDataProvider` é uma fronteira explícita: o provider atual é demo, atrasado e sinalizado na resposta; adapters oficiais serão adicionados somente com credenciais e licenças válidas. A carteira atual expõe posições PAPER demonstrativas, sem persistir ordens reais.

Criação de agentes-filhos exige pai existente, justificativa, objetivo, nome único e profundidade máxima. O Paper Broker valida ordens e grava apenas `SIMULATED`; não há caminho de execução real. O dashboard não possui valores de fallback: sem provider oficial ou conexão autorizada, responde com coleção vazia e mensagem de estado.

O seed é idempotente e cria apenas AURION. Agentes legados encontrados no banco são marcados como `ARCHIVED`, preservando histórico sem permanecerem ativos.

Avatares são assets individuais, catalogados no frontend e referenciados no agente por `avatar_path`/`avatar_index`. A primeira camada visual usa composição 2.5D com `mix-blend-mode: screen`, evitando cenários retangulares; WebGL fica opcional para a fase de múltiplos agentes.
