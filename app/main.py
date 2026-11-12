"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import close_client, ping_database
from app.routes import todos

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("todo-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ping_database()
        logger.info("Connected to MongoDB Atlas.")
    except PyMongoError as exc:
        # Don't crash: /docs still loads and endpoints return a clean 500 until Atlas is reachable.
        logger.error("Could not connect to MongoDB Atlas: %s", exc)
    yield
    close_client()


app = FastAPI(
    title="To-Do List API",
    description="A basic CRUD REST API built with FastAPI, PyMongo and MongoDB Atlas.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(todos.router)


def error_response(status_code: int, message, details=None) -> JSONResponse:
    body = {"error": {"status": status_code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return error_response(exc.status_code, exc.detail)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Return 400 (instead of FastAPI's default 422) with readable details.
    details = [
        {
            "field": ".".join(str(part) for part in err["loc"][1:]) or str(err["loc"][0]),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return error_response(400, "Validation failed", details)


@app.exception_handler(PyMongoError)
async def database_exception_handler(request: Request, exc: PyMongoError):
    logger.exception("Database error: %s", exc)
    return error_response(500, "Database error. Please try again later.")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return error_response(500, "Internal server error.")


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "docs": "/docs"}