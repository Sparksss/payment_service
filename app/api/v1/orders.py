from app.api.schemas.order import OrderRead

@router.get("/{order_id}", response_model=OrderRead)
async def read_order(order_id: int ,db: Async)