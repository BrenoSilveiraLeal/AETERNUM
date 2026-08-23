class NewsProvider:
    """Boundary for licensed/official news APIs; no scraping or fake endpoints."""

    name = "unconfigured"

    def search(self, query: str) -> list[dict[str, str]]:
        raise NotImplementedError("Configure an authorized news provider in the backend")
