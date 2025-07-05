from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePaymentGateway(ABC):
    """Abstract base class for payment gateways"""
    
    @abstractmethod
    async def initiate_payment(self, amount: float, order_id: int, return_url: str = None) -> Dict[str, Any]:
        """Initiate a payment transaction"""
        pass
    
    @abstractmethod
    async def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Verify a payment transaction"""
        pass
    
    @abstractmethod
    async def handle_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment gateway callback"""
        pass