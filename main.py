from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from User import UserCreate
from UsersTable import UsersTable
import ConnectToDB

app = FastAPI()
YANDEX_MAPS_API_KEY = "22955a5e-740a-4850-8379-1439a844b941"


@app.get("/get-api-key")
async def get_api_key():
    return {"api_key": YANDEX_MAPS_API_KEY}

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


# # Эндпоинт регистрации
# @app.post("/register", status_code=status.HTTP_201_CREATED)
# async def register_user(
#         request: UserCreate,
#         users_table: UsersTable = Depends(ConnectToDB.get_users_repository())):
#     try:
#         # Проверка существующего пользователя
#         if users_table.find_by_email(request.email):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Email already registered"
#             )
#
#         user_id = users_table.add_user(request)
#         return JSONResponse(
#             status_code=status.HTTP_201_CREATED,
#             content=users_table.get_user(user_id)
#         )
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Registration failed: {str(e)}"
#         )
#
#
# @app.post("/login")
# async def login_user(
#         request: UserCreate,
#         users_table: UsersTable = Depends(ConnectToDB.get_users_repository())):
#     try:
#         user = users_table.find_by_email(request.email)
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found"
#             )
#
#         if users_table.get_user_password_by_email(request.email) != request.password:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Incorrect password"
#             )
#
#         return JSONResponse(
#             status_code=status.HTTP_,
#             content=user
#         )
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Login failed: {str(e)}"
#         )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", port=5432, reload=True)
