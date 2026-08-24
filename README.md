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
## MetaTrader 5 / Rico (fase PAPER/DEMO)

A integraÃ§Ã£o Ã© opcional e somente de leitura. O backend nÃ£o chama `order_send` e nÃ£o abre conta real. O endpoint `GET /api/broker/connection` nunca devolve senha e mascara o login.

### ConfiguraÃ§Ã£o local no Windows

1. Instale o MetaTrader 5 pelo acesso oficial disponibilizado pela Rico e abra o terminal.
2. No terminal, use **Arquivo > Abrir uma conta** ou **Arquivo > Login na conta de negociaÃ§Ã£o** e selecione uma conta de demonstraÃ§Ã£o. Confirme o servidor demo.
3. Abra **Exibir > ObservaÃ§Ã£o do Mercado**; clique com o botÃ£o direito e use **SÃ­mbolos** para habilitar os ativos.
4. Copie apenas o nÃºmero da conta demo e o nome exato do servidor.
5. Execute `pip install -r backend/requirements.txt` no ambiente virtual. O pacote oficial Ã© `MetaTrader5`, publicado pela MetaQuotes.
6. Copie `.env.example` para `.env`. Preencha `MT5_TERMINAL_PATH`, `MT5_LOGIN` e `MT5_SERVER`; deixe `MT5_PASSWORD` vazio se o terminal jÃ¡ salvou a sessÃ£o. Mantenha `TRADING_MODE=PAPER`, `MT5_DEMO_ONLY=true` e ajuste `MT5_ALLOWED_DEMO_SERVERS` para o servidor demo da Rico.
7. Inicie com `uvicorn app.main:app --reload --app-dir backend` e `cd frontend; npm run dev`.
8. Abra `http://localhost:3000`. O cartÃ£o **BROKER CONNECTION** deve mostrar `CONNECTED`, `PAPER / DEMO`, login mascarado e `AVAILABLE` em market data.

Se o MT5 estiver fechado, o login falhar ou a conta nÃ£o for reconhecida como demo, o dashboard mostrarÃ¡ `DISCONNECTED` sem derrubar o AETERNUM.

ReferÃªncia: [documentaÃ§Ã£o oficial Python Integration da MetaQuotes](https://www.mql5.com/en/docs/python_metatrader5).

### DiagnÃ³stico

Com o ambiente virtual ativo, execute dentro de `backend`:

```powershell
python -m app.tools.mt5_doctor
```

O comando nÃ£o exibe senha. CÃ³digo `0` significa terminal conectado e conta DEMO permitida; cÃ³digo `1` significa que ainda falta instalaÃ§Ã£o, configuraÃ§Ã£o ou conexÃ£o.
## Fluxo final de decisÃ£o

Agentes enviam sinais para `POST /api/signals`. Um sinal `BUY` ou `SELL` precisa de confianÃ§a, justificativa, tamanho, stop loss e take profit. O `RiskManager` verifica modo PAPER, validade, capital alocado, reserva, limite por posiÃ§Ã£o e posiÃ§Ã£o disponÃ­vel para vendas. Apenas o `ExecutionEngine` pode preparar a ordem atravÃ©s do `BrokerAdapter`.

Nesta etapa, o resultado Ã© sempre `PAPER_ORDER_PREPARED`; a ordem nÃ£o Ã© enviada ao MT5. O histÃ³rico pode ser consultado em `GET /api/executions`, os sinais em `GET /api/signals` e as alocaÃ§Ãµes em `GET /api/risk/allocations`.
