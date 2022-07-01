from typing import List;

from fastapi import Depends, FastAPI, HTTPException;
from fastapi.responses import JSONResponse;
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm;
from sqlalchemy.orm import Session;

import auth, crud, models, schemas, enum_models;
from database import SessionLocal, engine;

models.Base.metadata.create_all(bind=engine);

app = FastAPI(); 

def get_db():
    db = SessionLocal();
    try:
        yield db;
    finally:
        db.close();


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

def get_user(db, username: str):
    if username in db:
        user_dict = db[username];
        return UserInDb(user_dict);

def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user;

#func has dependency with the oauth2_scheme
# will receive a token as a st from the sub-dependency oauth2_scheme
async def get_current_user(token: str = Depends(auth.oauth2_scheme)):
    user = fake_decode_token(token);
    if not user:
        raise HTTPException(
            status_code=401, detail='UNAUTHORIZED. Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'});
    # returns in a form of a pydantic model
    return user; 

async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if current_user.disables:
        raise HTTPException(
            status_code=400, detail='INACTIVE USER');
    return current_user;

#----------------------------
# AUTH endpoints 
#----------------------------

@app.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    '''takes the username and password from input form
    checks if the username is in db
    if not - raises http exception
    '''
    db_user = auth.get_user_by_username(db=db, username=form_data.username);
    if not db_user:
        raise HTTPException(
            status_code=400,
            # for testing purposes the exceptions differ for username and password
            # irl should be the same
            detail='Incorrect username');
    hashed_password = auth.hashing_password(form_data.password);
    if not hashed_password == db_user.hashed_password:
        raise HTTPException(
            status_code=400,
            detail='Wrong password');
    #token = crud.somefunction... for now just raw data - username itself
    token = db_user.username
    return {'access_token': token, 'token_type': 'bearer'}
    
@app.get('/users/me')
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user; 


##@app.get('/auth')
### dependency provides a str that is assigned to the parameter 'token' of the path op func
##async def read_items(token: str = Depends(oauth2_scheme)):
##    #fastapi looks in the request for that authorization headre
##    # then check if the value is Bearer + some token
##    # returns a token as a string
##    # if ir doesn't see an Authorization header or the value doesn't have a Bearer token,
##    # it will respond with 401: unaothorized (directly)
##    
##    return {'token': token}


#----------------------------
# CREATE endpoints (additional endpoints for admins - downpage)
#----------------------------

#admins only
@app.post('/schedule/manually', status_code=201, response_model=schemas.Schedule)
def create_schedule(input_data: schemas.ScheduleCreateManually, db: Session = Depends(get_db)):
    '''populates the table with provided input
    to be used for creation, not editing data
    if the schedule for this group && semester && day && lesson already exists, returns error
    
    requires manual input of all data, does not support auto generation for fields
    supports enum classes as input options for semester, weekday, lesson and class type
    as a result populates those fields with data matching with primary tables in db

    returns the last inserted info'''
    
    already_exists = crud.check_schedule(db=db, semester=input_data.semester, group=input_data.group, weekday=input_data.weekday, lesson_number=input_data.lesson_number);
    if already_exists:
        raise HTTPException(status_code=400, detail=f'''Schedule already exists! (Group: {input_data.group}; Weekday: {input_data.weekday}; Lesson: {input_data.lesson_number}; Semester: {input_data.semester}. If you want to change schedule - use change form, please!''');
    return crud.fill_schedule_manually(db, input_data);

#admins only 
@app.post('/schedule/auto', status_code=201)
def create_schedule_auto(semester: int,
                         weekday: enum_models.Weekdays,
                         lesson_number: int,
                         group_number: int,
                         module_id: int,
                         class_type: enum_models.ClassTypes,
                         db: Session = Depends(get_db)):
    '''checks if the provided group_number is busy for the provided date/time
    if not, checks if there are teachers to be assigned for provided module and class type:
    - either not busy ones related to this module
        then first empty romm is assigned as a room
    - or those who have the same module and class tipe lesson at provided date/time
        assignes such teacher and room, sets teacher and room busy
    sets group busy and commit new row to schedule database
    if group is busy, or there are no options with teachers, rises HTTPException'''

    group_busy_flag = crud.check_group_busy(db=db, group_number=group_number, weekday=weekday, lesson_number=lesson_number);

    if group_busy_flag == True:
        raise HTTPException(status_code=400, detail=f'''Group {group_number} in already busy on that time! Choose other conditions or use update!''');

    attempt = crud.autofill_schedule(db=db,
                                  semester=semester,
                                  weekday=weekday,
                                  lesson_number=lesson_number,
                                  group_number=group_number,
                                  module_id=module_id,
                                  class_type=class_type);
    if attempt == False:
        raise HTTPException(status_code=400, detail=f'''All teachers are busy for provided module-type pair! Please choose other conditions!''');
    else:
        return attempt; 

#----------------------------
# READ endpoints
#----------------------------

#students and teachers 
@app.get('/schedule/semester_{semester}/group_{group}', response_model=List[schemas.ScheduleGroupResponse])
def read_schedule_by_group(semester: enum_models.Semesters, group: int, skip: int = 0, limit: int = 100, db:Session = Depends(get_db)):
    
    '''takes semester number and group number as an input
    returns all rows from 'schedule' table for provided group and semester'''
    
    schedule = crud.get_schedule_by_group(db=db, semester=semester, group=group);
    return schedule;

#students and teachers 
@app.get('/schedule/semester_{semester}/teacher_{teacher_id}', response_model=List[schemas.ScheduleTeacherResponse])
def read_schedule_by_teacher(semester: enum_models.Semesters, teacher_id: int, skip: int = 0, limit: int = 100, db:Session = Depends(get_db)):

    '''takes semester number and teacher's id as an input
    returns all rows from 'schedule' table for provided teacher and semester'''

    schedule = crud.get_schedule_by_teacher_id(db=db, semester=semester, teacher_id=teacher_id);
    return schedule;

#----------------------------
# UPDATE endpoints
#----------------------------

#admins and teachers
@app.patch('/schedule')
def patch_schedule_row(semester: enum_models.Semesters,
                  group: int,
                  weekday: enum_models.Weekdays,
                  lesson_number: enum_models.Lessons,
                  module: str = None,
                  class_type: enum_models.ClassTypes = None,
                  room: int = None,
                  teacher: str = None,
                  db: Session = Depends(get_db)):
    
    update = crud.update_schedule(db, semester=semester, group=group, weekday=weekday,
                         lesson_number=lesson_number, module=module,
                         class_type=class_type, room=room, teacher=teacher);

    return update; 

#----------------------------
# DELETE endpoints
#----------------------------

#admins only
@app.delete('/schedule', responses={200: {'model': str}})
def delete_schedule(semester: enum_models.Semesters, group: int = None, db:Session = Depends(get_db)):
    
    '''deletes the rows from the table
    requires semester argument, additional argument - group, by default set to null

    if only semester argument is provided - deletes schedule for the named semester for all groups
    if group number is provided as well - deletes only group schedule for the provided semester

    does not affect table existance'''
    
    crud.clear_table(db=db, semester=semester, group=group);
    if group == None:
        return JSONResponse(status_code=200, content={'message': f'Schedule for {semester} semester was successfully deleted for all groups!'})
    else:
        return JSONResponse(status_code=200, content={'message': f'Schedule for group {group} for {semester} semester was successfully deleted!'})
    






