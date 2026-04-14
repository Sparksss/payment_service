import httpx
from app.core.config import settings

class BankAPIClient:
    def __init__(self):
        self.base_url = settings.BANK_API_URL
        self.headers = {"X-API-KEY": settings.BANK_API_KEY}
        
    async def stat_acquiring(self, order_id: int, amount: float):
        url = f"{self.base_url}/acquiring_start"
        payload = {"order_id": order_id, "amount": amount}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=settings.BANK_TIMEOUT
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise BankIntegrationError(f"Bank API unavalible: {str(e)}")
        
class BankIntegrationError(Exception):
    pass