import logging
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO, filename="test_service_offline.log",filemode="w", format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger('')#"uvicorn.info")

"""_summary_

    Сервис генерации ьпохожих треков
    
    Сервис при запуске будет загружать набор похожих треков из файла "similar.parquet" и 
    отдавать список похожих объектов через метод /similar_items.
    
    Код сервиса в файле features_service.py.
"""
class SimilarItems:

    def __init__(self):

        self._similar_items = None

    def load(self, path, **kwargs):
        """
        Загружаем данные из файла
        """
        logger.info(f"Загружаем данные из файла {path}")
        self._similar_items = pd.read_parquet(path, **kwargs)           # ваш код здесь #
        self._similar_items = self._similar_items.set_index("item_id_1") # ваш код здесь #
        logger.info(f"Loaded")
        logger.info(f"Размер датасета: {self._similar_items.shape}")

    def get(self, item_id: int, k: int = 10):
        """
        Возвращает список похожих объектов
        """
        try:
            i2i = self._similar_items.loc[item_id].head(k)
            i2i = i2i[["item_id_2", "score"]].to_dict(orient="list")
        except KeyError:
            logger.error("No recommendations found")
            i2i = {"item_id_2": [], "score": {}}

        return i2i

sim_items_store = SimilarItems()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    logger.info('Загрузка датасета похожих объектов...')
    sim_items_store.load(
        "../recommendations/similar.parquet", # ваш код здесь #
        columns=["item_id_1", "item_id_2", "score"],
    )
    logger.info("Ready!")
    # код ниже выполнится только один раз при остановке сервиса
    yield

# создаём приложение FastAPI
app = FastAPI(title="features", lifespan=lifespan)

@app.post("/similar_items")
async def recommendations(item_id: int, k: int = 10):
    """
    Возвращает список похожих объектов длиной k для item_id
    """
    logger.info(f'Список похожих объектов длиной {k} для item_id={item_id}:')
    i2i = sim_items_store.get(item_id, k)
    logger.info(f'\n{i2i}')

    return i2i 