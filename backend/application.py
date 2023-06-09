from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from backend.api import router
from backend.utils.exceptions import PaginationException

app = FastAPI()
app.include_router(router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


@app.exception_handler(PaginationException)
async def pagination_exception_handler(
    request: Request, exc: PaginationException
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"message": exc.args[0]},
    )
