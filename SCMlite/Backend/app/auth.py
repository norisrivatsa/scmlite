import jwt 
from jwt import ExpiredSignatureError, InvalidTokenError,PyJWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from app.database import get_user_database
from passlib.context import CryptContext
from fastapi import HTTPException, Header

# Configurations
SECRET_KEY = "10d2f9c16e1db93f69635484a2880824"  
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

utc_now = datetime.now(timezone.utc)

def hash_password(password: str) -> str:
    # Hashes the user's password using passlib's bcrypt.
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Verifies the plain password against the bcrypt hash using passlib.
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    # Creates an access token using the JWT algorithm.
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(db, email: str):
    # Fetches a user from the database.
    return db["users"].find_one({"email": email}, {"username" : 1, "email" : 1 , "hashed_password" : 1 ,"admin" : 1})


def verify_user(db: get_user_database, email: str, password: str) -> bool:
    user = db["users"].find_one({"email": email})
    if user and pwd_context.verify(password, user["hashed_password"]):
        return True
    return False

def verify_token(token: str) -> bool:
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True  
    except (ExpiredSignatureError, InvalidTokenError):
        return False  


def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")