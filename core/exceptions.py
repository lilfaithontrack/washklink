from fastapi import HTTPException, status

class LaundryAppException(Exception):
    """Base exception for the laundry app"""
    pass

class UserNotFoundException(LaundryAppException):
    """Raised when user is not found"""
    pass

class InvalidCredentialsException(LaundryAppException):
    """Raised when credentials are invalid"""
    pass

class OrderNotFoundException(LaundryAppException):
    """Raised when order is not found"""
    pass

class PaymentException(LaundryAppException):
    """Raised when payment processing fails"""
    pass

# HTTP Exception handlers
def user_not_found_exception():
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

def invalid_credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

def order_not_found_exception():
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Order not found"
    )