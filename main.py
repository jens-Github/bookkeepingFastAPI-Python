from fastapi.security import OAuth2PasswordRequestForm
import uvicorn
from typing import List
from src.helpers import *

from starlette import status
from starlette.responses import Response

from src.models import Income, Expense, User
from src.security import oauth2_scheme
from src.helpers import get_current_user
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db import income_documents, expense_documents

app = FastAPI()

origins = [
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

DEBUG = True


@app.get('/incomes', response_model=List[Income])
async def get_incomes(skip: int = 0, limit: int = 0, token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    return await income_documents.find({'_user_id': current_user['_id']},
                                       skip=skip, limit=limit).to_list(None)


@app.post('/incomes', response_model=Income)
async def post_income(income: Income, token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    return await create(income, income_documents, current_user['_id'])


@app.delete('/incomes')
async def delete_incomes(token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    await income_documents.delete_many({'_user_id': current_user['_id']})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get('/incomes/{income_id}', response_model=Income)
async def get_income(income_id: str, token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    if (income := await income_documents.find_one({"_id": income_id, '_user_id': current_user['_id']})) is not None:
        return income
    return None


@app.delete('/incomes/{income_id}')
async def delete_income(income_id: str, token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    await income_documents.delete_one({'_id': income_id, '_user_id': current_user['_id']})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put('/incomes/{income_id}', response_model=Income)
async def update_income(income_id: str, income: Income, token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    return await update(income, income_id, income_documents, current_user['_id'])


@app.post('/expenses', response_model=Expense)
async def post_expense(expense: Expense, token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    return await create(expense, expense_documents, current_user['_id'])


@app.get('/expenses', response_model=List[Expense])
async def get_expenses(skip: int = 0, limit: int = 0, token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    return await expense_documents.find({'_user_id': current_user['_id']},
                                        skip=skip, limit=limit).to_list(None)


@app.get('/expenses/{expense_id}', response_model=Expense)
async def get_expense(expense_id: str, token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    if (expense := await expense_documents.find_one({"_id": expense_id, '_user_id': current_user['_id']})) is not None:
        return expense
    return None


@app.delete('/expenses')
async def delete_expenses(token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    await expense_documents.delete_many({'_user_id': current_user['_id']})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete('/expenses/{expense_id}')
async def delete_expense(expense_id: str, token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    await expense_documents.delete_one({'_id': expense_id, '_user_id': current_user['_id']})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put('/expenses/{expense_id}', response_model=Expense)
async def update_expense(expense_id: str, expense: Expense, token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    return await update(expense, expense_id, expense_documents, current_user['_id'])


@app.get('/users/me')
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400,
                            detail='Incorrect username and password',
                            headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token(
        data={"sub": user['_id']}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register")
async def register(user: User, token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    if not current_user['is_admin']:
        raise HTTPException(status_code=400, detail=f'You have no access rights.')
    if (existing_user := await user_documents.find_one({"username": user.username})) is not None:
        raise HTTPException(status_code=400, detail=f'Username "{existing_user["username"]}" already exists.')
    user.joined = datetime.now()
    user.password = get_pwd_hash(user.password)
    user = jsonable_encoder(user)
    user = await user_documents.insert_one(user)
    user = await user_documents.find_one({'_id': user.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=user)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=4999, log_level="info", reload=True)
