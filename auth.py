from fastapi import Depends, FastAPI, HTTPException;
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm;

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, func;
from sqlalchemy.orm import Session, joinedload, defaultload, join, contains_eager, PropComparator;

import models, schemas, enum_models;

from database import engine, Base;

here is sth to test git


#make a class insnatce
#provides a url where frontend will send username and password
# 'token' is relative url == ./token (relative to api location)
#so the client will use /token to get the token 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token');
# instance is callable, call syntax: oauth2_scheme(some, parameters);

def hashing_password(password: str):
    '''simple example hashing function, not to be user irl'''
    return 'fakehashed' + password;

def decoding_token(token: str):
    pass
    
    
def get_user_by_username(db: Session, username: str):
    db_user = db.query(models.User).where(models.User.username==username).first();
    return db_user;

##def get_current_active_user(db: Session, ):
    
async def get_current_user(token: str = Depends(auth.oauth2_scheme)):
    user = fake_decode_token(token);
    if not user:
        raise HTTPException(
            status_code=401, detail='UNAUTHORIZED. Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'});
    # returns in a form of a pydantic model
    return user; 
