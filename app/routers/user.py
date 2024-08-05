from fastapi import HTTPException, status, Response, Depends, APIRouter
from .. import models, schemas, utils
from ..loggers import log
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    ## hash the password
    user.password = utils.hash(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id_}", response_model=schemas.UserOut)
async def get_user(id_: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id_).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id_} does not exist",
        )
    return user
