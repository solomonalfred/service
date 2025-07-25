from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import __all__ as routers
from src.core import APIINFO


def get_application():
    app = FastAPI(title=APIINFO.title,
                  version=APIINFO.version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for router in routers:
        app.include_router(router)

    return app

app = get_application()
