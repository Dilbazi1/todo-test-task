
import asyncio
import httpx
from .config import API_URL, API_USER, API_PASS

class DjangoAPI:
    def __init__(self):
        self.base = API_URL
        self.access_token = None
    
      
    async def login(self):
        async with httpx.AsyncClient() as client:
            for attempt in range(10):
                try:
                    resp = await client.post(
                        f"{self.base}token/",
                        json={"username": API_USER, "password": API_PASS}
                    )
                    resp.raise_for_status()
                    data = resp.json()  # для httpx AsyncClient нормально
                    self.access_token = data["access"]
                    print("Login successful")
                    return
                except httpx.ConnectError:
                    print(f"Backend not ready, retry {attempt + 1}/10...")
                    await asyncio.sleep(2)
                except httpx.HTTPStatusError as e:
                    print(f"Login failed: {e.response.status_code}, {e.response.text}")
                    await asyncio.sleep(2)
            raise RuntimeError("Cannot login after 10 attempts")
    

    async def get_tasks(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base}tasks/", headers=headers)
            resp.raise_for_status()
            return resp.json()
    
    async def get_categories(self):
        if not self.access_token:
            await self.login()
        headers = {"Authorization": f"Bearer {self.access_token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base}categories/", headers=headers)
            resp.raise_for_status()
            return resp.json()

  
   

    
    async def create_task(self, title, description, due_date, category_id=None):
        if not self.access_token:
            await self.login()

        headers = {"Authorization": f"Bearer {self.access_token}"}

        # Формируем payload
        payload = {
            "title": title,
            "description": description,
            "due_date": due_date,
        }

        # Добавляем category_id только если он есть
        if category_id:
            payload["category_id"] = category_id

        print("Sending payload:", payload)  # Логируем payload для проверки

        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base}tasks/", json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()


api = DjangoAPI()