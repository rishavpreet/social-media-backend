from fastapi import HTTPException, status, Response, Depends, APIRouter
from .. import models, schemas, oauth2
from ..loggers import log
from sqlalchemy.orm import Session
from ..database import get_db
from sqlalchemy import func

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=list[schemas.PostOut])
async def get_posts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    search: str | None = "",
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    # cursor.execute("""SELECT * FROM posts;""")
    # posts = cursor.fetchall()
    results = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(
            models.Post.title.contains(search) | models.Post.content.contains(search)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    return results


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_posts(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    #  cursor.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s,%s,%s) RETURNING *""",
    #     (post.title, post.content, post.published),
    # )
    # new_post = cursor.fetchone()
    # conn.commit()
    # log.info(current_user)
    db_posts = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(db_posts)
    db.commit()
    db.refresh(db_posts)
    return db_posts


@router.get("/{id_}", response_model=schemas.PostOut)
async def get_post(
    id_: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    # cursor.execute("""SELECT * FROM posts where id = %s""", (str(id_),))
    # post = cursor.fetchone()

    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id_)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id_} was not found",
        )
    return post


@router.put("/{id_}", response_model=schemas.Post)
async def update_post(
    id_: int,
    updated_post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    # cursor.execute(
    #     """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #     (post.title, post.content, post.published, id_),
    # )
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id_)
    post = post_query.first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id_} does not exist",
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not Authorised to perform requested action",
        )
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    # db.refresh(updated_post)
    return post_query.first()


@router.delete("/{id_}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id_: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id_),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id_)
    post = post_query.first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id_} does not exist",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not Authorised to perform requested action",
        )
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
