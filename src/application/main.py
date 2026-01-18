import uvicorn

from src.core.configurations import get_config
from src.core.configurations.fastapi import get_app


def main():
    config = get_config()
    app = get_app()

    uvicorn.run(app, host=config.app.host, port=config.app.port)


if __name__ == "__main__":
    main()
