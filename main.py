"""
This module initializes and configures the FastAPI application.

It imports the necessary routers from the `src.api` package and includes them
in the FastAPI application instance with the specified prefixes.

Routers included:
- utils: Handles utility endpoints.
- contacts: Manages contact-related endpoints.
- birstdays: Manages birthday-related endpoints.
- auth: Handles authentication and authorization endpoints.
- users: Manages user-related endpoints.

The application is accessible via the `/api` prefix for all included routers.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from src.api import contacts, utils, birstdays, auth, users

app = FastAPI()
origins = ["http://localhost:*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(
    request: Request, exc: RateLimitExceeded
):  # pylint: disable=W0613
    """
    Handles rate limit exceeded exceptions.
    Args:
        request (Request): The incoming HTTP request.
        exc (RateLimitExceeded): The exception raised when the rate limit is exceeded.
    Returns:
        JSONResponse: A JSON response with a 429 status code and an error message
            indicating that the rate limit has been exceeded.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Limit exceeded, too many requests"},
    )


app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(birstdays.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
