# rps-limiter

Скейлер

Связанные сервисы:
    1. ModelRegistry - эндпоинт "/v2/models/running/find-by" получение актуальных данных о запущеных моделях
    2. ModelDispatcher - эндпоинты "/v1/command/uninstall", "/v1/command/scale" и /v1/saga/{id} - управление жизненным циклом моделей
    3. BookingService - эндпоинты "/api/v1/reservations", "/api/v1/reservations/{id}" и/или /api/v1/reservations/{id}/slot-usage/{slot_id}
    4. Entrypoint - эндпоинт /metrics - базовое представление прометеус метрик
    5. Notificator - сервис информирования пользователей о намерениях и действиях с моделями (см. ниже)

# Стек:
    1. faststream[rabbit]
    2. Sqlalchemy + asyncpg + alembic. Для сервиса отдельная схема, задается в переменных окружения.  Миграции. (Используем связку postgres + pgbouncer)
    3. PydanticSettings, Pydantic
    4. Dishka
    5. Loguru
    6. prometheus-client
    7. httpx/aiohttp

# Линтеры 

Длина строк до 120 символов

    1. black
    2. flake8
    3. rufus (по желанию)
    4. mypy (по желанию, по очень большому желанию - иногда из-за него очень много оверхеда)

# Обязательные файлы
    1. DockerFile
    2. docker-compose.yaml
    3. README.md
    4. requirements.txt (можно и в pyptoject.toml (uv) хранить зависимости, но файл должен быть)
    5. example.env
    6. Makefile (опционально)
    7. .gitignore
    8. .dockerignore

# Дополнительные реализации
    1. Health check сервиса
    2. protmetheus метрики сервиса 
        а) Сколько моделей сейчас наблюдаются (опционально)
        б) Сколько моделей сейчас в работе (деление на scale/descale/uninstall/booking-cancel) (опционально)
        в) Сколько моделей было отменено (опционально)
        г) Количество критичных ошибок, на которые будет тригериться alarm
    3. Примеры графиков в графане (опционально)
    4. Makefile (up, down, restart, logs)

# Переменные окружения
    
Все константы должны задаваться через переменные окружения

# Требования по коду

    1. Типизация
    2. Использование DI
    3. Тесты
    4. Точка входа main.py (не cli)
    5. Исходный код в project/src
    6. Применение миграций только в ручную (alembic upgrade head), а в docker compose через отдельный контейнер

# Цель

Управлять жизненным циклом в рамках периода.
    1. При повышеном RPS - scale up
    2. При пониженом RPS - scale down
    2. При неиспользовании модели времени
        а) N - Y времени - предупреждение об отменен бронирования через event в нотификатор
        б) N времени - unbooking последующих бронирований (подряд или всех такой модели должно тянуться из конфига (ALL/IN_ROW)), uninstall (опционально, так же флаг из конфига), информирование через event в нотификатор


# Notifier Events

1. reservation_started_reminder_queue

```shell
@router.subscriber(
    queue=RabbitQueue(
        "reservation_started_reminder_queue",
        durable=True,
        routing_key="models.deployed.successfully",
    ),
    exchange=RabbitExchange(
        EXCHANGE_NAME,
        type=ExchangeType.TOPIC,
        durable=True,
    ),
)
```

Модель данных

```shell
class ReservationStartedReminder(BaseModel):
    user_id: str
    user_name: str
    user_email: str
    model_ids: list[str]
    model_names: list[str]
    reservation_ids: list[str]
```

2. No use (Не реализована в полном виде. Предварительно выглядит следующим образом)

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_serializer


class UserInfo(BaseModel):
    id: UUID
    email: str

    @field_serializer("id")
    def serialize_id(self, id: UUID, _info):
        return str(id)


class BaseEvent(BaseModel):
    event_version: str = "1.0"
    event_type: str
    occurred_at: datetime
    user: UserInfo

    @field_serializer("occurred_at")
    def serialize_occurred_at(self, occurred_at: datetime, _info):
        return (
            occurred_at.isoformat() + "Z"
            if occurred_at.tzinfo is None
            else occurred_at.isoformat()
        )

class ReservationNoUse(BaseEvent):
    event_type: str = "reservation.no_use"
    reservation: ReservationInfo
```
