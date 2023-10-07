from fastapi import FastAPI, Depends, status, HTTPException
from typing import List
from pydantic import BaseModel
from schema.schema import ArticleSchema, ArticleSchemaOut
from database.database import engine, SessionLocal
from sqlalchemy.orm import Session
import models
import uvicorn
app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/articles/", status_code=status.HTTP_201_CREATED)
def add_article(article: ArticleSchema, db: Session = Depends(get_db)):
    newArticle = models.Article(
        title=article.title, description=article.description)
    db.add(newArticle)
    db.commit()
    db.refresh(newArticle)
    return newArticle


@app.get("/articles/")
def get_articles(db: Session = Depends(get_db)):
    articles = db.query(models.Article).all()
    return articles


@app.get("/articles/{id}", response_model=ArticleSchemaOut, status_code=status.HTTP_200_OK)
def article_details(id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == id).first()
    if article:
        return article
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.put("/articles/{id}", status_code=status.HTTP_202_ACCEPTED)
def article_update(id: int, articel: ArticleSchema, db: Session = Depends(get_db)):
    db.query(models.Article).filter(models.Article.id == id).update({
        'title': articel.title,
        'description': articel.description
    })
    db.commit()
    return {
        'message': 'Data is updated'
    }


@app.delete('/articles/{id}', status_code=status.HTTP_202_ACCEPTED)
def article_delete(id: int, db: Session = Depends(get_db)):
    db.query(models.Article).filter(models.Article.id ==
                                    id).delete(synchronize_session=False)
    db.commit()
    return {
        'message': 'Data is deleted'
    }


if __name__ == "__main__":
    uvicorn.run('main:app', port=8000, log_level="info", reload=True)
