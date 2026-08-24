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
- [x] Remover fallbacks numéricos e exibir estados vazios verificáveis
- [x] Preparar catálogo de fontes B3, Banco Central e IBGE
- [x] Seed inicial reduzido a AURION; agentes antigos são arquivados
- [x] Relógio real no fuso America/Sao_Paulo
- [x] Ecossistema visual com holograma dedicado à AURION
- [x] Catalogar oito avatares individuais fornecidos
- [x] Integrar avatar da AURION com fallback 2.5D responsivo
- [ ] Extrair alpha real e migrar assets para WebP otimizado
- [ ] Adicionar cena Three.js/React Three Fiber quando houver necessidade de múltiplos agentes ativos
- [ ] Conectar provider oficial com credenciais server-side

## Próximas fatias

- [x] Criar posições de carteira PAPER e endpoint de portfólio
- [x] Adicionar Paper Broker mínimo com ordens simuladas
- [x] Adicionar criação segura de agentes-filhos com limites e auditoria de relação
- [x] Criar configuração `.env.example` sem secrets
- [ ] CapitalAllocation, Portfolio persistente e Survival/Risk
- [ ] TechnicalAnalysis e Backtesting com validação out-of-sample
- [ ] Command Center read-only e audit log
- [ ] Paper broker, workers e reconciliação
- [ ] News/ImpactGraph, consenso multiagente e Agent Factory
- [ ] PWA, deploy cloud e hardening de segurança

> LIVE, PIX, saques reais e movimentação financeira permanecem desativados até existir uma revisão e autorização explícitas.
## MetaTrader 5 / Rico

- [x] Criar ponte opcional em modo somente leitura
- [x] Adicionar proteÃ§Ãµes PAPER/DEMO e status seguro no dashboard
- [x] Preparar `MetaTraderMarketDataProvider`
- [x] Criar sinais persistidos, alocaÃ§Ãµes internas e RiskManager
- [x] Criar ExecutionEngine PAPER com bloqueio de cotaÃ§Ã£o e auditoria
- [x] Criar diagnÃ³stico local `python -m app.tools.mt5_doctor`
- [ ] Validar conta demo Rico localmente e mapear sÃ­mbolos B3
- [ ] Criar RiskManager + ExecutionEngine antes de qualquer ordem demo
## Hardening do nÃºcleo

- [x] Injetar `BrokerAdapter` no ExecutionEngine
- [x] Adicionar reserva configurÃ¡vel e endpoint de alocaÃ§Ãµes
- [ ] Implementar reconciliaÃ§Ã£o PAPER/DEMO e idempotÃªncia de execuÃ§Ã£o
- [ ] Implementar autenticaÃ§Ã£o forte e aprovaÃ§Ã£o operacional para habilitar DEMO
- [ ] Somente depois: revisÃ£o independente para eventual trading real
