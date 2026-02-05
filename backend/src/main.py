"""
Main entry point for the Chat Agent Connector server.
"""
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.chat_endpoint import router as chat_router
from .api.auth_endpoint import router as auth_router
from .core.config import settings
from .core.database import init_db
# Import models to ensure they're registered with SQLModel
from . import models


def create_app():
    """
    Create and configure the FastAPI application.
    """
    app_instance = FastAPI(
        title="Chat Agent Connector",
        description="A stateless chat backend that connects reusable agents to MCP tools using an external LLM provider",
        version="0.1.0"
    )

    # Configure CORS — origins from env var CORS_ORIGINS (comma-separated), default "*"
    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Startup event
    @app_instance.on_event("startup")
    async def startup():
        """Initialize database and MCP server on startup."""
        try:
            await init_db()
            print("[OK] Database initialized successfully")
        except Exception as e:
            print(f"[WARNING] Database initialization failed: {e}")
            print("[WARNING] Server will start but database-dependent features may not work")

    # Include routers
    app_instance.include_router(chat_router, prefix="/api")
    app_instance.include_router(auth_router, prefix="/api")

    # Root endpoint
    @app_instance.get("/")
    def root():
        return {"status": "healthy", "service": "chat-agent-connector", "docs": "/docs"}

    # Health check endpoint
    @app_instance.get("/health")
    def health_check():
        return {"status": "healthy", "service": "chat-agent-connector", "mcp_tools": "ready"}

    return app_instance


# Create app instance at module level for uvicorn
app = create_app()


def main():
    """
    Main entry point for the application when run directly.
    """
    # Run the server
    uvicorn.run(
        "src.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True  # Enable reload for development
    )


if __name__ == "__main__":
    main()