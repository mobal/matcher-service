from app.repositories.catalogue_repository import CatalogueRepository


class CatalogueService:
    def __init__(self, repository: CatalogueRepository) -> None:
        self.repository = repository

    def page(self, resource: str, page: int, size: int) -> dict:
        rows, total = self.repository.page(resource, page, size)

        return {"rows": rows, "total": total, "page": page, "size": size}
