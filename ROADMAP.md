# Roadmap

## Fase 0 — Diagnóstico e arquitetura

- [x] Inspecionar workspace, Git, Python e Node
- [x] Registrar arquitetura e decisões de segurança
- [x] Criar estrutura mínima

## Fase 1/2 — Backend base e banco

- [x] Configurar FastAPI, SQLAlchemy e SQLite local
- [x] Criar entidade Agent e seed de AURION
- [x] Expor API de agentes e health check
- [x] Adicionar agentes especializados e linhagem inicial de AURION

## Fase 3 — Market data

- [x] Criar contrato inicial de histórico
- [x] Exibir gráfico demonstrativo no dashboard
- [x] Criar contrato `MarketDataProvider` e marcar dados demo
- [ ] Conectar provider oficial com credenciais server-side

## Próximas fatias

- [x] Criar posições de carteira PAPER e endpoint de portfólio
- [ ] CapitalAllocation, Portfolio persistente e Survival/Risk
- [ ] TechnicalAnalysis e Backtesting com validação out-of-sample
- [ ] Command Center read-only e audit log
- [ ] Paper broker, workers e reconciliação
- [ ] News/ImpactGraph, consenso multiagente e Agent Factory
- [ ] PWA, deploy cloud e hardening de segurança

> LIVE, PIX, saques reais e movimentação financeira permanecem desativados até existir uma revisão e autorização explícitas.
