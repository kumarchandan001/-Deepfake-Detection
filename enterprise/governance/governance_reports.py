import time
from typing import Dict, Any, List
from ai_engine.utils.logger import setup_logger
from enterprise.governance.audit_engine import GovernanceAuditEngine
from enterprise.governance.compliance_tracker import ComplianceTracker

logger = setup_logger("governance_reports")

class GovernanceReportGenerator:
    def __init__(self):
        self.auditor = GovernanceAuditEngine()
        self.compliance = ComplianceTracker()

    async def compile_comprehensive_report(self, tenant_id: str, system_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gathers cryptographic audit logs, runs active compliance evaluations, 
        and packages a structured EU AI Act transparency and risk management report.
        """
        logger.info(f"Compiling comprehensive governance package for: {tenant_id}")
        
        # 1. Evaluate compliance status
        compliance_check = await self.compliance.run_compliance_check(tenant_id, system_state)
        
        # 2. Extract tenant specific audit trails
        full_trail = self.auditor.get_audit_trail()
        tenant_trail = [
            block for block in full_trail 
            if block.get("tenant_id") == tenant_id or block.get("tenant_id") == "system"
        ]
        
        # 3. Check tamper-proof status (verify cryptographic block hash linking)
        tamper_free = self.auditor.verify_ledger_integrity()

        report_payload = {
            "report_id": f"gov_rep_{tenant_id}_{int(time.time())}",
            "generated_at": time.time(),
            "tenant_id": tenant_id,
            "verification_metrics": {
                "ledger_tamper_free": tamper_free,
                "forensic_entries_logged": len(tenant_trail)
            },
            "compliance_summary": {
                "overall_status": compliance_check["compliance_status"],
                "score_percentage": compliance_check["compliance_score_percentage"]
            },
            "eu_ai_act_risk_profile": {
                "system_classification": "High-Risk AI System (Biometric identification & forensics)",
                "governance_adherence_index": round(compliance_check["compliance_score_percentage"] / 100.0, 2),
                "required_transparency_notices": [
                    "User informed of synthetic media checks",
                    "Forensic metadata analysis models versioned and logged",
                    "Option to review automated decisions provided"
                ]
            },
            "recent_audit_trail": tenant_trail[-50:]  # include last 50 entries
        }

        # Log report generation event
        await self.auditor.log_event(
            tenant_id=tenant_id,
            action="GOVERNANCE_REPORT_COMPILED",
            resource_details=f"Compiled Report ID: {report_payload['report_id']}. Ledger Integrity Verified: {tamper_free}"
        )

        return report_payload
