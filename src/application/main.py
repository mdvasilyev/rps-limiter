import uvicorn

from src.core.configurations.config import GlobalConfig
from src.core.configurations.dishka import container
from src.core.configurations.fastapi import get_app


def main():
    config: GlobalConfig = container.get(GlobalConfig)
    app = get_app()

    uvicorn.run(app, host=config.app.host, port=config.app.port)


if __name__ == "__main__":
    main()
