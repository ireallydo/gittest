from typing import List, Union, Dict
from pydantic import BaseModel

import enum_models


# -----------------------------------------------------------------
# auth classes
# -----------------------------------------------------------------

class UserBase(BaseModel):
    email: str;

class UserCreate(UserBase):
    username: str;
    hashed_password: str;
    student_id: Union[str, None] = None;
    admin_id: Union[str, None] = None;
    teacher_id: Union[str, None] = None;

class User(UserBase):
    #id: int;
    username: str; 
    is_active: Union[bool, None] = None;

    class Config:
        orm_mode = True;

class UserInDB(User):
    hashed_password: str; 
# -----------------------------------------------------------------
# administrations classes (create, edit, delete permission)
# -----------------------------------------------------------------

class AdminBase(BaseModel):
    name: str;

class AdminCreate(AdminBase):
    pass

class Admin(AdminBase):
    id: int;
    name: str;
    
    class Config:
        orm_mode = True;

class AdminUser(Admin):
    username: List[User];
    
# -----------------------------------------------------------------
# students classes
# -----------------------------------------------------------------

class StudentBase(BaseModel):
    last_name: str;
    first_name: str;
    second_name: Union[str, None] = None;

class StudentCreate(StudentBase):
    academic_year: int;
    academic_group: int;

class Student(StudentBase):
    id: int;
    academic_year: int;
    academic_group: int;
    
    class Config:
        orm_mode = True;

class StudentUser(Student):
    username: List[User]; 

# -----------------------------------------------------------------
# academic year classes
# -----------------------------------------------------------------

class YearBase(BaseModel):
    number: int;

class YearCreate(YearBase):
    pass;

class Year(YearBase):
    id: int;
    number: int;

    class Config:
        orm_mode = True;

# -----------------------------------------------------------------
# groups classes
# -----------------------------------------------------------------

class GroupBase(BaseModel):
    number: int;

class GroupCreate(GroupBase):
    pass

class Group(GroupBase):
    id: int;
    number: int;

    class Config:
        orm_mode = True;

# -----------------------------------------------------------------
# types_of_classes classes
# -----------------------------------------------------------------

class TypeClassBase(BaseModel):
    name: str;

class TypeClassCreate(TypeClassBase):
    pass;

class TypeClass(TypeClassBase):
    id: int;

    class Config:
        orm_mode = True; 

# -----------------------------------------------------------------
# modules classes
# -----------------------------------------------------------------

class ModuleBase(BaseModel):
    name: str;
    class Config:
        orm_mode = True;

class ModuleCreate(ModuleBase):
    year: int;

class Module(ModuleCreate):
    id: int; 

class ModuleClasses(Module):
    classes: List[TypeClass];

class ModuleSchedule(ModuleBase):
    pass;
    
# -----------------------------------------------------------------
# teachers classes
# -----------------------------------------------------------------

class TeacherBase(BaseModel):
    pass;

class TeacherCreate(TeacherBase):
    last_name: str;
    first_name: str;
    second_name: Union[str, None] = None;
    class Config:
        orm_mode = True;

class Teacher(BaseModel):
    id: int;

    class Config:
        orm_mode = True;

class TeacherModules(Teacher):
    modules: List[Module];

class TeacherSchedule(TeacherBase):
    last_name: str;
    first_name: str;
    second_name: Union[str, None] = None;
    class Config:
        orm_mode = True;

# -----------------------------------------------------------------
# rooms classes
# -----------------------------------------------------------------

class RoomBase(BaseModel):
    number: int;

class RoomCreate(RoomBase):
    pass;

class Room(RoomBase):
    id: int;

    class Config:
        orm_mode = True;

class RoomBusyBase(BaseModel):
    room_id: int;
    weekday: str;
    lesson: int;
    is_busy: bool;

    class Config:
        orm_mode = True; 
    

# -----------------------------------------------------------------
# lesson classes
# -----------------------------------------------------------------

class LessonBase(BaseModel):
    number: int;
    time: str;
    class Config:
        orm_mode = True; 

class LessonCreate(LessonBase):
    pass;

class Lesson(LessonBase):
    id: int;

class LessonSchedule(LessonBase):
    pass;
# -----------------------------------------------------------------
# weekday classes
# -----------------------------------------------------------------

class WeekdayBase(BaseModel):
    name: str;

class WeekdayCreate(WeekdayBase):
    pass;

class Weekday(WeekdayBase):
    id: int;
    
    class Config:
        orm_mode = True;

class WeekdayLessons(WeekdayBase):
    lessons: List[LessonBase];


# -----------------------------------------------------------------
# schedule classes
# -----------------------------------------------------------------

class ScheduleBase(BaseModel):
    class Config:
        orm_mode = True;

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleCreateManually(ScheduleBase):
    semester: enum_models.Semesters;
    group: int;
    weekday: enum_models.Weekdays;
    lesson_number: enum_models.Lessons;
    module_id: int;
    class_type: enum_models.ClassTypes;
    room: int;
    teacher_id: int;

class Schedule(ScheduleBase):
    id: int;
    semester: int;
    group: int;
    weekday: str;
    lesson_number: int;
    module_id: int;
    class_type: str;
    room: int;
    teacher_id: int;

class ScheduleGroupRequest(ScheduleBase):
    semester: enum_models.Semesters;
    group: int;

##class ScheduleGroupResponse(ScheduleBase):
##    group: int;
##    weekday: str;
##    lessons: LessonSchedule;
##    modules: ModuleSchedule;
##    class_type: str;
##    room: int;
##    teachers: TeacherSchedule;

#----------------------

class ScheduleModule(ScheduleBase):
    name: str;

class ScheduleClass(ScheduleBase):
    #teacher_id: int; # for testing
    modules: ScheduleModule;
    class_type: str;
    room: int;

#-----------------------

class ScheduleClassForGroup(ScheduleClass):
    teachers: TeacherSchedule;

class ScheduleLessonForGroup(ScheduleBase):
    number: int;
    time: str;
    schedule: List[ScheduleClassForGroup];

class ScheduleGroupResponse(ScheduleBase):
    name: str;
    lessons: List[ScheduleLessonForGroup];

#------------------------

class ScheduleClassForTeacher(ScheduleClass):
    group: int;

class ScheduleLessonForTeacher(ScheduleBase):
    number: int;
    time: str;
    schedule: List[ScheduleClassForTeacher];

class ScheduleTeacherResponse(ScheduleBase):
    name: str;
    lessons: List[ScheduleLessonForTeacher];

#-----------------------

class Test(BaseModel):
    is_busy: bool; 
