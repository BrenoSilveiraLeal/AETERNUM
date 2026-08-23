# AETERNUM

Plataforma modular de inteligência financeira, análise quantitativa e agentes especializados. A primeira versão opera exclusivamente em `PAPER` e não executa ordens ou pagamentos reais.

## Regra de veracidade

O produto não preenche saldo, patrimônio, cotação, lucro, posição ou gráfico com números demonstrativos. Sem uma fonte oficial configurada, a interface mostra `Dados indisponíveis` ou `Integração ainda não configurada`. O modo operacional permanece `PAPER`.

## Primeiro slice

- API FastAPI em `backend/`;
- SQLite local para desenvolvimento;
- entidade `Agent` e seed do agente fundador AURION;
- constelação inicial de agentes especializados;
- AURION como único agente inicial; novos agentes dependem de proposta e autorização;
- carteira PAPER separada, inicialmente vazia;
- contrato `MarketDataProvider` com sinalização de DEMO DATA;
- frontend Next.js em `frontend/`;
- dashboard inicial com estado de sobrevivência, alocação e série histórica demonstrativa.

## Desenvolvimento

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --app-dir backend

cd frontend
npm install
npm run dev
```

O frontend usa `NEXT_PUBLIC_API_URL` (padrão `http://localhost:8000`).

Configuração: copie `.env.example` para `.env` no backend. Providers oficiais permanecem `NOT_CONFIGURED` até credenciais, documentação e autorização serem fornecidas. O endpoint `/api/paper/orders` apenas registra ordens simuladas quando uma ordem é criada explicitamente.

O relógio da interface usa `America/Sao_Paulo`; timestamps persistidos no backend devem permanecer em UTC e ser convertidos apenas na apresentação.

Os avatares fornecidos estão catalogados em `frontend/app/agentAvatars.ts` e armazenados individualmente em `frontend/public/avatars/`. A primeira integração usa composição `screen` para neutralizar visualmente os fundos escuros; a migração para PNG/WebP com alpha real permanece uma etapa de otimização de arte.

## Segurança

`TRADING_MODE` permanece `PAPER` por padrão. Segredos devem ficar no ambiente do servidor; nunca no frontend ou no repositório.

Consulte [ARCHITECTURE.md](ARCHITECTURE.md) e [ROADMAP.md](ROADMAP.md) para contexto e próximos passos.
