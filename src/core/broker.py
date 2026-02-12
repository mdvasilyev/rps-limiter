from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange


def get_rabbitmq_broker(url: str) -> RabbitBroker:
    return RabbitBroker(url=url)


def get_rabbitmq_exchange(exchange: str) -> RabbitExchange:
    return RabbitExchange(name=exchange, durable=True, type=ExchangeType.TOPIC)
