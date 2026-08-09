import asyncio, json
from app.services import rawg_service

async def run():
    try:
        data = await rawg_service.get_game_detail(447530)
        print(json.dumps(data.get("name")))
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(run())
