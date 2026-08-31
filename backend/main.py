from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import simulator, agent, evaluator

app = FastAPI(
    title="Ultron Engine API",
    description="Backend API for the Ultron Autonomous Revenue Recovery Engine",
    version="3.2.0"
)

# Configure CORS for local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(simulator.router)
app.include_router(agent.router)
app.include_router(evaluator.router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "engine": "Ultron", "version": "3.2.0"}

if __name__ == "__main__":
    import uvicorn
    # When run directly, start the server
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
