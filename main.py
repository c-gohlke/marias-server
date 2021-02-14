from fastapi import FastAPI
from routers import (home,
                     login,
                     register,
                     websocket,
                     logout)

app = FastAPI()

app.include_router(home.router)
app.include_router(login.router)
app.include_router(register.router)
app.include_router(websocket.router)
app.include_router(logout.router)
