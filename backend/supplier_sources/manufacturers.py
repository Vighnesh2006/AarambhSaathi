"""
Placeholder Adapter for Verified Direct Manufacturers & OEM Networks.
"""

from typing import List, Dict, Any, Optional
from backend.supplier_sources.base import SupplierSource

class ManufacturerSource(SupplierSource):
    @property
    def source_name(self) -> str:
        return "direct_manufacturers"

    def get_suppliers_for_machine(
        self,
        machine_id: str,
        location: Optional[str] = None,
        budget: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        # Ready for direct OEM webhooks/catalog integrations
        return []
