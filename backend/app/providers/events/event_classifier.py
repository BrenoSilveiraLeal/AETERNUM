EVENT_KEYWORDS = {
    "juros": ("juros", "selic", "taxa básica"),
    "inflacao": ("inflação", "inflacionária", "ipca", "cpi"),
    "cambio": ("câmbio", "dólar", "euro", "moeda"),
    "eleicao": ("eleição", "eleições", "pesquisa eleitoral", "candidato"),
    "regulacao": ("regulação", "regulador", "cvm", "lei", "medida provisória"),
    "guerra": ("guerra", "conflito", "ataque", "sanções"),
    "desastre_natural": ("terremoto", "furacão", "enchente", "desastre", "incêndio"),
    "energia": ("petróleo", "energia", "gás", "brent"),
    "commodity": ("soja", "minério", "ouro", "commodity"),
    "resultado_empresarial": ("balanço", "lucro", "receita", "resultado trimestral"),
    "credito": ("crédito", "inadimplência", "dívida"),
}


def classify(title: str) -> str:
    lowered = title.casefold()
    for event_type, keywords in EVENT_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return event_type
    return "nao_classificado"
