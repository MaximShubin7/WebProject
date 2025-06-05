from typing import List
from uuid import UUID

from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import uvicorn
import bcrypt

from Classes.Comment import CommentCreate, CommentUpdate
from Classes.FilterEstablishments import FilterEstablishments
from Classes.Stock import StockCreate, StockResponse
from DataBase.CommentsTable import CommentsTable
from Classes.Establishment import EstablishmentCreate, EstablishmentUpdate
from DataBase.EstablishmentsTable import EstablishmentsTable
from DataBase.StocksTable import StocksTable
from Parsers.ParserReceiptQRCodeToData import UseParserReceipt
from Classes.User import UserCreate, UserLogin, UserResponse, UserUpdate
from DataBase.UsersTable import UsersTable

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/users/register")
def register(user: UserCreate):
    repository = UsersTable()
    if repository.find_by_email(user.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists"
        )
    user_id = repository.add_user(user)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=repository.get_user(user_id).model_dump(mode='json')
    )


@app.post("/users/login")
def login(user: UserLogin):
    repository = UsersTable()
    finded_user = repository.find_by_email(user.email)
    if (finded_user is None or
            not bcrypt.checkpw(user.password.encode('utf-8'),
                               repository.get_user_password_by_email(user.email).encode('utf-8'))):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=finded_user.model_dump(mode='json')
    )


@app.get("/users/{user_id}")
def get_user(user_id: str):
    repository = UsersTable()
    finded_user = repository.get_user(user_id)
    if finded_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=finded_user.model_dump(mode='json')
    )


@app.patch("/users/update-user/")
def update_user(user: UserUpdate):
    repository = UsersTable()
    finded_user = repository.get_user(user.user_id)
    if finded_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not repository.update_user(user):
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No changes")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=repository.get_user(user.user_id).model_dump(mode='json')
    )


@app.delete("/users/delete-user/{user_id}")
def delete_user(user_id: str):
    repository = UsersTable()
    finded_user = repository.get_user(user_id)
    if finded_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    repository.delete_user(user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Success"
    )


@app.post("/establishments/create-establishment")
def create_establishment(establishment: EstablishmentCreate):
    repository = EstablishmentsTable()
    repository.add_establishment(establishment)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content="Success"
    )


@app.get("/establishments")
def get_all_establishments(filters: FilterEstablishments):
    repository = EstablishmentsTable()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[establishment.model_dump(mode='json') for establishment in repository.get_all_establishments(filters)]
    )


@app.get("/establishments/{establishment_id}")
def get_establishment(establishment_id: str):
    repository = EstablishmentsTable()
    finded_establishment = repository.get_establishment(establishment_id)
    if finded_establishment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Establishment not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=finded_establishment.model_dump(mode='json')
    )


@app.patch("/establishments/update-establishment/")
def update_establishment(establishment: EstablishmentUpdate):
    repository = EstablishmentsTable()
    finded_establishment = repository.get_establishment(establishment.establishment_id)
    if finded_establishment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Establishment not found")
    if not repository.update_establishment(establishment):
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No changes")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=repository.get_establishment(establishment.establishment_id).model_dump(mode='json')
    )


@app.delete("/establishments/delete-establishment/{establishment_id}", response_model=UserResponse)
def delete_establishment(establishment_id: str):
    repository = EstablishmentsTable()
    finded_establishment = repository.get_establishment(establishment_id)
    if finded_establishment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Establishment not found")
    repository.delete_establishment(establishment_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Success"
    )


@app.post("/comments/create-comment")
def create_comment(comment: CommentCreate):
    repository_comments = CommentsTable()
    repository_comments.add_comment(comment)
    repository_establishments = EstablishmentsTable()
    repository_establishments.increment_comment_count(comment.establishment_id)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content="Success"
    )


@app.get("/comments/{comment_id}")
def get_comment(comment_id: str):
    repository = CommentsTable()
    finded_comment = repository.get_comment(comment_id)
    if finded_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=finded_comment.model_dump(mode='json')
    )


@app.get("/comments/establishments/{establishment_id}")
def get_comments_establishment(establishment_id: str):
    repository_comments = CommentsTable()
    repository_establishments = EstablishmentsTable()
    finded_establishment = repository_establishments.get_establishment(establishment_id)
    if finded_establishment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Establishment not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[comment.model_dump(mode='json') for comment in
                 repository_comments.get_comments_by_establishment(establishment_id)]
    )


@app.get("/comments/users/{user_id}")
def get_comments_user(user_id: str):
    repository_comments = CommentsTable()
    repository_users = UsersTable()
    finded_user = repository_users.get_user(user_id)
    if finded_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[comment.model_dump(mode='json') for comment in
                 repository_comments.get_comments_by_user(user_id)]
    )


@app.patch("/comments/update-comment/")
def update_establishment(comment: CommentUpdate):
    repository = CommentsTable()
    finded_comment = repository.get_comment(comment.comment_id)
    if finded_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if not repository.update_comment(comment):
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No changes")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=repository.get_comment(comment.comment_id).model_dump(mode='json')
    )


@app.delete("/comments/delete-comment/{comment_id}")
def delete_comment(comment_id: str):
    repository = CommentsTable()
    finded_comment = repository.get_comment(comment_id)
    if finded_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    repository.delete_comment(comment_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Success"
    )


@app.post("/users/get-bonus")
def request_session(user: UserResponse):
    if user.phone_number is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The user does not have a phone number")
    try:
        parser = UseParserReceipt()
        parser.request_session_id(user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Success"
    )


@app.post("/users/verify-bonus")
def get_bonus(user: UserResponse, code: str, qr_code_image: UploadFile = File(...)):
    if user.phone_number is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The user does not have a phone number")
    try:
        contents = qr_code_image.read()
        image_np = np.frombuffer(contents, np.uint8)
        image_np = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        if image_np is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")
        parser = UseParserReceipt()
        parser.add_bonus(user, code, image_np)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The file is not a valid image")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Success"
    )


@app.post("/users/buy-promo")
def buy_promo(user: UserResponse, price: float):
    if user.bonus < price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You don't have enough bonuses")
    repository = UsersTable()
    repository.change_bonus(user.user_id, -price)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Success"
    )


@app.get("/api-key")
def get_api_key_yandex_maps():
    API_KEY_YANDEX_MAPS = "22955a5e-740a-4850-8379-1439a844b941"
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=API_KEY_YANDEX_MAPS
    )


@app.post("/stocks/create-stock")
def create_stock(stock: StockCreate) -> StockResponse:
    repository = StocksTable()
    repository.add_stock(stock)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content="Success"
    )


@app.get("/stocks/")
def get_all_stocks() -> List[StockResponse]:
    repository = StocksTable()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[stock.model_dump(mode='json') for stock in repository.get_all_stocks()]
    )


@app.get("/stocks/{stock_id}")
def get_stock(stock_id: UUID) -> StockResponse:
    repository = StocksTable()
    finded_stock = repository.get_stock(stock_id)
    if not finded_stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=finded_stock.model_dump(mode='json')
    )


@app.delete("/stocks/delete-stock/{stock_id}")
def delete_stock(stock_id: UUID) -> None:
    repository = StocksTable()
    if not repository.delete_stock(stock_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Success"
    )
