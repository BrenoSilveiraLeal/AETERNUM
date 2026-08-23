"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type Agent = {
  id?: number;
  unique_id: string;
  name: string;
  role: string;
  avatar?: string;
  specialization: string;
  status: string;
  generation?: number;
  created_at?: string;
};
type History = {
  data_status: string;
  points: { date: string; value: number }[];
};
type Chat = { role: "user" | "assistant"; content: string; time: string };
type WalletTransaction = { id: number; direction: string; amount: number; status: string; method: string; description: string; created_at: string };
type Wallet = { agent_name: string; currency: string; balance: number; status: string; pix_status: string; transactions: WalletTransaction[] };
type NewsEvent = { id: number; title: string; summary?: string; source: string; source_url: string; published_at?: string; event_type: string; confirmation_status: string; impact_status: string };
type MarketMarker = { kind: string; date: string; value: number; label: string; status: string };
type MarketChart = { symbol: string; source: string; data_status: string; delayed: boolean; points: { date: string; value: number }[]; markers: MarketMarker[] };

const api = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const watchlist = [
  { symbol: "PETR4", name: "Petrobras PN" },
  { symbol: "VALE3", name: "Vale ON" },
  { symbol: "ITUB4", name: "Itaú Unibanco" },
  { symbol: "AAPL", name: "Apple Inc." },
];

