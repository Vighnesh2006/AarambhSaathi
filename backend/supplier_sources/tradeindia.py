"""
Placeholder / Mock Adapter for TradeIndia Official Partner API.
"""

from typing import List, Dict, Any, Optional
from backend.supplier_sources.base import SupplierSource

class TradeIndiaSource(SupplierSource):
    @property
    def source_name(self) -> str:
        return "tradeindia_api"

    def get_suppliers_for_machine(
        self,
        machine_id: str,
        location: Optional[str] = None,
        budget: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        # Ready for official TradeIndia API integration
        return []
