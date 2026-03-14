from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import database
from pydantic import BaseModel
from typing import List

app = FastAPI()

database.init_db()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ExpenseSchema(BaseModel):
    date: str
    category: str
    amount: float
    description: str

    model_config = {"from_attributes": True}

@app.get("/api/expenses")
def get_expenses(db: Session = Depends(get_db)):
    return db.query(database.ExpenseModel).all()

@app.post("/api/expenses")
def add_expense(expense: ExpenseSchema, db: Session = Depends(get_db)):
    db_expense = database.ExpenseModel(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    return {"status": "success"}

@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = db.query(database.ExpenseModel).filter(database.ExpenseModel.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(db_expense)
    db.commit()
    return {"status": "success", "message": f"Deleted expense {expense_id}"}

app.mount("/", StaticFiles(directory="static", html=True), name="static")