from app.models.response.catalogue import CataloguePage
from app.repositories.catalogue_repository import CatalogueRepository


class CatalogueService:
    def __init__(self, repository: CatalogueRepository) -> None:
        self.repository = repository

    def page(self, resource: str, page: int, size: int) -> CataloguePage:
        rows, total = self.repository.page(resource, page, size)

        return CataloguePage(rows=rows, total=total, page=page, size=size)
