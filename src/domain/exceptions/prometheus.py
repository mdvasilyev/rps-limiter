class PrometheusError(Exception):
    def __init__(
        self,
        message: str,
        *,
        query: str | None = None,
        status_code: int | None = None,
        details: str | None = None,
    ) -> None:
        self.message = message
        self.query = query
        self.status_code = status_code
        self.details = details
        super().__init__(self.__str__())

    def __str__(self) -> str:
        parts: list[str] = [self.message]
        if self.query:
            parts.append(f"query={self.query}")
        if self.status_code is not None:
            parts.append(f"status_code={self.status_code}")
        if self.details:
            parts.append(f"details={self.details}")
        return "; ".join(parts)
