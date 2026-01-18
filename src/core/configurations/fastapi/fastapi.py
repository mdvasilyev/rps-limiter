from fastapi import FastAPI


def get_app() -> FastAPI:
    """Create and return a FastAPI application instance.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    app = FastAPI(
        title="RPS Limiter",
        description="Service for managing model lifecycle based on RPS",
        version="0.1.0",
    )

    return app
