import hashlib
import time
import uuid
from typing import Dict, Any, List, Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("evidence_chain")

class EvidenceChainOfCustody:
    _instance: Optional["EvidenceChainOfCustody"] = None
    
    # In-memory inventory of tracked evidence nodes
    # evidence_id -> EvidenceNode
    _evidence_inventory: Dict[str, Dict[str, Any]] = {}
    
    # Transaction transfers ledger: evidence_id -> list of transfers
    _transfer_ledger: Dict[str, List[Dict[str, Any]]] = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EvidenceChainOfCustody, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def calculate_file_checksum(self, file_content: bytes) -> str:
        """
        Computes SHA256 hashes of raw evidence files for verification.
        """
        return hashlib.sha256(file_content).hexdigest()

    async def register_evidence(
        self, 
        case_id: str, 
        filename: str, 
        file_content: bytes, 
        analyst_id: str,
        device_details: str
    ) -> Dict[str, Any]:
        """
        Logs a newly received piece of forensic media evidence.
        Generates initial SHA256 checksum tags.
        """
        evidence_id = f"evd_{uuid.uuid4().hex[:12]}"
        checksum = self.calculate_file_checksum(file_content)
        
        logger.info(f"Registering forensic evidence: ID={evidence_id}, Name={filename}, Hash={checksum}")

        evidence_node = {
            "evidence_id": evidence_id,
            "case_id": case_id,
            "filename": filename,
            "file_size_bytes": len(file_content),
            "sha256_checksum": checksum,
            "registration_time": time.time(),
            "originator_analyst_id": analyst_id,
            "current_custodian_id": analyst_id,
            "verification_status": "UNPROCESSED"  # UNPROCESSED, VERIFYING, COMPLETED
        }

        # Initialize transfer logs
        genesis_transfer = {
            "transfer_id": f"xfr_{uuid.uuid4().hex[:12]}",
            "timestamp": time.time(),
            "sender_id": "system",
            "receiver_id": analyst_id,
            "purpose": "INITIAL_FORENSIC_ACQUISITION",
            "device_details": device_details,
            "integrity_hash_verified": True
        }

        self._evidence_inventory[evidence_id] = evidence_node
        self._transfer_ledger[evidence_id] = [genesis_transfer]
        
        return evidence_node

    async def transfer_custody(
        self, 
        evidence_id: str, 
        sender_id: str, 
        receiver_id: str, 
        purpose: str, 
        device_details: str,
        expected_checksum: str
    ) -> Dict[str, Any]:
        """
        Logs a custody transfer event.
        Verifies SHA256 hashes match to detect mid-transit tampering.
        """
        node = self._evidence_inventory.get(evidence_id)
        if not node:
            raise ValueError(f"Evidence {evidence_id} not found in system catalogs.")

        # Verify integrity
        if node["sha256_checksum"] != expected_checksum:
            logger.error(f"INTEGRITY FAULT: Custody transfer blocked. Checksums mismatch for evidence: {evidence_id}")
            raise ValueError("Integrity verification failed. File hashes mismatch.")

        transfer = {
            "transfer_id": f"xfr_{uuid.uuid4().hex[:12]}",
            "timestamp": time.time(),
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "purpose": purpose,
            "device_details": device_details,
            "integrity_hash_verified": True
        }

        node["current_custodian_id"] = receiver_id
        self._transfer_ledger[evidence_id].append(transfer)
        
        logger.info(f"Custody transfer processed successfully: Evidence={evidence_id}, NewCustodian={receiver_id}")
        return transfer

    def get_custody_history(self, evidence_id: str) -> List[Dict[str, Any]]:
        """
        Returns full chain of custody log records.
        """
        return self._transfer_ledger.get(evidence_id, [])

    def get_evidence_node(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """
        Gets evidence node attributes.
        """
        return self._evidence_inventory.get(evidence_id)
