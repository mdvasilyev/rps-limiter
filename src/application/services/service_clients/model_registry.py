from typing import Any

from httpx import Response
from loguru import logger
from starlette import status

from src.domain.dto import (
    EndpointDTO,
    InstanceDTO,
    ModelDTO,
    PaginatedModelDTO,
    RunningModelsQuery,
    StorageDTO,
    TagDTO,
)
from src.domain.interfaces.service_clients import IModelRegistryClient

from .base import BaseServiceClient


class ModelRegistryClient(BaseServiceClient, IModelRegistryClient):
    @staticmethod
    def _to_model(model_data: dict[str, Any]) -> PaginatedModelDTO:
        """Конвертирует сырые данные в объект ModelInfo"""
        try:
            return PaginatedModelDTO(
                limit=model_data.get("limit"),
                offset=model_data.get("offset"),
                total=model_data.get("total"),
                items=[
                    ModelDTO(
                        configuration=item.get("configuration"),
                        deleted=item.get("deleted"),
                        endpoints=[
                            EndpointDTO(
                                description=endpoint.get("description"),
                                id=endpoint.get("id"),
                                path=endpoint.get("path"),
                            )
                            for endpoint in item.get("endpoints", [])
                        ],
                        hf_repo_id=item.get("hfRepoId"),
                        id=item.get("id"),
                        instance=InstanceDTO(
                            address=item.get("instance").get("address"),
                            id=item.get("instance").get("id"),
                            owner_id=item.get("instance").get("ownerId"),
                            replicas=item.get("instance").get("replicas"),
                        ),
                        name=item.get("name"),
                        status=item.get("status"),
                        storage=StorageDTO(
                            artifact_id=item.get("storage").get("artifactId"),
                            id=item.get("storage").get("id"),
                            revision=item.get("storage").get("revision"),
                            type=item.get("storage").get("type"),
                            uri=item.get("storage").get("uri"),
                        ),
                        tags=[
                            TagDTO(
                                id=tag.get("id"),
                                tag=tag.get("tag"),
                            )
                            for tag in item.get("tags", [])
                        ],
                        type=item.get("type"),
                    )
                    for item in model_data.get("items", [])
                ],
            )
        except Exception as e:
            logger.error("Failed to validate model data: {}. Error: {}", model_data, e)
            raise

    @staticmethod
    async def _check_and_parse_response(response: Response) -> dict[str, Any]:
        """Проверяет успешность ответа и возвращает его JSON-тело."""
        if response.status_code != status.HTTP_200_OK:
            logger.error(
                "ModelRegistry request failed with status {}: {}",
                response.status_code,
                response.text,
            )
            raise Exception("Model registry service is unavailable")
        return response.json()

    async def find_running_models(
        self,
        query: RunningModelsQuery,
    ) -> list[ModelDTO]:
        response = await self._request(
            method="GET",
            path="/running/find-by",
            params=query.to_params(),
        )

        data = await self._check_and_parse_response(response)
        items = data.get("items", [])

        return [self._to_model(item) for item in items]

    async def find_all_running_models(self) -> list[ModelDTO]:
        results: list[ModelDTO] = []

        query = RunningModelsQuery(
            offset=0,
            limit=50,
            sort="name",
        )

        while True:
            items = await self.find_running_models(query)

            if not items:
                break

            results.extend(items)
            query.offset += len(items)

        return results
