from app.scrapers.base import BaseSourceAdapter


class DisabledSourceAdapter(BaseSourceAdapter):
    name = "disabled"

    def search(self, category: str, location: str):
        return []
