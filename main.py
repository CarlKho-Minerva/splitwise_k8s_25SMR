from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import copy  # For deep copying objects

app = FastAPI(title="Simple Splitwise API")

# --- In-Memory Database ---
# We'll use simple dictionaries and lists to store data in memory.
# Data will be lost if the application restarts.
db_users: Dict[int, Dict] = {}
db_expenses: List[Dict] = []
next_user_id = 1
next_expense_id = 1


# --- Pydantic Models (Data Schemas) ---
class UserBase(BaseModel):
    name: str = Field(..., example="Alice")


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int


class ExpenseBase(BaseModel):
    description: str = Field(..., example="Dinner")
    amount: float = Field(..., gt=0, example=50.0)  # Amount must be greater than 0
    paid_by_user_id: int = Field(..., example=1)
    participants: List[int] = Field(
        ..., min_items=1, example=[1, 2]
    )  # At least one participant


class ExpenseCreate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    id: int
    created_at: datetime


class UserBalance(BaseModel):
    user_id: int
    name: str
    balance: float = Field(..., example=25.50)


# --- Helper Functions ---
def get_user_or_404(user_id: int) -> Dict:
    user = db_users.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return user


# --- API Endpoints ---


# == Users ==
@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate):
    """
    Create a new user.
    """
    global next_user_id
    new_user = {"id": next_user_id, "name": user_in.name}
    db_users[next_user_id] = new_user
    next_user_id += 1
    return new_user


@app.get("/users", response_model=List[User])
async def get_users():
    """
    Get a list of all users.
    """
    return list(db_users.values())


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """
    Get details for a specific user.
    """
    return get_user_or_404(user_id)


# == Expenses ==
@app.post("/expenses", response_model=Expense, status_code=status.HTTP_201_CREATED)
async def create_expense(expense_in: ExpenseCreate):
    """
    Add a new expense.
    Ensures the payer and all participants are valid users.
    """
    global next_expense_id

    # Validate payer exists
    get_user_or_404(expense_in.paid_by_user_id)

    # Validate all participants exist
    for user_id in expense_in.participants:
        get_user_or_404(user_id)

    if not expense_in.participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expense must have at least one participant.",
        )

    new_expense = expense_in.model_dump()  # Use model_dump() for Pydantic v2+
    new_expense["id"] = next_expense_id
    new_expense["created_at"] = datetime.utcnow()
    db_expenses.append(new_expense)
    next_expense_id += 1
    return new_expense


@app.get("/expenses", response_model=List[Expense])
async def get_expenses():
    """
    Get a list of all expenses.
    """
    return db_expenses


# == Balances ==
@app.get("/balances", response_model=List[UserBalance])
async def get_balances():
    """
    Calculate and return the current balance for each user.
    A positive balance means the user is owed money.
    A negative balance means the user owes money.
    """
    if not db_users:  # Handle case with no users
        return []

    balances: Dict[int, float] = {user_id: 0.0 for user_id in db_users}

    for expense in db_expenses:
        paid_by_user_id = expense["paid_by_user_id"]
        amount = expense["amount"]
        participants = expense["participants"]

        if (
            not participants
        ):  # Should not happen if POST /expenses validation is correct
            continue

        share_per_participant = amount / len(participants)

        # Payer gets credited the full amount initially
        balances[paid_by_user_id] += amount

        # Each participant (including payer if they participated) is debited their share
        for participant_id in participants:
            if (
                participant_id in balances
            ):  # Ensure participant exists (should be guaranteed by user check)
                balances[participant_id] -= share_per_participant
            # else: might log an inconsistency if data integrity was somehow broken

    user_balances = []
    for user_id, balance_amount in balances.items():
        user_details = db_users.get(user_id)
        if user_details:  # Should always be true if balances keys are from db_users
            user_balances.append(
                {
                    "user_id": user_id,
                    "name": user_details["name"],
                    "balance": round(balance_amount, 2),  # Round to 2 decimal places
                }
            )
    return user_balances


# --- To run the app locally (for testing before Dockerizing) ---
# Use the command: uvicorn main:app --reload
# Then open your browser to http://127.0.0.1:8000/docs
