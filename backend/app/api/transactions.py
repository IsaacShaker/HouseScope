"""
Transactions API endpoints.
Handles CRUD operations for transactions and CSV import functionality.
"""
import csv
import io
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.core.schemas import TransactionCreate, TransactionUpdate, TransactionResponse
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=List[TransactionResponse])
def get_transactions(
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    limit: int = Query(100, le=1000, description="Maximum number of transactions to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get transactions with optional filtering.
    Returns transactions ordered by date (most recent first).
    """
    # Get user's account IDs for security
    user_account_ids = [
        acc.id for acc in db.query(Account).filter(Account.user_id == current_user.id).all()
    ]
    
    query = db.query(Transaction).filter(Transaction.account_id.in_(user_account_ids))
    
    # Apply filters
    if account_id:
        if account_id not in user_account_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this account",
            )
        query = query.filter(Transaction.account_id == account_id)
    
    if category:
        query = query.filter(Transaction.category == category)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    transactions = query.order_by(Transaction.date.desc()).limit(limit).all()
    
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific transaction by ID.
    """
    # Get user's account IDs for security
    user_account_ids = [
        acc.id for acc in db.query(Account).filter(Account.user_id == current_user.id).all()
    ]
    
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.account_id.in_(user_account_ids),
        )
        .first()
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    return transaction


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new transaction.
    
    - **account_id**: ID of the account this transaction belongs to
    - **date**: Transaction date
    - **amount**: Transaction amount (positive for income, negative for expenses)
    - **category**: Transaction category
    - **merchant**: Merchant name (optional)
    - **description**: Transaction description (optional)
    """
    # Verify account belongs to user
    account = (
        db.query(Account)
        .filter(Account.id == transaction_data.account_id, Account.user_id == current_user.id)
        .first()
    )
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    new_transaction = Transaction(
        account_id=transaction_data.account_id,
        date=transaction_data.date,
        amount=transaction_data.amount,
        category=transaction_data.category,
        merchant=transaction_data.merchant,
        description=transaction_data.description,
    )
    
    # Update account balance
    account.balance += transaction_data.amount
    
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return new_transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing transaction.
    """
    # Get user's account IDs for security
    user_account_ids = [
        acc.id for acc in db.query(Account).filter(Account.user_id == current_user.id).all()
    ]
    
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.account_id.in_(user_account_ids),
        )
        .first()
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    # Update account balance if amount changed
    if transaction_data.amount is not None and transaction_data.amount != transaction.amount:
        account = db.query(Account).filter(Account.id == transaction.account_id).first()
        balance_diff = transaction_data.amount - transaction.amount
        account.balance += balance_diff
    
    # Update fields
    update_data = transaction_data.model_dump(exclude_unset=True)
    
    # Convert date string to date object if needed
    if 'date' in update_data and isinstance(update_data['date'], str):
        from datetime import datetime as dt
        update_data['date'] = dt.strptime(update_data['date'], '%Y-%m-%d').date()
    
    for field, value in update_data.items():
        setattr(transaction, field, value)
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a transaction.
    """
    # Get user's account IDs for security
    user_account_ids = [
        acc.id for acc in db.query(Account).filter(Account.user_id == current_user.id).all()
    ]
    
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.account_id.in_(user_account_ids),
        )
        .first()
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    # Update account balance
    account = db.query(Account).filter(Account.id == transaction.account_id).first()
    account.balance -= transaction.amount
    
    db.delete(transaction)
    db.commit()
    
    return None


@router.post("/import-csv/{account_id}")
def import_transactions_csv(
    account_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Import transactions from a CSV file.
    
    Expected CSV format:
    date, amount, category, merchant, description
    2024-01-01, -50.00, groceries, Walmart, Weekly shopping
    2024-01-05, 3000.00, income, Employer, Monthly salary
    
    - Date format: YYYY-MM-DD
    - Amount: Positive for income, negative for expenses
    """
    # Verify account belongs to user
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
    
    # Check file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV",
        )
    
    try:
        # Read CSV file
        contents = file.file.read()
        csv_data = io.StringIO(contents.decode('utf-8'))
        csv_reader = csv.DictReader(csv_data)
        
        imported_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (1 is header)
            try:
                # Parse date
                date = datetime.strptime(row['date'].strip(), '%Y-%m-%d')
                amount = float(row['amount'].strip())
                category = row.get('category', 'uncategorized').strip()
                merchant = row.get('merchant', '').strip() or None
                description = row.get('description', '').strip() or None
                
                # Create transaction
                transaction = Transaction(
                    account_id=account_id,
                    date=date,
                    amount=amount,
                    category=category,
                    merchant=merchant,
                    description=description,
                )
                
                db.add(transaction)
                
                # Update account balance
                account.balance += amount
                
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        db.commit()
        
        return {
            "success": True,
            "imported_count": imported_count,
            "errors": errors if errors else None,
            "message": f"Successfully imported {imported_count} transactions",
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing CSV: {str(e)}",
        )
    finally:
        file.file.close()


@router.get("/categories/list")
def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get list of categories for the current user.
    Returns user-defined categories from the categories table.
    """
    from app.models.category import Category
    
    categories = (
        db.query(Category)
        .filter(Category.user_id == current_user.id)
        .order_by(Category.name)
        .all()
    )
    
    return {"categories": [cat.name for cat in categories]}
