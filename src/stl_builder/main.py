from fastapi import FastAPI


def create_app() -> FastAPI:
    from .router import router as router_v1

    app = FastAPI()

    app.include_router(router_v1)

    return app


app = create_app()
