from http.client import responses
from typing import List, Optional, Union

from fastapi import Depends, FastAPI, HTTPException, Header, APIRouter, Security
from fastapi.security import APIKeyHeader
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel


_api_key = APIKeyHeader(name="x-api-key", scheme_name="api-key", auto_error=True)

def get_api_key(token: str = Security(_api_key)):
    if token != "my_secreto":
        raise HTTPException(status_code=403, detail=f"Invalid token!")


class User(BaseModel):
    id: int
    name: str
    last_name: str
    job: str


class Computer(BaseModel):
    id: int
    brand: str
    model: str
    price: float

class Message(BaseModel):
    detail: str


_users = [
    User(id=1, name="Pedro", last_name="Lopez", job="Red Hat"),
    User(id=2, name="David", last_name="Garcia", job="Smart Protection"),
    User(id=3, name="Pedro", last_name="Gomez", job="Google"),
    User(id=4, name="Rocio", last_name="Lopez", job="Amazon"),
    User(id=5, name="David", last_name="Lopez", job="Google"),
    User(id=6, name="Apu", last_name="Jefe de Pedro", job="Red Hat"),
    User(id=7, name="Ruben", last_name="Sanchez", job="Amazon"),
]

_computers = [
    Computer(id=1, brand="HP", model="HP 1", price=1000),
    Computer(id=2, brand="Dell", model="DELL 1", price=1200),
    Computer(id=3, brand="Apple", model="Mac", price=1500),
]


users_api_router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@users_api_router.get("", response_model=List[User])
def get_users(job: Optional[str] = None, name: Optional[str] = None, user_agent: Union[str, None] = Header(default=None)) -> List[User]:
    users = [
        u for u in _users if job is None or u.job == job
    ]
    users = [
        u for u in users if name is None or u.name == name
    ]
    return users


@users_api_router.get("{user_id}", response_model=User, responses={404: {"model": Message}})
def get_user(user_id: int) -> User:
    for u in _users:
        if u.id == user_id:
            return u
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found!")


computer_api_router = APIRouter(
    prefix="/computers",
    tags=["computers"]
)

@computer_api_router.get("", response_model=List[Computer])
def get_computers() -> List[Computer]:
    return _computers

@computer_api_router.get("/{computer_id}", response_model=Computer, responses={404: {"model": Message}})
def get_user(computer_id: int) -> Computer:
    for u in _computers:
        if u.id == computer_id:
            return u
    raise HTTPException(status_code=404, detail=f"Computer '{computer_id}' not found!")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Custom title",
        version="2.5.0",
        description="Pepito perez",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Red_Hat_logo.svg/1200px-Red_Hat_logo.svg.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI(dependencies=[Depends(get_api_key)])
app.openapi = custom_openapi

app.include_router(users_api_router)
app.include_router(computer_api_router)