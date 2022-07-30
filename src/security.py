from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "5bd09dc855a55261a719cbe8ec5cac33178ed07dbe00fef6ed1cce5e65ea2068"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_pwd(pwd, hashed_pwd):
    return pwd_context.verify(pwd, hashed_pwd)


def get_pwd_hash(pwd):
    return pwd_context.hash(pwd)


async def fake_decode_token(token):
    pass


def fake_hash_password(password: str):
    return "fakehashed" + password
