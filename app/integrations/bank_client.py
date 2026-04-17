import uuid
import httpx
from app.core.config import settings

class BankAPIClient:
    def __init__(self):
        self.base_url = settings.BANK_API_URL
        self.headers = {
            "Authorization": f"Bearer {settings.BANK_API_KEY}",
            "Content-Type": "application/json"
        }
        self.timeout = settings.BANK_TIMEOUT

    async def process_payment(self, order_id: int, amount: float) -> str:
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/payments",
                json={"order_id": order_id, "amount": amount}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("transaction_id", str(uuid.uuid4()))
        
    async def refund_payment(self, external_id: str) -> bool:
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/refunds",
                json={"transaction_id": external_id}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("status") == "success"
