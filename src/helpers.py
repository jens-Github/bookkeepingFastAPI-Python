from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse, Response
from src.db import user_documents
from src.security import *
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from src.models import TokenData


async def create(model, model_documents, current_user_id):
    model.created = datetime.now()
    model.updated = datetime.now()
    model.user_id = current_user_id
    model = jsonable_encoder(model)
    model = await model_documents.insert_one(model)
    model = await model_documents.find_one({"_id": model.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=model)


async def update(model, model_id, model_documents, current_user_id):
    model = {k: v for k, v in model.dict().items() if v is not None}
    if len(model) >= 3:
        if 'created' in model:
            model.pop('created')
        model['updated'] = datetime.now()
        update_result = await model_documents.update_one({"_id": model_id, '_user_id': current_user_id},
                                                         {"$set": model})
        if update_result.modified_count == 1:
            if (updated_model := await model_documents.find_one({"_id": model_id,
                                                                 '_user_id': current_user_id})) is not None:
                return updated_model

    if (existing_model := await model_documents.find_one({"_id": model_id,
                                                          '_user_id': current_user_id})) is not None:
        return existing_model
    return Response(status_code=status.HTTP_404_NOT_FOUND)


async def get_user_by_username(username: str):
    if (user := await user_documents.find_one(
            {
                'username': username,
            })) is not None:
        return user
    return None


async def get_user_by_id(_id: str):
    if (user := await user_documents.find_one(
            {
                '_id': _id,
            })) is not None:
        return user
    return None


async def authenticate_user(username: str, password: str):
    user = await get_user_by_username(username)
    if not user:
        return False
    if not verify_pwd(password, user['password']):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError as e:
        print(e)
        raise credentials_exception
    user = await get_user_by_id(token_data.user_id)
    if not user:
        raise credentials_exception
    return user
