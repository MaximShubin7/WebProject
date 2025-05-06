from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
import uvicorn
import bcrypt
import io

from Comment import CommentCreate, CommentUpdate
from CommentsTable import CommentsTable
from ConnectDataBase import get_db_connection
from Establishment import EstablishmentCreate, EstablishmentUpdate
from EstablishmentsTable import EstablishmentsTable
from ParserReceiptQRCodeToData import UseParserReceipt
from User import UserCreate, UserLogin, UserResponse, UserUpdate
from UsersTable import UsersTable

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/users/register")
async def register(user: UserCreate):
    repository = UsersTable(get_db_connection())
    if repository.find_by_email(user.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists"
        )
    user_id = repository.add_user(user)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=repository.get_user(str(user_id)).model_dump(mode='json')
    )


@app.post("/users/login")
async def login(user: UserLogin):
    repository = UsersTable(get_db_connection())
    finded_user = repository.find_by_email(user.email)
    if (finded_user is None or
            not bcrypt.checkpw(user.password, repository.get_user_password_by_email(user.email))):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=finded_user.model_dump(mode='json')
    )


@app.get("/users/{user_id}")
async def get_user(user_id: str):
    repository = UsersTable(get_db_connection())
    finded_user = repository.get_user(user_id)
    if finded_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=finded_user.model_dump(mode='json')
    )


@app.patch("/users/update-user/")
async def update_user(user: UserUpdate):
    repository = UsersTable(get_db_connection())
    finded_user = repository.get_user(str(user.user_id))
    if finded_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not repository.update_user(user):
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No changes")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=repository.get_user(str(user.user_id)).model_dump(mode='json')
    )


@app.delete("/users/delete-user/{user_id}")
async def delete_user(user_id: str):
    repository = UsersTable(get_db_connection())
    finded_user = repository.get_user(user_id)
    if finded_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    repository.delete_user(user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Success"
    )


@app.post("/establishments/create-establishment")
async def create_establishment(establishment: EstablishmentCreate):
    repository = EstablishmentsTable(get_db_connection())
    repository.add_establishment(establishment)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content="Success"
    )


@app.get("/establishments")
async def get_all_establishments():
    repository = EstablishmentsTable(get_db_connection())
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[establishment.model_dump(mode='json') for establishment in repository.get_all_establishments()]
    )


@app.get("/establishments/{establishment_id}")
async def get_establishment(establishment_id: str):
    repository = EstablishmentsTable(get_db_connection())
    finded_establishment = repository.get_establishment(establishment_id)
    if finded_establishment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Establishment not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=finded_establishment.model_dump(mode='json')
    )


@app.patch("/establishments/update-establishment/")
async def update_establishment(establishment: EstablishmentUpdate):
    repository = EstablishmentsTable(get_db_connection())
    finded_establishment = repository.get_establishment(str(establishment.establishment_id))
    if finded_establishment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Establishment not found")
    if not repository.update_establishment(establishment):
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No changes")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=repository.get_establishment(str(establishment.establishment_id)).model_dump(mode='json')
    )


@app.delete("/establishments/delete-establishment/{establishment_id}", response_model=UserResponse)
async def delete_establishment(establishment_id: str):
    repository = EstablishmentsTable(get_db_connection())
    finded_establishment = repository.get_establishment(establishment_id)
    if finded_establishment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Establishment not found")
    repository.delete_establishment(establishment_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Success"
    )


@app.post("/comments/create-comment")
async def create_comment(comment: CommentCreate):
    repository_comments = CommentsTable(get_db_connection())
    repository_comments.add_comment(comment)
    repository_establishments = EstablishmentsTable(get_db_connection())
    repository_establishments.increment_comment_count(str(comment.establishment_id))
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content="Success"
    )


@app.get("/comments/{comment_id}")
async def get_comment(comment_id: str):
    repository = CommentsTable(get_db_connection())
    finded_comment = repository.get_comment(comment_id)
    if finded_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=finded_comment.model_dump(mode='json')
    )


@app.get("/comments/establishments/{establishment_id}")
async def get_comments_establishment(establishment_id: str):
    repository_comments = CommentsTable(get_db_connection())
    repository_establishments = EstablishmentsTable(get_db_connection())
    finded_establishment = repository_establishments.get_establishment(establishment_id)
    if finded_establishment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Establishment not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[comment.model_dump(mode='json') for comment in
                 repository_comments.get_comments_by_establishment(establishment_id)]
    )


@app.get("/comments/users/{user_id}")
async def get_comments_user(user_id: str):
    repository_comments = CommentsTable(get_db_connection())
    repository_users = UsersTable(get_db_connection())
    finded_user = repository_users.get_user(user_id)
    if finded_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[comment.model_dump(mode='json') for comment in
                 repository_comments.get_comments_by_user(user_id)]
    )


@app.patch("/comments/update-comment/")
async def update_establishment(comment: CommentUpdate):
    repository = CommentsTable(get_db_connection())
    finded_comment = repository.get_comment(str(comment.comment_id))
    if finded_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if not repository.update_comment(comment):
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No changes")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=repository.get_comment(str(comment.comment_id)).model_dump(mode='json')
    )


@app.delete("/comments/delete-comment/{comment_id}", response_model=UserResponse)
async def delete_comment(comment_id: str):
    repository = CommentsTable(get_db_connection())
    finded_comment = repository.get_comment(comment_id)
    if finded_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    repository.delete_comment(comment_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Success"
    )


@app.delete("/comments/delete-comment/{comment_id}", response_model=UserResponse)
async def delete_comment(comment_id: str):
    repository = CommentsTable(get_db_connection())
    finded_comment = repository.get_comment(comment_id)
    if finded_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    repository.delete_comment(comment_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Success"
    )


@app.post("/users/get-bonus", response_model=UserResponse)
async def request_session(user: UserResponse):
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
async def get_bonus(user: UserResponse, code: str, qr_code_image: UploadFile = File(...)):
    if user.phone_number is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The user does not have a phone number")
    try:
        img = Image.open(io.BytesIO(qr_code_image))
        if img is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")
        parser = UseParserReceipt()
        parser.add_bonus(user, code, img)
    except (UnidentifiedImageError, IOError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The file is not a valid image")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Success"
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=4000)
