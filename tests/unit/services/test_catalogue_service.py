from typing import cast
from unittest.mock import Mock

from app.models.response.catalogue import CataloguePage, CatalogueRow
from app.services.catalogue_service import CatalogueService


class TestCatalogueService:
    def test_page_maps_repository_result(
        self, catalogue_service: CatalogueService
    ) -> None:
        repository = cast(Mock, catalogue_service.repository)
        repository.page.return_value = ([CatalogueRow(id=1)], 1)

        result = catalogue_service.page("movies", 2, 10)

        repository.page.assert_called_once_with("movies", 2, 10)
        assert result == CataloguePage(
            rows=[CatalogueRow(id=1)], total=1, page=2, size=10
        )
