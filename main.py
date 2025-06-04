from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, timezone
from pathlib import Path
import copy  # For deep copying objects
import os
import json

app = FastAPI(title="Simple Splitwise API")

# --- Configuration for Data File ---
# Get the data directory from an environment variable, default to './app_data'
# In Kubernetes, we'll mount a volume here.
DATA_DIR = Path(os.getenv("SPLITWISE_DATA_DIR", "./app_data"))
DATA_FILE = DATA_DIR / "splitwise_data.json"

# Ensure the data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


# --- In-Memory Database (will now be loaded from/saved to file) ---
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


class GreetingResponse(BaseModel):
    message: str


# --- Helper Functions for Data Persistence ---
def load_data():
    global db_users, db_expenses, next_user_id, next_expense_id
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                # Convert keys in db_users back to int, as JSON stores keys as strings
                db_users = {int(k): v for k, v in data.get("users", {}).items()}

                # Convert created_at string back to datetime objects for expenses
                loaded_expenses = data.get("expenses", [])
                db_expenses = []
                for exp_data in loaded_expenses:
                    if "created_at" in exp_data and isinstance(
                        exp_data["created_at"], str
                    ):
                        try:
                            exp_data["created_at"] = datetime.fromisoformat(
                                exp_data["created_at"].replace("Z", "+00:00")
                            )
                        except ValueError:
                            # Handle cases where it might already be a datetime or different format
                            pass
                    db_expenses.append(exp_data)

                next_user_id = data.get("next_user_id", 1)
                next_expense_id = data.get("next_expense_id", 1)
                print(f"Data loaded successfully from {DATA_FILE}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {DATA_FILE}. Starting with empty data.")
        except Exception as e:
            print(
                f"Error loading data from {DATA_FILE}: {e}. Starting with empty data."
            )
    else:
        print(f"Data file {DATA_FILE} not found. Starting with empty data.")


def save_data():
    try:
        # Prepare expenses for JSON serialization (convert datetime to ISO string)
        expenses_to_save = []
        for exp in db_expenses:
            exp_copy = exp.copy()  # Avoid modifying the in-memory db_expenses
            if isinstance(exp_copy.get("created_at"), datetime):
                exp_copy["created_at"] = exp_copy["created_at"].isoformat()
            expenses_to_save.append(exp_copy)

        data_to_save = {
            "users": db_users,
            "expenses": expenses_to_save,
            "next_user_id": next_user_id,
            "next_expense_id": next_expense_id,
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data_to_save, f, indent=4)
        # print(f"Data saved successfully to {DATA_FILE}") # Can be noisy, uncomment for debug
    except Exception as e:
        print(f"Error saving data to {DATA_FILE}: {e}")


# Load data when the application starts
load_data()


# --- Helper Function for User Not Found ---
def get_user_or_404(user_id: int) -> Dict:
    user = db_users.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return user


# --- API Endpoints ---


# == Greeting Endpoint ==
@app.get("/greeting", response_model=GreetingResponse)
async def get_greeting():
    """
    Returns a configurable greeting message.
    """
    # Read the greeting message from an environment variable
    # Provide a default value if the environment variable is not set
    greeting_message = os.getenv("APP_GREETING", "Hello from Simple Splitwise!")
    return {"message": greeting_message}


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
    save_data()
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

    new_expense_dict = expense_in.model_dump()
    new_expense_dict["id"] = next_expense_id
    new_expense_dict["created_at"] = datetime.now(
        timezone.utc
    )  # Store as datetime in memory

    db_expenses.append(new_expense_dict)
    next_expense_id += 1
    save_data()  # Save after modification

    # For the response, ensure created_at is a datetime object as defined by the Expense model
    return Expense(**new_expense_dict)


@app.get("/expenses", response_model=List[Expense])
async def get_expenses():
    """
    Get a list of all expenses.
    Converts created_at strings back to datetime objects for response.
    """
    response_expenses = []
    for exp_data in db_expenses:
        exp_copy = exp_data.copy()
        if isinstance(exp_copy.get("created_at"), str):
            try:
                exp_copy["created_at"] = datetime.fromisoformat(
                    exp_copy["created_at"].replace("Z", "+00:00")
                )
            except ValueError:
                pass  # If it's not a valid ISO string, pass it as is or handle error
        response_expenses.append(
            Expense(**exp_copy)
        )  # Validate against Expense model for response
    return response_expenses


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
