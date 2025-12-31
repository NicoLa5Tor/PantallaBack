import uvicorn

from config.settings import load_settings


def main() -> None:
    settings = load_settings()
    uvicorn.run("app:app", host=settings.ws_host, port=settings.ws_port, log_level="info")


if __name__ == "__main__":
    main()
