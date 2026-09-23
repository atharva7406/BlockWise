from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_tasks import router as tasks_router
from app.api.routes_bundles import router as bundles_router
from app.api.routes_schedule import router as schedule_router
from app.api.routes_demo import router as demo_router

app = FastAPI(
    title="PS-27 Automatic Block Planning API",
    description="Intelligent Railway Maintenance Block Planning & Auto-Shadow Bundling Engine (SIH26027)",
    version="1.0.0",
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(tasks_router)
app.include_router(bundles_router)
app.include_router(schedule_router)
app.include_router(demo_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PS-27 Automatic Block Planning Engine",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
