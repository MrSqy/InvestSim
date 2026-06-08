from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.routers import market, orders, portfolio, analytics

app = FastAPI(title="InvestSim API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(market.router)
app.include_router(orders.router)
app.include_router(portfolio.router)
app.include_router(analytics.router)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