export default function Home() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [history, setHistory] = useState<History>();
  const [now, setNow] = useState(new Date(0));
  const [messages, setMessages] = useState<Chat[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [conversation, setConversation] = useState<string>();
  const [active, setActive] = useState("overview");
  const [modal, setModal] = useState<
    "connection" | "policy" | "order" | "proposal" | null
  >(null);
  const [selectedAsset, setSelectedAsset] = useState("PETR4");
  const [toast, setToast] = useState("");
  const [proposalBusy, setProposalBusy] = useState(false);
  const [wallet, setWallet] = useState<Wallet>();
  const [walletBusy, setWalletBusy] = useState(false);
  const [newsEvents, setNewsEvents] = useState<NewsEvent[]>([]);
  const [newsConfigured, setNewsConfigured] = useState(false);
  const [marketSymbol, setMarketSymbol] = useState("PETR4");
  const [marketChart, setMarketChart] = useState<MarketChart>();
  useEffect(() => {
    setNow(new Date());
    const clock = window.setInterval(() => setNow(new Date()), 1000);
    Promise.all([
      fetch(`${api}/api/agents`).then((r) => r.json()),
      fetch(`${api}/api/market/history`).then((r) => r.json()),
      fetch(`${api}/api/wallet/aurion`).then((r) => r.json()),
      fetch(`${api}/api/news/events`).then((r) => r.json()),
      fetch(`${api}/api/news/status`).then((r) => r.json()),
    ])
      .then(([a, h, w, n, ns]) => {
        setAgents(a);
        setHistory(h);
        setWallet(w);
        setNewsEvents(Array.isArray(n) ? n : []);
        setNewsConfigured(Boolean(ns.configured));
      })
      .catch(() => undefined);
    return () => window.clearInterval(clock);
  }, []);
  useEffect(() => {
    let cancelled = false;
    async function loadChart() {
      try {
        const response = await fetch(`${api}/api/market/chart/${encodeURIComponent(marketSymbol)}?days=3650`);
        const data = await response.json();
        if (!cancelled) setMarketChart(data);
      } catch {
        if (!cancelled) setMarketChart({ symbol: marketSymbol, source: "", data_status: "Fonte indisponível.", delayed: false, points: [], markers: [] });
      }
    }
    loadChart();
    const refresh = window.setInterval(loadChart, 30000);
    return () => { cancelled = true; window.clearInterval(refresh); };
  }, [marketSymbol]);
  const time = new Intl.DateTimeFormat("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    timeZone: "America/Sao_Paulo",
  }).format(now);
  const date = new Intl.DateTimeFormat("pt-BR", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    timeZone: "America/Sao_Paulo",
  }).format(now);
  async function send(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: text, time }]);
    setBusy(true);
    try {
      const r = await fetch(`${api}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, conversation_id: conversation }),
      });
      const data = await r.json();
      if (!r.ok)
        throw new Error(data.detail ?? "Não foi possível consultar a Aurion.");
      setConversation(data.conversation_id);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: data.message,
          time: data.display_time ?? time,
        },
      ]);
    } catch (error) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? error.message
              : "Serviço indisponível no momento.",
          time,
        },
      ]);
    } finally {
      setBusy(false);
    }
  }
  const commands = useMemo(
    () => [
      "Qual é o status de sobrevivência da Aurion?",
      "Mostre os sinais que precisam de fonte",
      "Simule uma ordem para PETR4",
    ],
    [],
  );
  const displayAgents = agents.length
    ? agents
    : [
        {
          name: "Aurion",
          role: "fundador",
          specialization: "Alocação de capital",
          status: "ativa",
          unique_id: "aurion",
        },
      ];
  function notify(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 3200);
  }
  function openOrder(symbol: string) {
    setSelectedAsset(symbol);
    setModal("order");
  }
  async function createDeposit(amount: number) {
    setWalletBusy(true);
    try {
      const response = await fetch(`${api}/api/wallet/aurion/deposit-intents`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ amount }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Não foi possível iniciar o depósito.");
      setWallet((current) => current ? { ...current, transactions: [{ id: data.id, direction: "CREDIT", amount: data.amount, status: data.status, method: "PIX", description: data.message, created_at: new Date().toISOString() }, ...current.transactions] } : current);
      notify(data.message);
    } catch (error) {
      notify(error instanceof Error ? error.message : "Não foi possível iniciar o depósito.");
    } finally {
      setWalletBusy(false);
    }
  }
  async function createWithdrawal(amount: number, pixKey: string) {
    setWalletBusy(true);
    try {
      const response = await fetch(`${api}/api/wallet/ecosystem/withdrawal-intents`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ amount, pix_key: pixKey }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Não foi possível solicitar a retirada.");
      setWallet((current) => current ? { ...current, transactions: [{ id: data.id, direction: "DEBIT", amount: data.amount, status: data.status, method: "PIX", description: data.message, created_at: new Date().toISOString() }, ...current.transactions] } : current);
      notify(data.message);
    } catch (error) {
      notify(error instanceof Error ? error.message : "Não foi possível solicitar a retirada.");
    } finally {
      setWalletBusy(false);
    }
  }
  async function syncNews() {
    try {
      const response = await fetch(`${api}/api/news/sync`, { method: "POST" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Não foi possível sincronizar notícias.");
      notify(`${data.inserted} novos eventos foram armazenados.`);
    } catch (error) {
      notify(error instanceof Error ? error.message : "Provedor de notícias indisponível.");
    }
  }
  async function proposeAgent(form: {
    name: string;
    role: string;
    specialization: string;
    objective: string;
    reason: string;
  }) {
    const founder = agents.find(
      (agent) => agent.name.toLowerCase() === "aurion",
    );
    if (!founder?.id) {
      notify("Aurion ainda não está sincronizada com o backend.");
      return;
    }
    setProposalBusy(true);
    try {
      const response = await fetch(
        `${api}/api/agents/${founder.id}/proposals`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...form, risk_level: "LOW" }),
        },
      );
      const data = await response.json();
      if (!response.ok)
        throw new Error(data.detail ?? "Não foi possível criar a proposta.");
      setModal(null);
      notify(`Proposta para ${data.name} criada e aguardando autorização.`);
    } catch (error) {
      notify(
        error instanceof Error
          ? error.message
          : "Não foi possível criar a proposta.",
      );
    } finally {
      setProposalBusy(false);
    }
  }
  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-symbol">✦</span>
          <span>AETERNUM</span>
          <small>OS 01</small>
        </div>
        <div className="sidebar-label">CENTRO DE COMANDO</div>
        <nav aria-label="Navegação principal">
          <NavItem
            active={active === "overview"}
            onClick={() => setActive("overview")}
            icon="⌂"
          >
            Visão geral
          </NavItem>
          <NavItem
            active={active === "market"}
            onClick={() => setActive("market")}
            icon="◒"
          >
            Mercado
          </NavItem>
          <NavItem
            active={active === "agents"}
            onClick={() => setActive("agents")}
            icon="✦"
          >
            Ecossistema <span className="nav-count">{agents.length || 1}</span>
          </NavItem>
          <NavItem
            active={active === "portfolio"}
            onClick={() => setActive("portfolio")}
            icon="▣"
          >
            Carteiras
          </NavItem>
          <NavItem
            active={active === "signals"}
            onClick={() => setActive("signals")}
            icon="⌁"
          >
            Sinais & notícias
          </NavItem>
        </nav>
        <div className="sidebar-bottom">
          <div className="paper-status">
            <span className="pulse" /> PAPER MODE <strong>ATIVO</strong>
            <p>Simulação protegida · sem ordens reais</p>
          </div>
          <button className="operator">
            <span className="operator-avatar">B</span>
            <span>
              <strong>Operador</strong>
              <small>conta local</small>
            </span>
            <span className="dots">•••</span>
          </button>
        </div>
      </aside>
      <section className="workspace">
        <header className="topbar">
          <div>
            <div className="breadcrumb">
              AETERNUM <span>/</span>{" "}
              {active === "overview" ? "VISÃO GERAL" : active.toUpperCase()}
            </div>
            <h1>
              {active === "overview" ? (
                <>
                  Bom dia, <em>operador.</em>
                </>
              ) : active === "agents" ? (
                "Ecossistema de inteligências"
              ) : active === "portfolio" ? (
                "Carteiras e alocações"
              ) : active === "market" ? (
                "Terminal de mercado"
              ) : (
                "Sinais e notícias"
              )}
            </h1>
            <p className="subline">
              {date} <span>·</span> <b>{time}</b> <span>·</span> São Paulo
            </p>
          </div>
          <div className="top-actions">
            <span className="connection">
              <i /> Ambiente local
            </span>
            <button
              className="icon-btn"
              aria-label="Notificações"
              onClick={() => notify("Nenhuma notificação pendente.")}
            >
              ♧<i />
            </button>
            <button className="help-btn" onClick={() => setModal("policy")}>
              ?
            </button>
          </div>
        </header>
        <div className="integrity-banner">
          <span className="shield">✓</span>
          <div>
            <strong>Ambiente protegido</strong>
            <span>
              AETERNUM opera em PAPER. Saldos, cotações e sinais só aparecem
              quando uma fonte verificável estiver conectada.
            </span>
          </div>
          <button onClick={() => setModal("policy")}>
            Ver política de dados <span>↗</span>
          </button>
        </div>
        {active === "overview" ? (
          <Overview
            agents={displayAgents}
            history={history}
            onNavigate={setActive}
            onConnection={() => setModal("connection")}
            onOrder={openOrder}
          />
        ) : (
          <DetailView
            active={active}
            agents={displayAgents}
            dataReady={Boolean(history?.points?.length)}
            onBack={() => setActive("overview")}
            onConnection={() => setModal("connection")}
            onOrder={openOrder}
            onPropose={() => setModal("proposal")}
            wallet={wallet}
            walletBusy={walletBusy}
            onDeposit={createDeposit}
            onWithdraw={createWithdrawal}
            newsEvents={newsEvents}
            newsConfigured={newsConfigured}
            onNewsSync={syncNews}
            marketSymbol={marketSymbol}
            marketChart={marketChart}
            onMarketSymbol={setMarketSymbol}
          />
        )}
      </section>
      {false && <aside className="command-panel">
        <div className="command-top">
          <div className="command-title">
            <span className="aurion-mini">✦</span>
            <span>
              <b>AURION</b>
              <small>INTERFACE DE COMANDO</small>
            </span>
          </div>
          <span className="live-tag">
            <i /> AO VIVO
          </span>
        </div>
        <div className="command-intro">
          <span className="message-orb">✦</span>
          <div>
            <b>
              AURION <span>· agora</span>
            </b>
            <p>
              Estou observando o sistema. Pergunte sobre sobrevivência, sinais
              ou prepare uma simulação.
            </p>
          </div>
        </div>
        <div className="suggestions">
          {commands.map((c) => (
            <button key={c} onClick={() => setInput(c)}>
              {c}
              <span>↗</span>
            </button>
          ))}
        </div>
        <div className="messages">
          {messages.map((m, i) => (
            <div className={`chat-message ${m.role}`} key={`${m.time}-${i}`}>
              <span className="chat-label">
                {m.role === "user" ? "VOCÊ" : "AURION"} · {m.time}
              </span>
              <p>{m.content}</p>
            </div>
          ))}
          {busy && (
            <div className="chat-message assistant">
              <span className="chat-label">AURION · processando</span>
              <p className="typing">•••</p>
            </div>
          )}
        </div>
        <form className="command-composer" onSubmit={send}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            aria-label="Comando para Aurion"
            placeholder="Escreva um comando para Aurion…"
            disabled={busy}
          />
          <button disabled={busy || !input.trim()} aria-label="Enviar comando">
            ↑
          </button>
          <small>
            Enter para enviar · comandos financeiros exigem confirmação
          </small>
        </form>
      </aside>}
      {modal && (
        <Modal
          type={modal}
          asset={selectedAsset}
          busy={proposalBusy}
          onClose={() => setModal(null)}
          onConnection={() =>
            notify("Conexão segura: aguardando credenciais do provedor.")
          }
          onOrder={() => {
            setModal(null);
            notify(`Simulação PAPER criada para ${selectedAsset}.`);
          }}
          onProposal={proposeAgent}
        />
      )}
      {toast && (
        <div className="toast" role="status">
          ✓ {toast}
        </div>
      )}
    </main>
  );
}

function Overview({
  agents,
  history,
  onNavigate,
  onConnection,
  onOrder,
}: {
  agents: Agent[];
  history?: History;
  onNavigate: (v: string) => void;
  onConnection: () => void;
  onOrder: (symbol: string) => void;
}) {
  return (
    <>
      <section className="hero-grid">
        <article className="survival-card panel-card">
          <div className="card-heading">
            <div>
              <span className="section-kicker">SAÚDE DO ECOSSISTEMA</span>
              <h2>Sobrevivência da Aurion</h2>
            </div>
            <span className="status-pill">
              <i /> OPERACIONAL
            </span>
          </div>
          <div className="survival-body">
            <div className="survival-orb">
              <div className="orb-ring ring-one" />
              <div className="orb-ring ring-two" />
              <span>✦</span>
            </div>
            <div className="survival-copy">
              <span className="label">SALDO DA CARTEIRA</span>
              <strong className="unknown">
                Dados
                <br />
                indisponíveis
              </strong>
              <p>
                Conecte uma origem financeira autorizada para acompanhar o
                gatilho de sobrevivência.
              </p>
              <button className="secondary-btn" onClick={onConnection}>
                Configurar conexão <span>→</span>
              </button>
            </div>
          </div>
          <div className="survival-footer">
            <span>
              <i className="dot lime" /> Regra vital: carteira acima de zero
            </span>
            <span>Última leitura: indisponível</span>
          </div>
        </article>
        <article className="aurion-card panel-card">
          <div className="section-kicker">AGENTE FUNDADOR</div>
          <div className="aurion-visual">
            <div className="orbit orbit-a" />
            <div className="orbit orbit-b" />
            <div className="core">
              <img src="/avatars/aurion.png" alt="" />
              <span>✦</span>
            </div>
          </div>
          <h2>Aurion</h2>
          <p className="role">
            Inteligência de alocação · <span>nível 01</span>
          </p>
          <div className="aurion-meta">
            <span>
              STATUS{" "}
              <b>
                <i /> ATIVA
              </b>
            </span>
            <span>
              IDADE <b>01 ciclo</b>
            </span>
          </div>
          <button className="ghost-btn" onClick={() => onNavigate("agents")}>
            Abrir perfil <span>↗</span>
          </button>
        </article>
      </section>
      <section className="metric-grid">
        <Metric
          label="PATRIMÔNIO TOTAL"
          value="—"
          detail="Aguardando conexão"
        />
        <Metric label="VARIAÇÃO 24H" value="—" detail="Sem cotações" />
        <Metric
          label="POSIÇÕES ATIVAS"
          value="0"
          detail="Nenhuma ordem registrada"
        />
        <Metric
          label="RISCO OPERACIONAL"
          value="baixo"
          detail="Modo protegido"
          accent="lime"
        />
      </section>
      <section className="content-grid">
        <article className="panel-card market-card">
          <div className="card-heading">
            <div>
              <span className="section-kicker">MONITOR DE MERCADO</span>
              <h2>Watchlist</h2>
            </div>
            <button className="text-btn" onClick={() => onNavigate("market")}>
              Abrir mercado <span>↗</span>
            </button>
          </div>
          <div className="table-head">
            <span>ATIVO</span>
            <span>ÚLTIMO</span>
            <span>VARIAÇÃO</span>
            <span>STATUS</span>
          </div>
          {watchlist.map((item) => (
            <button
              className="asset-row asset-button"
              key={item.symbol}
              onClick={() => onOrder(item.symbol)}
            >
              <span className="asset-name">
                <b>{item.symbol}</b>
                <small>{item.name}</small>
              </span>
              <strong className="unknown small-unknown">
                Dados indisponíveis
              </strong>
              <strong className="neutral">—</strong>
              <span className="data-state">
                <i /> Aguardando fonte
              </span>
            </button>
          ))}
          <div className="table-note">
            Clique em um ativo para preparar uma ordem PAPER. Dados reais entram
            após conectar um provedor.
          </div>
        </article>
        <article className="panel-card signals-card">
          <div className="card-heading">
            <div>
              <span className="section-kicker">CONTEXTO EXTERNO</span>
              <h2>Sinais monitorados</h2>
            </div>
            <span className="count-badge">0 NOVOS</span>
          </div>
          <div className="empty-state">
            <div className="empty-icon">⌁</div>
            <strong>Fontes de notícias offline</strong>
            <p>
              Política, macroeconomia, conflitos e eventos climáticos entram
              aqui após a conexão de provedores autorizados.
            </p>
            <button className="secondary-btn" onClick={onConnection}>
              Configurar fontes <span>→</span>
            </button>
          </div>
        </article>
      </section>
      <section className="agent-strip panel-card">
        <div className="card-heading">
          <div>
            <span className="section-kicker">CONSTELAÇÃO AETERNUM</span>
            <h2>Agentes em operação</h2>
          </div>
          <button className="text-btn" onClick={() => onNavigate("agents")}>
            Ver ecossistema <span>↗</span>
          </button>
        </div>
        <div className="agent-list">
          {agents.map((agent) => (
            <div className="agent-chip" key={agent.unique_id}>
              <span className="agent-chip-avatar">✦</span>
              <span>
                <b>{agent.name}</b>
                <small>
                  {agent.role} · {agent.status}
                </small>
              </span>
              <span className="agent-live">
                <i /> online
              </span>
            </div>
          ))}
        </div>
        <p className="footnote">
          A criação de novos agentes exige proposta, capital disponível e
          autorização explícita do operador.
        </p>
      </section>
    </>
  );
}

function NavItem({
  active,
  onClick,
  icon,
  children,
}: {
  active: boolean;
  onClick: () => void;
  icon: string;
  children: React.ReactNode;
}) {
  return (
    <button className={`nav-item ${active ? "active" : ""}`} onClick={onClick}>
      <span>{icon}</span>
      {children}
    </button>
  );
}
function Metric({
  label,
  value,
  detail,
  accent,
}: {
  label: string;
  value: string;
  detail: string;
  accent?: string;
}) {
  return (
    <article className="metric-card">
      <span className="section-kicker">{label}</span>
      <strong className={accent ?? ""}>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}
function DetailView({
  active,
  agents,
  dataReady,
  onBack,
  onConnection,
  onOrder,
  onPropose,
  wallet,
  walletBusy,
  onDeposit,
  onWithdraw,
  newsEvents,
  newsConfigured,
  onNewsSync,
  marketSymbol,
  marketChart,
  onMarketSymbol,
}: {
  active: string;
  agents: Agent[];
  dataReady: boolean;
  onBack: () => void;
  onConnection: () => void;
  onOrder: (symbol: string) => void;
  onPropose: () => void;
  wallet?: Wallet;
  walletBusy: boolean;
  onDeposit: (amount: number) => void;
  onWithdraw: (amount: number, pixKey: string) => void;
  newsEvents: NewsEvent[];
  newsConfigured: boolean;
  onNewsSync: () => void;
  marketSymbol: string;
  marketChart?: MarketChart;
  onMarketSymbol: (symbol: string) => void;
}) {
  const title =
    active === "agents"
      ? "Ecossistema de inteligências"
      : active === "portfolio"
        ? "Carteiras e alocações"
        : active === "market"
          ? "Terminal de mercado"
          : "Sinais e notícias";
  const desc =
    active === "agents"
      ? "A Aurion é o primeiro agente. Novas inteligências crescem por ciclos, nível e capital verificável."
      : active === "portfolio"
        ? "Uma visão consolidada do capital, posições e ordens previstas por agente."
        : active === "market"
          ? "Gráficos, ativos e pontos de entrada somente quando os provedores oficiais estiverem conectados."
          : "Contexto político, macroeconômico e eventos que podem alterar risco e preço.";
  return (
    <section className="detail-view">
      <button className="back-btn" onClick={onBack}>
        ← Voltar para visão geral
      </button>
      <div className="detail-title">
        <span className="section-kicker">
          AETERNUM / {active.toUpperCase()}
        </span>
        <h2>{title}</h2>
        <p>{desc}</p>
      </div>
      {active === "agents" ? (
        <EvolutionView agents={agents} onPropose={onPropose} />
      ) : active === "portfolio" ? (
        <UnifiedWalletView wallet={wallet} walletBusy={walletBusy} onDeposit={onDeposit} onWithdraw={onWithdraw} />
      ) : active === "signals" ? (
        <SignalsView events={newsEvents} configured={newsConfigured} onSync={onNewsSync} />
      ) : active === "market" ? (
        <MarketView symbol={marketSymbol} chart={marketChart ?? { symbol: marketSymbol, source: "", data_status: "Aguardando fonte de mercado.", delayed: false, points: [], markers: [] }} onSymbolChange={onMarketSymbol} onOrder={onOrder} />
      ) : (
        <div className="detail-grid">
          <article className="panel-card detail-main">
            <div className="empty-state large">
              <div className="empty-icon">
                {active === "market" ? "◒" : active === "portfolio" ? "▣" : "⌁"}
              </div>
              <strong>
                {dataReady
                  ? "Dados disponíveis"
                  : "Integração ainda não configurada"}
              </strong>
              <p>
                {dataReady
                  ? "A fonte retornou dados para este ambiente."
                  : "Para manter a veracidade do produto, esta área permanece vazia até que uma origem verificável seja conectada."}
              </p>
              <button className="secondary-btn" onClick={onConnection}>
                Configurar integração <span>→</span>
              </button>
              {active === "market" && (
                <button
                  className="secondary-btn secondary-spaced"
                  onClick={() => onOrder("PETR4")}
                >
                  Preparar ordem PAPER <span>→</span>
                </button>
              )}
            </div>
          </article>
          <aside className="panel-card detail-side">
            <span className="section-kicker">CONTROLE</span>
            <h3>Regras do sistema</h3>
            <div className="rule">
              <span>Modo operacional</span>
              <b>PAPER</b>
            </div>
            <div className="rule">
              <span>Ordens reais</span>
              <b>bloqueadas</b>
            </div>
            <div className="rule">
              <span>Agentes ativos</span>
              <b>{agents.length}</b>
            </div>
          </aside>
        </div>
      )}
    </section>
  );
}

function MarketView({ symbol, chart, onSymbolChange, onOrder }: { symbol: string; chart: MarketChart; onSymbolChange: (symbol: string) => void; onOrder: (symbol: string) => void }) {
  const symbols = ["PETR4", "VALE3", "ITUB4", "AAPL", "ETHUSD"];
  const points = chart?.points ?? [];
  const values = points.map((point) => point.value);
  const min = values.length ? Math.min(...values) : 0;
  const max = values.length ? Math.max(...values) : 1;
  const range = max - min || 1;
  const width = 800;
  const height = 300;
  const xForIndex = (index: number) => 20 + (index / Math.max(points.length - 1, 1)) * 760;
  const yForValue = (value: number) => 270 - ((value - min) / range) * 240;
  const line = points.map((point, index) => `${xForIndex(index)},${yForValue(point.value)}`).join(" ");
  function xForDate(date: string) {
    if (!points.length) return 20;
    const start = new Date(points[0].date).getTime();
    const end = new Date(points[points.length - 1].date).getTime();
    const ratio = end > start ? (new Date(date).getTime() - start) / (end - start) : 1;
    return 20 + Math.max(0, Math.min(1, ratio)) * 760;
  }
  return <div className="market-terminal"><div className="market-toolbar"><div className="symbol-tabs">{symbols.map((item) => <button className={item === symbol ? "active" : ""} key={item} onClick={() => onSymbolChange(item)}>{item}</button>)}</div><button className="secondary-btn" onClick={() => onOrder(symbol)}>Preparar ordem PAPER <span>→</span></button></div><article className="panel-card chart-card"><div className="chart-heading"><div><span className="section-kicker">HISTÓRICO DE PREÇOS · ATÉ 10 ANOS</span><h3>{symbol}</h3></div><div className="chart-meta"><span>{chart?.source || "Fonte não conectada"}</span><b>{chart?.delayed ? "ATRASADO" : "AO VIVO QUANDO DISPONÍVEL"}</b></div></div>{points.length ? <div className="price-chart"><svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`Gráfico histórico de ${symbol}`}><defs><linearGradient id="chart-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#62cfff" stopOpacity=".22" /><stop offset="100%" stopColor="#62cfff" stopOpacity="0" /></linearGradient></defs><polyline points={`${line} 780,270 20,270`} fill="url(#chart-fill)" stroke="none" /><polyline points={line} fill="none" stroke="#62cfff" strokeWidth="2" vectorEffect="non-scaling-stroke" />{chart.markers.map((marker) => <g key={`${marker.kind}-${marker.date}`} className={`chart-marker ${marker.kind.toLowerCase()}`}><line x1={xForDate(marker.date)} x2={xForDate(marker.date)} y1="20" y2="270" /><circle cx={xForDate(marker.date)} cy={yForValue(marker.value)} r="5" /><title>{marker.label} · R$ {marker.value.toFixed(2)}</title></g>)}</svg><div className="chart-axis"><span>{new Date(points[0].date).toLocaleDateString("pt-BR")}</span><span>R$ {max.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</span><span>R$ {min.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</span><span>{new Date(points[points.length - 1].date).toLocaleDateString("pt-BR")}</span></div></div> : <div className="empty-state large"><div className="empty-icon">◒</div><strong>Histórico indisponível</strong><p>{chart?.data_status ?? "Aguardando fonte de mercado."} Conecte um provedor autorizado para visualizar preços reais e atualizações.</p></div>}<div className="chart-legend"><span><i className="legend-line" /> preço histórico</span><span><i className="legend-dot buy" /> compra</span><span><i className="legend-dot sell" /> venda</span><span><i className="legend-dot planned" /> intenção</span></div></article></div>;
}

function SignalsView({ events, configured, onSync }: { events: NewsEvent[]; configured: boolean; onSync: () => void }) {
  return <div className="signals-layout"><article className="panel-card signals-feed"><div className="card-heading"><div><span className="section-kicker">RADAR GLOBAL</span><h2>Eventos monitorados</h2></div><button className="text-btn" onClick={onSync}>Sincronizar <span>↻</span></button></div>{configured ? <p className="source-ready"><i /> Provedor autorizado conectado · atualização conforme intervalo configurado</p> : <div className="signals-config-warning"><strong>Fontes em modo catálogo</strong><p>O sistema conhece as fontes oficiais, mas ainda não tem uma API licenciada conectada para receber notícias ao vivo.</p></div>}{events.length ? events.map((event) => <a className="news-event" href={event.source_url} target="_blank" rel="noreferrer" key={event.id}><span className="news-event-type">{event.event_type}</span><strong>{event.title}</strong><small>{event.source} · {event.published_at ? new Date(event.published_at).toLocaleString("pt-BR") : "horário não informado"}</small><p>{event.summary ?? "Sem resumo fornecido pela fonte."}</p></a>) : <div className="empty-state large"><div className="empty-icon">⌁</div><strong>Nenhum evento recebido</strong><p>Configure um provedor autorizado para alimentar este radar. Nenhum evento demonstrativo é exibido.</p></div>}</article><aside className="panel-card news-rules"><span className="section-kicker">ANÁLISE DE IMPACTO</span><h3>Como a Aurion usa as notícias</h3><div className="rule"><span>Classificação temática</span><b>ativa</b></div><div className="rule"><span>Impacto no ativo</span><b>cenário</b></div><div className="rule"><span>Compra automática</span><b>bloqueada</b></div><p className="footnote">Uma manchete política ou pesquisa eleitoral pode alterar expectativas, mas não determina sozinha o preço de uma ação. Cada sinal precisa de fonte, contexto, confirmação e dados de mercado.</p></aside></div>;
}

function WalletView({ wallet, walletBusy, onDeposit }: { wallet?: Wallet; walletBusy: boolean; onDeposit: (amount: number) => void }) {
  const [amount, setAmount] = useState("100");
  const balance = wallet?.balance ?? 0;
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const parsed = Number(amount.replace(",", "."));
    if (Number.isFinite(parsed) && parsed > 0) onDeposit(parsed);
  }
  return <div className="wallet-layout">
    <article className="panel-card wallet-hero">
      <div className="wallet-heading"><div><span className="section-kicker">CARTEIRA DA AURION</span><h3>Capital para investir</h3><p>Saldo reservado para as futuras ordens PAPER da agente fundadora.</p></div><span className="wallet-status"><i /> {wallet?.status ?? "CARREGANDO"}</span></div>
      <div className="wallet-balance"><span className="section-kicker">SALDO DISPONÍVEL</span><strong>R$ {balance.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</strong><small>BRL · apenas depósitos confirmados entram no saldo</small></div>
      <div className="wallet-warning"><span>!</span><div><strong>Pix ainda não conectado</strong><p>O pedido abaixo cria uma intenção de depósito. O saldo só muda depois que um provedor Pix confirmar o pagamento por webhook.</p></div></div>
    </article>
    <aside className="panel-card deposit-card"><span className="section-kicker">ADICIONAR CAPITAL</span><h3>Enviar via Pix</h3><p>Informe quanto pretende depositar para gerar um pedido rastreável.</p><form onSubmit={submit}><label htmlFor="pix-amount">Valor do depósito<input id="pix-amount" name="amount" inputMode="decimal" value={amount} onChange={(event) => setAmount(event.target.value)} placeholder="100,00" /></label><button className="primary-btn" disabled={walletBusy || !amount}>{walletBusy ? "Registrando…" : "Criar intenção Pix"}<span>→</span></button></form><small className="deposit-note">Não use uma chave Pix pessoal como se fosse a carteira. Precisamos conectar um provedor de pagamentos para gerar o QR Code e confirmar automaticamente.</small></aside>
    <article className="panel-card wallet-transactions"><div className="card-heading"><div><span className="section-kicker">MOVIMENTAÇÕES</span><h2>Histórico da carteira</h2></div><span className="count-badge">{wallet?.transactions.length ?? 0}</span></div>{wallet?.transactions.length ? wallet.transactions.map((transaction) => <div className="wallet-transaction" key={transaction.id}><span className="transaction-icon">↗</span><div><strong>Pix · R$ {transaction.amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</strong><small>{transaction.description}</small></div><b className="transaction-pending">{transaction.status === "PENDING_PROVIDER" ? "PENDENTE" : transaction.status}</b></div>) : <div className="empty-state"><div className="empty-icon">▣</div><strong>Nenhum depósito confirmado</strong><p>Os depósitos e créditos confirmados aparecerão aqui.</p></div>}</article>
  </div>;
}

function UnifiedWalletView({ wallet, walletBusy, onDeposit, onWithdraw }: { wallet?: Wallet; walletBusy: boolean; onDeposit: (amount: number) => void; onWithdraw: (amount: number, pixKey: string) => void }) {
  const [depositAmount, setDepositAmount] = useState("100");
  const [withdrawAmount, setWithdrawAmount] = useState("");
  const [pixKey, setPixKey] = useState("");
  const balance = wallet?.balance ?? 0;
  function submitDeposit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = Number(depositAmount.replace(",", "."));
    if (Number.isFinite(value) && value > 0) onDeposit(value);
  }
  function submitWithdrawal(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = Number(withdrawAmount.replace(",", "."));
    if (Number.isFinite(value) && value > 0 && pixKey.trim()) onWithdraw(value, pixKey.trim());
  }
  return <div className="wallet-layout">
    <article className="panel-card wallet-hero">
      <div className="wallet-heading"><div><span className="section-kicker">CARTEIRA DO ECOSSISTEMA</span><h3>Capital compartilhado</h3><p>Aurion e futuras IAs dependem deste mesmo saldo para investir e sobreviver.</p></div><span className="wallet-status"><i /> {wallet?.status ?? "CARREGANDO"}</span></div>
      <div className="wallet-balance"><span className="section-kicker">SALDO ÚNICO DISPONÍVEL</span><strong>R$ {balance.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</strong><small>BRL · retiradas preservam uma reserva mínima de sobrevivência</small></div>
      <div className="wallet-warning"><span>!</span><div><strong>Pix em modo pendente</strong><p>Depósitos e retiradas só alteram o saldo após confirmação de um provedor Pix autorizado.</p></div></div>
    </article>
    <aside className="panel-card deposit-card"><span className="section-kicker">ENTRADA DE CAPITAL</span><h3>Adicionar via Pix</h3><p>Crie uma solicitação rastreável para depositar na carteira única.</p><form onSubmit={submitDeposit}><label htmlFor="pix-deposit-amount">Valor do depósito<input id="pix-deposit-amount" inputMode="decimal" value={depositAmount} onChange={(event) => setDepositAmount(event.target.value)} placeholder="100,00" /></label><button className="primary-btn" disabled={walletBusy || !depositAmount}>{walletBusy ? "Registrando…" : "Solicitar depósito"}<span>→</span></button></form><small className="deposit-note">Nenhum saldo é inventado: sem webhook confirmado, a solicitação fica pendente.</small></aside>
    <aside className="panel-card deposit-card"><span className="section-kicker">SAÍDA DE CAPITAL</span><h3>Solicitar retirada</h3><p>Informe o valor e a chave Pix de destino. O envio real depende do provedor.</p><form onSubmit={submitWithdrawal}><label htmlFor="pix-withdraw-amount">Valor da retirada<input id="pix-withdraw-amount" inputMode="decimal" value={withdrawAmount} onChange={(event) => setWithdrawAmount(event.target.value)} placeholder="100,00" /></label><label htmlFor="pix-destination-key">Chave Pix de destino<input id="pix-destination-key" value={pixKey} onChange={(event) => setPixKey(event.target.value)} placeholder="Digite a chave Pix" autoComplete="off" /></label><button className="secondary-btn" disabled={walletBusy || !withdrawAmount || !pixKey.trim()}>{walletBusy ? "Registrando…" : "Solicitar retirada"}<span>→</span></button></form><small className="deposit-note">A chave não fica exposta na interface. Nenhum valor será enviado enquanto o Pix não estiver conectado.</small></aside>
    <article className="panel-card wallet-transactions"><div className="card-heading"><div><span className="section-kicker">MOVIMENTAÇÕES DA CARTEIRA ÚNICA</span><h2>Histórico financeiro</h2></div><span className="count-badge">{wallet?.transactions.length ?? 0}</span></div>{wallet?.transactions.length ? wallet.transactions.map((transaction) => <div className="wallet-transaction" key={transaction.id}><span className="transaction-icon">{transaction.direction === "DEBIT" ? "↙" : "↗"}</span><div><strong>{transaction.direction === "DEBIT" ? "Retirada" : "Depósito"} · R$ {transaction.amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</strong><small>{transaction.description}</small></div><b className="transaction-pending">{transaction.status === "PENDING_PROVIDER" ? "PENDENTE" : transaction.status}</b></div>) : <div className="empty-state"><div className="empty-icon">▣</div><strong>Nenhuma movimentação confirmada</strong><p>Depósitos e retiradas aparecerão aqui com seus respectivos estados.</p></div>}</article>
  </div>;
}

function EvolutionView({
  agents,
  onPropose,
}: {
  agents: Agent[];
  onPropose: () => void;
}) {
  const aurion = agents[0];
  const level = (aurion.generation ?? 0) + 1;
  const age = aurion.created_at
    ? Math.max(
        1,
        Math.floor(
          (Date.now() - new Date(aurion.created_at).getTime()) / 86400000,
        ) + 1,
      )
    : 1;
  return (
    <div className="evolution-layout">
      <article className="panel-card evolution-main">
        <div className="evolution-heading">
          <div>
            <span className="section-kicker">PROGRESSÃO DO ECOSSISTEMA</span>
            <h3>Desbloqueios da Aurion</h3>
          </div>
          <span className="level-badge">
            NÍVEL {String(level).padStart(2, "0")}
          </span>
        </div>
        <div className="progression-track">
          <div className="progress-node current">
            <span>01</span>
            <small>Nascer</small>
          </div>
          <div className="progress-line">
            <i />
          </div>
          <div className="progress-node locked">
            <span>02</span>
            <small>Primeiro ajudante</small>
          </div>
          <div className="progress-line">
            <i />
          </div>
          <div className="progress-node locked">
            <span>03</span>
            <small>Constelação</small>
          </div>
        </div>
        <div className="evolution-stats">
          <div>
            <span className="section-kicker">IDADE</span>
            <strong>
              {age} <small>ciclo{age === 1 ? "" : "s"}</small>
            </strong>
            <p>Cada dia ativo fortalece a linhagem.</p>
          </div>
          <div>
            <span className="section-kicker">CAPITAL NECESSÁRIO</span>
            <strong>
              R$ 1.000 <small>configurável</small>
            </strong>
            <p>O limite será comparado ao saldo real da carteira.</p>
          </div>
          <div>
            <span className="section-kicker">STATUS</span>
            <strong className="locked-text">AGUARDANDO SALDO</strong>
            <p>Nenhuma criação é liberada sem fonte verificável.</p>
          </div>
        </div>
        <div className="unlock-callout">
          <span>◈</span>
          <div>
            <strong>Próximo desbloqueio: Ajudante nível 01</strong>
            <p>
              Quando o patrimônio atingir o limite definido, a Aurion poderá
              propor uma nova inteligência especializada. A criação continua
              exigindo autorização do operador.
            </p>
          </div>
          <button className="secondary-btn" onClick={onPropose}>
            Criar proposta <span>→</span>
          </button>
        </div>
      </article>
      <aside className="panel-card lineage-card">
        <span className="section-kicker">LINHAGEM</span>
        <h3>
          {agents.length} agente{agents.length === 1 ? "" : "s"} ativo
          {agents.length === 1 ? "" : "s"}
        </h3>
        <div className="lineage-root">
          <span>✦</span>
          <div>
            <b>Aurion</b>
            <small>fundadora · geração 00</small>
          </div>
        </div>
        <div className="lineage-empty">
          Os próximos nós nascerão aqui quando o capital e a autorização
          existirem.
        </div>
      </aside>
    </div>
  );
}

function Modal({
  type,
  asset,
  busy,
  onClose,
  onConnection,
  onOrder,
  onProposal,
}: {
  type: "connection" | "policy" | "order" | "proposal";
  asset: string;
  busy: boolean;
  onClose: () => void;
  onConnection: () => void;
  onOrder: () => void;
  onProposal: (form: {
    name: string;
    role: string;
    specialization: string;
    objective: string;
    reason: string;
  }) => void;
}) {
  const isOrder = type === "order";
  const isProposal = type === "proposal";
  function submitProposal(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    onProposal({
      name: String(form.get("name") ?? ""),
      role: String(form.get("role") ?? ""),
      specialization: String(form.get("specialization") ?? ""),
      objective: String(form.get("objective") ?? ""),
      reason: String(form.get("reason") ?? ""),
    });
  }
  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onMouseDown={(e) => {
        if (e.currentTarget === e.target) onClose();
      }}
    >
      <section
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <button className="modal-close" onClick={onClose} aria-label="Fechar">
          ×
        </button>
        <span className="section-kicker">
          AETERNUM /{" "}
          {isOrder ? "PAPER" : isProposal ? "EVOLUÇÃO" : "CONFIGURAÇÃO"}
        </span>
        <h2 id="modal-title">
          {isOrder
            ? `Preparar ordem · ${asset}`
            : isProposal
              ? "Propor um novo ajudante"
              : type === "policy"
                ? "Política de dados"
                : "Conectar fonte verificável"}
        </h2>
        {isProposal ? (
          <form onSubmit={submitProposal}>
            <p>
              Esta proposta será registrada na linhagem da Aurion. O desbloqueio
              por capital depende de saldo verificável e a aprovação continua
              manual.
            </p>
            <label htmlFor="proposal-name">
              Nome
              <input
                id="proposal-name"
                name="name"
                required
                placeholder="Ex.: Nyx"
              />
            </label>
            <label htmlFor="proposal-role">
              Função
              <input
                id="proposal-role"
                name="role"
                required
                placeholder="Ex.: Analista macro"
              />
            </label>
            <label htmlFor="proposal-specialization">
              Especialidade
              <input
                id="proposal-specialization"
                name="specialization"
                required
                placeholder="Ex.: Política e juros"
              />
            </label>
            <label htmlFor="proposal-objective">
              Objetivo
              <input
                id="proposal-objective"
                name="objective"
                required
                placeholder="O que essa IA deve proteger?"
              />
            </label>
            <label htmlFor="proposal-reason">
              Motivo
              <input
                id="proposal-reason"
                name="reason"
                required
                placeholder="Por que criar agora?"
              />
            </label>
            <button className="primary-btn" disabled={busy}>
              {busy ? "Registrando…" : "Enviar proposta para autorização"}
            </button>
          </form>
        ) : isOrder ? (
          <>
            <p>
              Esta ordem ficará apenas registrada como simulação. Nenhuma
              corretora ou conta bancária será acessada.
            </p>
            <label htmlFor="order-quantity">
              Quantidade
              <input
                id="order-quantity"
                name="quantity"
                type="number"
                min="1"
                defaultValue="1"
              />
            </label>
            <label htmlFor="order-limit">
              Limite de preço
              <input
                id="order-limit"
                name="limit"
                placeholder="Aguardando cotação real"
                disabled
              />
            </label>
            <div className="modal-warning">
              ⚠ Cotações reais ainda não estão conectadas. A simulação não será
              executada.
            </div>
            <button className="primary-btn" onClick={onOrder}>
              Salvar simulação PAPER
            </button>
          </>
        ) : (
          <>
            <p>
              O AETERNUM só exibirá informações de fontes autorizadas.
              Credenciais ficam no backend e nunca no navegador.
            </p>
            <div className="integration-option">
              <span>◉</span>
              <div>
                <strong>
                  {type === "policy"
                    ? "Regra de veracidade"
                    : "Provedores de mercado e notícias"}
                </strong>
                <small>
                  {type === "policy"
                    ? "Sem dados demonstrativos, sem saldo inventado, sem previsão garantida."
                    : "Conexão segura ainda não configurada neste ambiente."}
                </small>
              </div>
            </div>
            <button className="primary-btn" onClick={onConnection}>
              {type === "policy" ? "Entendi" : "Continuar configuração"}
            </button>
          </>
        )}
      </section>
    </div>
  );
}
