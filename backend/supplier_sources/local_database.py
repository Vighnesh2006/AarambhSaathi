"""
Local Database Supplier Source Adapter.
Reads curated suppliers from data/suppliers.json and machines from data/machines.json.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from backend.supplier_sources.base import SupplierSource

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
SUPPLIERS_FILE = DATA_DIR / "suppliers.json"
MACHINES_FILE = DATA_DIR / "machines.json"

class LocalDatabaseSource(SupplierSource):
    """
    Active local supplier repository adapter for curated and verified enterprise datasets.
    """

    @property
    def source_name(self) -> str:
        return "local_database"

    def load_all_suppliers(self) -> List[Dict[str, Any]]:
        if not SUPPLIERS_FILE.exists():
            return []
        try:
            with open(SUPPLIERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def load_all_machines(self) -> List[Dict[str, Any]]:
        if not MACHINES_FILE.exists():
            return []
        try:
            with open(MACHINES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def get_suppliers_for_machine(
        self,
        machine_id: str,
        location: Optional[str] = None,
        budget: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        all_suppliers = self.load_all_suppliers()
        all_machines = self.load_all_machines()
        machine_map = {m["machine_id"]: m for m in all_machines}

        target_machine = machine_map.get(machine_id)
        matched_suppliers = []

        for s in all_suppliers:
            if machine_id in s.get("machine_ids", []):
                rec = dict(s)
                # Attach indicative price bounds from machine if not explicitly set on supplier
                if target_machine:
                    rec["machine_name"] = target_machine.get("machine_name")
                    rec["estimated_price_min"] = target_machine.get("estimated_price_min", 0.0)
                    rec["estimated_price_max"] = target_machine.get("estimated_price_max", 0.0)
                matched_suppliers.append(rec)

        return matched_suppliers
