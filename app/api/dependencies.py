from __future__ import annotations
from typing import Annotated

from fastapi import Depends, HTTPException, Request

from app.dto_configs import AppContainer


def obter_container(request: Request) -> AppContainer:
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise HTTPException(
            status_code=500,
            detail="Container da aplicacao nao foi inicializado.",
        )
    if not isinstance(container, AppContainer):
        raise HTTPException(
            status_code=500,
            detail="Container da aplicacao tem tipo invalido.",
        )
    return container

AppContainerDep = Annotated[AppContainer, Depends(obter_container)]
