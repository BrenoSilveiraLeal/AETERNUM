# Estado de implementação

## Entregue

- AURION é o único agente ativo inicial; agentes antigos permanecem arquivados.
- O modo de operação está travado em `PAPER`; não há execução de ordens reais.
- O painel e o chat usam estados vazios quando não existe fonte verificável.
- O adaptador de mercado usa Dados de Mercado somente com credencial no servidor.
- Existem adaptadores oficiais catalogados para Banco Central SGS, IBGE SIDRA e CVM.
- Posições, ordens simuladas, mensagens e auditoria possuem persistência SQLAlchemy.
- O banco possui migração Alembic inicial e pode usar SQLite local ou PostgreSQL por `POSTGRES_URL`.
- Cada requisição recebe `x-request-id`; criação de ordem PAPER e conversa do AURION deixam registro de auditoria.
- Novos agentes são registrados como propostas e só entram no ecossistema após aprovação explícita.
- Ordens PAPER podem ser executadas/reconciliadas apenas quando existe uma cotação persistida e verificável.

## Dependências externas ainda necessárias

- Credencial válida do provedor de mercado para preencher cotações e histórico reais.
- Credencial e configuração do provedor de IA para respostas geradas; sem isso o chat informa a indisponibilidade.
- Integração Open Finance homologada, com OAuth/consentimento e instituição participante; senhas bancárias nunca são aceitas.
- Contrato/licença B3, quando a fonte licenciada for necessária.
- Serviço autorizado de notícias, caso o módulo de eventos seja ativado.

Essas dependências não podem ser simuladas com números, notícias ou patrimônio inventados.

## Verificação local

```powershell
python -m alembic -c backend/alembic.ini upgrade head
pytest -q
cd frontend
npm run build
```

## Radar de notÃ­cias

- CatÃ¡logo de fontes oficiais e endpoints de eventos/sincronizaÃ§Ã£o foram adicionados.
- A sincronizaÃ§Ã£o via NewsAPI Ã© opcional e exige `NEWS_PROVIDER=newsapi` e `NEWS_API_KEY` no backend.
- Eventos guardam fonte, URL e horÃ¡rio; impacto financeiro permanece como cenÃ¡rio, nunca previsÃ£o garantida.
