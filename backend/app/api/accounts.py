"""
Accounts API endpoints.
Handles CRUD operations for financial accounts (checking, savings, credit cards, loans).
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import AccountCreate, AccountUpdate, AccountResponse
from app.models.account import Account
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("", response_model=List[AccountResponse])
def get_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all accounts for the current user.
    Returns list of accounts with current balances.
    """
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific account by ID.
    User can only access their own accounts.
    """
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == current_user.id)
        .first()
    )
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    return account


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new financial account.
    
    - **account_type**: checking, savings, credit, loan, investment
    - **institution_name**: Bank or institution name
    - **account_name**: Custom name for the account
    - **balance**: Current balance
    - **credit_limit**: Optional, for credit accounts
    """
    new_account = Account(
        user_id=current_user.id,
        account_type=account_data.account_type,
        institution_name=account_data.institution_name,
        account_name=account_data.account_name,
        balance=account_data.balance,
        credit_limit=account_data.credit_limit,
        interest_rate=account_data.interest_rate,
    )
    
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    
    return new_account


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing account.
    User can only update their own accounts.
    """
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == current_user.id)
        .first()
    )
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    # Update fields if provided
    update_data = account_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    
    db.commit()
    db.refresh(account)
    
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete an account.
    User can only delete their own accounts.
    """
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == current_user.id)
        .first()
    )
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    db.delete(account)
    db.commit()
    
    return None


@router.get("/summary/net-worth")
def get_net_worth(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Calculate total net worth (assets - liabilities).
    
    Assets: checking, savings, investment accounts (positive balance)
    Liabilities: credit cards (negative balance), loans (negative balance)
    """
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    
    assets = 0.0
    liabilities = 0.0
    
    for account in accounts:
        if account.account_type in ["checking", "savings", "investment"]:
            assets += account.balance
        elif account.account_type in ["credit", "loan"]:
            # Credit and loan balances are typically negative
            liabilities += abs(account.balance)
    
    net_worth = assets - liabilities
    
    return {
        "assets": assets,
        "liabilities": liabilities,
        "net_worth": net_worth,
        "account_count": len(accounts),
    }
