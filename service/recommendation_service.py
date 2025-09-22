import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager
from recommendations import Recommendations
import requests

features_store_url = "http://127.0.0.1:8081"
events_store_url = "http://127.0.0.1:8082" 

logging.basicConfig(level=logging.DEBUG, filename="test_service_recommend.log",filemode="w", format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger('')#"uvicorn.error")
rec_store = Recommendations()

def dedup_ids(ids):
    """
    Дедублицирует список идентификаторов, оставляя только первое вхождение
    """
    logger.info(f"Дедублицируем список идентификаторов, оставляя только первое вхождение")
    seen = set()
    ids = [id for id in ids if not (id in seen or seen.add(id))]

    return ids

@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    logger.info(f"Personal recommendation loading")
    rec_store.load(
        "personal",
        "../recommendations/recommendations.parquet",
        columns=["user_id", "item_id", "rank"],
    )
    
    logger.info(f"Top-popular recommendation loading")
    rec_store.load(
        "default",
        "../recommendations/top_popular.parquet",
        columns=["item_id", "rank"],
    )
    
    logger.info("Starting")
    yield
    rec_store.stats() # этот код выполнится только один раз при остановке сервиса
    logger.info("Stopping")
    
# создаём приложение FastAPI
app = FastAPI(title="recommendations", lifespan=lifespan)
#app.add_middleware(Analytics, api_key="http://127.0.0.1:8000/stat")  # Add middleware

@app.post("/stats")
async def recommendations_stats():
    """
    Статистику в логер
    """

    rec_store.stats()
    
@app.post("/recommendations_offline")
async def recommendations_offline(user_id: int, k: int = 100):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """
    logger.info(f"Возвращаем список off-line рекомендаций длиной {k} для пользователя {user_id}")
    recs = []        
    recs = rec_store.get(user_id=user_id, k=k)
    logger.info(f"Off-line рекомендации: {recs}")
    
    return {"recs": recs} 


@app.post("/recommendations_online")
async def recommendations_online(user_id: int, k: int = 100):
    """
    Возвращает список онлайн-рекомендаций длиной k для пользователя user_id
    """
    logger.info(f"Возвращаем список on-line рекомендаций длиной {k} для пользователя {user_id}")
    
    headers = {"Content-type": "application/json", "Accept": "text/plain"}

    # получаем последнее событие пользователя
    logger.info(f"- получаем последнее {k} событий пользователя {user_id}")
    
    params = {"user_id": user_id, "k": k}
    logger.info(f"- оправляем запрос на сервер on-line рекомендаций {events_store_url} \n   c параметрами: {params}")
    resp = requests.post(events_store_url + "/get", headers=headers, params=params)
    
    events = resp.json()
    events = events["events"]
    logger.info(f"- ответ сервера on-line рекомендаций: количество={len(events)}, рекомендации - {events}")
    
    # получаем список похожих объектов
    """if len(events) > 0:
        item_id = events[0]
        params = {"item_id": item_id, "k": k}
        resp = requests.post(features_store_url + "/similar_items", headers=headers, params=params)
        item_similar_items = resp.json()
        print("item_similar_items", item_similar_items)
        item_similar_items = item_similar_items["item_id_2"]
        print("item_similar_items", item_similar_items)
        recs = item_similar_items[:k]
    else:
        recs = []"""
        
    print("len(events)=",len(events))
    # получаем список айтемов, похожих на последние k, с которыми взаимодействовал пользователь
    logger.info(f"Получаем список айтемов, похожих на последние {k}, с которыми взаимодействовал пользователь:")
    if len(events) > 0:
        items = []
        scores = []
        for item_id in events:
            # для каждого item_id получаем список похожих в item_similar_items
            #=======================
            logger.info(f"- для каждого item_id={item_id} получаем список похожих в item_similar_items")
            
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            params = {"item_id": item_id, "k": k}
            
            logger.info(f"- оправляем запрос на сервер off-line рекомендаций {features_store_url} \n   c параметрами: {params}")
            resp = requests.post(features_store_url +"/similar_items", headers=headers, params=params)
            
            item_similar_items = resp.json()
            logger.info(f"- ответ сервера off-line рекомендаций: количество={len(item_similar_items)}, рекомендации - {item_similar_items}")
            
            items += item_similar_items["item_id_2"]
            scores += item_similar_items["score"]
        # сортируем похожие объекты по scores в убывающем порядке
        # для старта это приемлемый подход
        logger.info(f"- сортируем похожие объекты по scores в убывающем порядке")
        combined = list(zip(items, scores))
        combined = sorted(combined, key=lambda x: x[1], reverse=True)[:k]
        combined = [item for item, _ in combined]
        logger.info(f"   результат: {combined}")
        
        # удаляем дубликаты, чтобы не выдавать одинаковые рекомендации
        logger.info(f"- удаляем дубликаты, чтобы не выдавать одинаковые рекомендации")
        recs = dedup_ids(combined)
        logger.info(f"   результат: {recs}")
    else:
        recs = []
    
    return {"recs": recs} 

@app.post("/recommendations")
async def recommendations(user_id: int, k: int = 100):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """
    logger.info(f"Возвращаем список all рекомендаций длиной {k} для пользователя {user_id}:")
    
    logger.info(f'- получение списока off-line рекомендаций длиной {k} для пользователя {user_id}')
    recs_offline = await recommendations_offline(user_id, k)
    logger.info(f'- получение списока on-line рекомендаций длиной {k} для пользователя {user_id}')
    recs_online = await recommendations_online(user_id, k)

    recs_offline = recs_offline["recs"]
    recs_online = recs_online["recs"]
    
    logger.info(f"User {user_id}: получено {len(recs_online)} онлайн и {len(recs_offline)} офлайн рекомендаций")

    recs_blended = []

    min_length = min(len(recs_offline), len(recs_online))
    # чередуем элементы из списков, пока позволяет минимальная длина
    logger.info(f"- чередуем элементы из списков, пока позволяет минимальная длина {min_length}")
    for i in range(min_length):
        recs_blended.append(recs_online[i])
        recs_blended.append(recs_offline[i])
    logger.info(f"/n{recs_blended}")
                
    # добавляем оставшиеся элементы в конец
    logger.info("- добавляем оставшиеся элементы в конец")
    if len(recs_online) > min_length:
        recs_blended.extend(recs_online[min_length:])
    if len(recs_offline) > min_length:
        recs_blended.extend(recs_offline[min_length:])
    logger.info(f"/n{recs_blended}")
    
    # удаляем дубликаты
    logger.info("- удаляем дубликаты")
    recs_blended = dedup_ids(recs_blended)
    logger.info(f"/n{recs_blended}")
    
    # оставляем только первые k рекомендаций
    logger.info("- оставляем только первые k рекомендаций")
    recs_blended = recs_blended[:k]
    logger.info(f"/n{recs_blended}")

    return {"recs": recs_blended} 