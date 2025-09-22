# Подготовка виртуальной машины

## Склонируйте репозиторий

Склонируйте репозиторий проекта:

```
git clone https://github.com/yandex-praktikum/mle-project-sprint-4-v001.git
```

## Активируйте виртуальное окружение

Используйте то же самое виртуальное окружение, что и созданное для работы с уроками. Если его не существует, то его следует создать.

Создать новое виртуальное окружение можно командой:

```
python3 -m venv env_recsys_start
```

После его инициализации следующей командой

```
. env_recsys_start/bin/activate
```

установите в него необходимые Python-пакеты следующей командой

```
pip install -r requirements.txt
```

### Скачайте файлы с данными

Для начала работы понадобится три файла с данными:
- [tracks.parquet](https://storage.yandexcloud.net/mle-data/ym/tracks.parquet)
- [catalog_names.parquet](https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet)
- [interactions.parquet](https://storage.yandexcloud.net/mle-data/ym/interactions.parquet)
 
Скачайте их в директорию локального репозитория. Для удобства вы можете воспользоваться командой wget:

```
wget https://storage.yandexcloud.net/mle-data/ym/tracks.parquet

wget https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet

wget https://storage.yandexcloud.net/mle-data/ym/interactions.parquet
```

## Запустите Jupyter Lab

Запустите Jupyter Lab в командной строке

```
jupyter lab --ip=0.0.0.0 --no-browser
```

# Расчёт рекомендаций

Код для выполнения первой части проекта находится в файле `recommendations.ipynb`. Изначально, это шаблон. Используйте его для выполнения первой части проекта.

# Сервис рекомендаций
Каждая инструкция выполняется из директории репозитория mle-project-sprint-4-v001
Если необходимо перейти в поддиректорию, напишите соотвесвтующую команду

Код сервиса рекомендаций находится в файле `recommendations_service.py`.

# Инструкции для запуска сервиса рекомендаций
```python

cd service
# запуск сервиса off-line рекомендаций
uvicorn features_service:app --reload --port 8081 --host 0.0.0.0
# запуск сервиса on-line рекомендаций
uvicorn events_service:app --reload --port 8082 --host 0.0.0.0
# запуск сервиса рекомендаций
uvicorn recommendation_service:app --reload --port 8080 --host 0.0.0.0
# 
```
# Инструкции для тестирования сервиса

Код для тестирования сервиса находится в файле `test_service.py`.

```python

# запуск кода для тестирования
python3 test_service.py
#
```

### Пример curl-запроса к off-line сервису
```bash
curl -X 'POST' \
  'http://localhost:8081/similar_items?item_id=53404&k=10' \
  -H 'accept: application/json' \
  -d ''
```
### Пример curl-запроса PUT к on-line сервису
```bash
curl -X 'POST' \
  'http://localhost:8082/put?user_id=1291250&item_id=34308497' \
  -H 'accept: application/json' \
  -d ''
```

### Пример curl-запроса GET к on-line сервису
```bash
curl -X 'POST' \
  'http://localhost:8082/get?user_id=1291250&k=10' \
  -H 'accept: application/json' \
  -d ''
```

### Пример curl-запроса к сервису рекомендаций для получения похожих объектов (вызов сервера off-line)
```bash
curl -X 'POST' \
  'http://localhost:8080/recommendations_offline?user_id=1291250&k=100' \
  -H 'accept: application/json' \
  -d ''
```

### Пример curl-запроса к сервису рекомендаций для получения объектов на основании текущего взаимодействия с пользователем (вызов сервера on-line)
```bash
curl -X 'POST' \
  'http://localhost:8080/recommendations_online?user_id=1291250&k=100' \
  -H 'accept: application/json' \
  -d ''
```

### Пример curl-запроса к сервису рекомендаций для получения полных рекомендаций
```bash
curl -X 'POST' \
  'http://localhost:8080/recommendations?user_id=1291250&k=100' \
  -H 'accept: application/json' \
  -d ''
```
# Лог файлы:
/service/test_service.log - логирование результатов тестирования
/service/test_service_offline.log - логирование работы сервиса off-line рекомендаций
/service/test_service_online.log - логирование работы сервиса on-line рекомендаций
/service/test_service_recommend.log - логирование различных методов сервиса рекомендаций (отдельно)