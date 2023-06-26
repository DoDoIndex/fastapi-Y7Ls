from fastapi import FastAPI


def create_app() -> FastAPI:
    from .router import router

    app = FastAPI()

    app.include_router(router)

    return app


app = create_app()
