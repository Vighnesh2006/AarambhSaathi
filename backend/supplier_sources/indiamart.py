"""
Placeholder / Mock Adapter for IndiaMART Official Partner API.
Note: Direct unauthorized scraping of IndiaMART is strictly avoided.
When an official partner API key / endpoint is configured, this adapter will activate.
"""

from typing import List, Dict, Any, Optional
from backend.supplier_sources.base import SupplierSource

class IndiaMARTSource(SupplierSource):
    @property
    def source_name(self) -> str:
        return "indiamart_api"

    def get_suppliers_for_machine(
        self,
        machine_id: str,
        location: Optional[str] = None,
        budget: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        # Ready for official API key & OAuth integration
        return []
