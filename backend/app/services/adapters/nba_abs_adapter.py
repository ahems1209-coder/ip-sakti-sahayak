from typing import Dict, Any

class NBAABSAdapter:
    """
    Dedicated Adapter Interface for National Biodiversity Authority (NBA) & ABS Portal:
    - Biological Diversity Act 2002 & Rules 2004
    - NBA Form I / II / III / IV Regulatory ABS Approvals
    - Benefit Sharing Guidelines (2014)
    - State Biodiversity Boards (SBB)
    """
    SOURCE_ID = "IND-NBA-ABS-PORTAL"
    OFFICIAL_URL = "http://nbaindia.org"
    ACCESS_STATUS = "ACCESSIBLE_STATUTORY_ONLY" # Biological Diversity Act 2002 ingested; live Form I filing portal not connected

    @classmethod
    def get_adapter_info(cls) -> Dict[str, Any]:
        return {
            "source_id": cls.SOURCE_ID,
            "adapter_name": "NBAABSAdapter",
            "official_url": cls.OFFICIAL_URL,
            "access_type": "public",
            "access_status": cls.ACCESS_STATUS,
            "source_category": "SIH_PORTAL_SPECIFIED",
            "has_public_search_capability": True,
            "ingested_components": ["Biological Diversity Act 2002 (Sec 3, Sec 6)"],
            "not_currently_accessible": ["Live NBA Form I online application tracking system", "State Biodiversity Board (SBB) localized registers"]
        }
