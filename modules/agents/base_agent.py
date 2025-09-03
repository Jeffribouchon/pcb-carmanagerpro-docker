from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Classe abstraite pour tous les agents IA
    """

    @abstractmethod
    def extract_criteria(self, query: str) -> dict:
        """Analyse la requête utilisateur et retourne des critères structurés"""
        pass

    @abstractmethod
    def search(self, criteria: dict):
        """Recherche dans Odoo ou autre source"""
        pass
