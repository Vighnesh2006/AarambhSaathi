"""
Abstract Base Class for Machinery Supplier Data Sources.
Enables pluggable adapter architecture for local database, IndiaMART, TradeIndia, and Direct Manufacturer APIs.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class SupplierSource(ABC):
    """
    Standardized interface for retrieving machinery supplier records.
    Every adapter must return a standardized list of supplier dictionaries.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Returns the unique identifier/name for this supplier adapter source."""
        pass

    @abstractmethod
    def get_suppliers_for_machine(
        self,
        machine_id: str,
        location: Optional[str] = None,
        budget: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves suppliers providing the given machine_id.
        Standard returned record structure:
        {
            "supplier_id": str,
            "supplier_name": str,
            "machine_ids": List[str],
            "location": str,
            "district": Optional[str],
            "state": str,
            "website": Optional[str],
            "contact": Optional[str],
            "price_range": str,
            "estimated_price_min": float,
            "estimated_price_max": float,
            "capacity": str,
            "installation_available": bool,
            "warranty_available": bool,
            "verified": bool,
            "source": str,
            "source_type": str,  # "verified", "indicative", "estimated", "demo"
            "last_verified": Optional[str]
        }
        """
        pass
