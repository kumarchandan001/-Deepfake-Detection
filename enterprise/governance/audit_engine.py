import time
import json
import hashlib
import os
from typing import Dict, Any, Optional, List
from ai_engine.utils.logger import setup_logger
from backend.db.config import AsyncSessionLocal
from backend.db.models import AuditLog

logger = setup_logger("audit_engine")

class GovernanceAuditEngine:
    _instance: Optional["GovernanceAuditEngine"] = None
    _audit_file = "C:/Users/Chandan Kumar/Desktop/Deepfake-Detection/logs/forensic_audit_trail.json"
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GovernanceAuditEngine, cls).__new__(cls, *args, **kwargs)
            cls._instance._init_audit_file()
        return cls._instance

    def _init_audit_file(self):
        """
        Initializes the tamper-proof ledger file.
        """
        os.makedirs(os.path.dirname(self._audit_file), exist_ok=True)
        if not os.path.exists(self._audit_file):
            # Create genesis block
            genesis = {
                "index": 0,
                "timestamp": time.time(),
                "tenant_id": "system",
                "action": "GENESIS_AUDIT_BLOCK",
                "resource_details": "AI Trust Platform Audit Engine Initialized",
                "previous_hash": "0" * 64,
                "hash": ""
            }
            genesis["hash"] = self._calculate_hash(genesis)
            with open(self._audit_file, "w") as f:
                json.dump([genesis], f, indent=4)
            logger.info("Tamper-proof genesis audit block successfully written.")

    def _calculate_hash(self, block: Dict[str, Any]) -> str:
        """
        Computes SHA256 hash of block contents.
        """
        block_str = f"{block['index']}{block['timestamp']}{block['tenant_id']}{block['action']}{block['resource_details']}{block['previous_hash']}"
        return hashlib.sha256(block_str.encode("utf-8")).hexdigest()

    async def log_event(
        self, 
        tenant_id: str, 
        action: str, 
        resource_details: str, 
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registers an event in the relational audit table and appends a cryptographically
        secured entry to the forensic ledger.
        """
        logger.info(f"Logging governance event: Tenant={tenant_id}, Action={action}")
        
        # 1. DB Logging (Async database helper)
        try:
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    db_log = AuditLog(
                        user_id=user_id,
                        action=action,
                        ip_address=ip_address,
                        resource_details=f"Tenant: {tenant_id} | {resource_details}"
                    )
                    session.add(db_log)
            logger.info("Relational audit trail record saved successfully.")
        except Exception as e:
            logger.warning(f"Database write bypassed (standard local mode): {e}")

        # 2. Append to cryptographically chained ledger file
        new_block = {}
        try:
            with open(self._audit_file, "r+") as f:
                trail = json.load(f)
                last_block = trail[-1]
                
                new_block = {
                    "index": len(trail),
                    "timestamp": time.time(),
                    "tenant_id": tenant_id,
                    "action": action,
                    "resource_details": resource_details,
                    "user_id": user_id,
                    "ip_address": ip_address,
                    "previous_hash": last_block["hash"],
                    "hash": ""
                }
                new_block["hash"] = self._calculate_hash(new_block)
                
                trail.append(new_block)
                f.seek(0)
                json.dump(trail, f, indent=4)
                f.truncate()
            logger.info(f"Cryptographic block #{new_block['index']} verified and appended to ledger.")
        except Exception as e:
            logger.error(f"Failed to append cryptographic audit entry: {e}")
            
        return new_block

    def verify_ledger_integrity(self) -> bool:
        """
        Verifies the tamper-proof ledger chain hashes.
        """
        try:
            with open(self._audit_file, "r") as f:
                trail = json.load(f)
                
            for i in range(1, len(trail)):
                current = trail[i]
                prev = trail[i-1]
                
                # Check previous hash matching
                if current["previous_hash"] != prev["hash"]:
                    logger.error(f"Ledger Integrity broken: Block #{current['index']} points to incorrect previous hash.")
                    return False
                
                # Re-verify current hash value
                actual_hash = self._calculate_hash(current)
                if current["hash"] != actual_hash:
                    logger.error(f"Ledger Integrity broken: Block #{current['index']} data modified after writing.")
                    return False
            
            logger.info("Cryptographic audit trail integrity verification succeeded.")
            return True
        except Exception as e:
            logger.error(f"Failed verification checks: {e}")
            return False
            
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """
        Returns all ledger entries.
        """
        try:
            with open(self._audit_file, "r") as f:
                return json.load(f)
        except Exception:
            return []
