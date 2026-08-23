# AETERNUM

Plataforma modular de inteligência financeira, análise quantitativa e agentes especializados. A primeira versão opera exclusivamente em `PAPER` e não executa ordens ou pagamentos reais.

## Primeiro slice

- API FastAPI em `backend/`;
- SQLite local para desenvolvimento;
- entidade `Agent` e seed do agente fundador AURION;
- constelação inicial de agentes especializados;
- carteira PAPER com posições demonstrativas;
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

## Segurança

`TRADING_MODE` permanece `PAPER` por padrão. Segredos devem ficar no ambiente do servidor; nunca no frontend ou no repositório.

Consulte [ARCHITECTURE.md](ARCHITECTURE.md) e [ROADMAP.md](ROADMAP.md) para contexto e próximos passos.
