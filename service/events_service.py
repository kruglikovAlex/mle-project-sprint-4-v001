from fastapi import FastAPI
import logging

logging.basicConfig(level=logging.INFO, filename="test_service_online.log",filemode="w", format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger('')#"uvicorn.info")

"""_summary_

    «Для онлайн-взаимодействия пользователя с каким-то объектом можно использовать 
    список похожих на него объектов»). 
    Event Store. - Сервис, умеющий сохранять и выдавать последние события пользователя.
"""
class EventStore:

    def __init__(self, max_events_per_user=10):

        self.events = {}
        self.max_events_per_user = max_events_per_user

    def put(self, user_id, item_id):
        """
        Сохраняет событие
        """
        logging.info(f'Сохраняем событие: user_id={user_id}, item_id={item_id}')
        user_events = self.events.get(user_id, [])
        logging.info(f'user_events after get: {user_events}')
        self.events[user_id] = [item_id] + user_events[: self.max_events_per_user]
        logging.info(f'self.events[user_id]  = {self.events[user_id] }')

    def get(self, user_id, k):
        """
        Возвращает события для пользователя
        """
        user_events = self.events.get(user_id, [])[:k]
        logging.info(f'Возвращаем {k} событий для пользователя user_id={user_id}:\n{user_events}')
        
        return user_events

events_store = EventStore()

# создаём приложение FastAPI
app = FastAPI(title="events")

@app.post("/put")
async def put(user_id: int, item_id: int):
    """
    Сохраняет событие для user_id, item_id
    """
    logging.info(f"Вызов метода PUT сервиса on-line рекомендаций user_id={user_id}, item_id={item_id}")
    events_store.put(user_id, item_id)

    return {"result": "ok"}

@app.post("/get")
async def get(user_id: int, k: int = 10):
    """
    Возвращает список последних k событий для пользователя user_id
    """

    logging.info(f"Вызов метода GET сервиса on-line рекомендаций user_id={user_id}, k={k}")
    events = events_store.get(user_id, k)
    logging.info(f"result: {events}")
    
    return {"events": events} 