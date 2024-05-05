from passlib.context import CryptContext

# last supported version, bcrypt==4.0.1
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
