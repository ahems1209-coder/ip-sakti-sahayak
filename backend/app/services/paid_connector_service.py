from typing import List
from app.schemas.full_scope import PaidConnectorStatusResponse

class PaidConnectorService:
    @staticmethod
    def list_connectors() -> List[PaidConnectorStatusResponse]:
        return [
            PaidConnectorStatusResponse(
                connector_id="CONN-PATENT-PAID",
                name="Commercial Global Patent Search API (Derwent / Orbit)",
                provider_type="Licensed Patent Database",
                is_connected=False,
                explicit_consent_granted=False,
                auth_status="Connector Architecture Ready (Requires User License Key)",
                disclaimer="Privacy and security controls are implemented; formal legal compliance depends on deployment and organizational assessment."
            ),
            PaidConnectorStatusResponse(
                connector_id="CONN-TK-PAID-SUBSCRIPTION",
                name="CSIR Restricted TKDL Institutional Access Channel",
                provider_type="Authorized Institutional Portal",
                is_connected=False,
                explicit_consent_granted=False,
                auth_status="Connector Architecture Ready (Requires CSIR Non-Disclosure Agreement Credential)",
                disclaimer="Privacy and security controls are implemented; formal legal compliance depends on deployment and organizational assessment."
            ),
            PaidConnectorStatusResponse(
                connector_id="CONN-JOURNAL-PAYWALL",
                name="Phytomedicine & Pharmacognosy Subscription Repository",
                provider_type="Subscription Journal Connector",
                is_connected=False,
                explicit_consent_granted=False,
                auth_status="Connector Architecture Ready (Requires Institution Authentication)",
                disclaimer="Privacy and security controls are implemented; formal legal compliance depends on deployment and organizational assessment."
            )
        ]
