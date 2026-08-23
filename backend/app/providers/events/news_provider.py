class NewsProvider:
    name = "official_sources_catalog"

    def search(self, query: str) -> list[dict]:
        raise NotImplementedError("Nenhum provedor de notícias autorizado está configurado.")
