from typing import Dict, Any, Optional
from ai_engine.utils.logger import setup_logger
from enterprise.governance.audit_engine import GovernanceAuditEngine

logger = setup_logger("policy_enforcer")

class PolicyViolationException(Exception):
    def __init__(self, message: str, policy_key: str):
        super().__init__(message)
        self.policy_key = policy_key
        self.message = message

class PolicyEnforcer:
    def __init__(self):
        self.auditor = GovernanceAuditEngine()

    async def validate_operation(
        self, 
        tenant_id: str, 
        action: str, 
        payload: Dict[str, Any],
        active_policies: Dict[str, Any]
    ) -> bool:
        """
        Validates an operational check against configurable policies:
        - "require_liveness_verification" (reject if spoof protection check is absent)
        - "minimum_confidence_threshold" (block reports below target delta limits)
        - "prohibit_anonymous_uploads" (prevent unlogged client requests)
        """
        logger.info(f"Enforcing policy checks: Tenant={tenant_id}, Action={action}")
        
        # Policy 1: Require Liveness Verification
        if active_policies.get("require_liveness_verification", False):
            if action == "media_verification" and not payload.get("liveness_verified", False):
                err_msg = "Policy Violation: Media verification rejected. Liveness verification check is mandatory."
                await self.auditor.log_event(
                    tenant_id=tenant_id,
                    action="POLICY_VIOLATION",
                    resource_details=f"Policy: require_liveness_verification | {err_msg}"
                )
                raise PolicyViolationException(err_msg, "require_liveness_verification")

        # Policy 2: Minimum Model Confidence Threshold
        min_conf = active_policies.get("minimum_confidence_threshold", 0.0)
        if min_conf > 0.0:
            confidence = payload.get("model_confidence", 1.0)
            if confidence < min_conf:
                err_msg = f"Policy Violation: Verification output blocked. Confidence ({confidence:.2f}) is below minimum limit ({min_conf:.2f})."
                await self.auditor.log_event(
                    tenant_id=tenant_id,
                    action="POLICY_VIOLATION",
                    resource_details=f"Policy: minimum_confidence_threshold | {err_msg}"
                )
                raise PolicyViolationException(err_msg, "minimum_confidence_threshold")

        # Policy 3: Prohibit Anonymous Client IPs
        if active_policies.get("prohibit_anonymous_uploads", False):
            if not payload.get("client_ip"):
                err_msg = "Policy Violation: Anonymous upload rejected. Authenticated Client IP address header required."
                await self.auditor.log_event(
                    tenant_id=tenant_id,
                    action="POLICY_VIOLATION",
                    resource_details=f"Policy: prohibit_anonymous_uploads | {err_msg}"
                )
                raise PolicyViolationException(err_msg, "prohibit_anonymous_uploads")

        logger.info(f"Policy validations succeeded for action '{action}'.")
        return True
