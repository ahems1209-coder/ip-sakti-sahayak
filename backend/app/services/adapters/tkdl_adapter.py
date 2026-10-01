from typing import Dict, Any, List
from app.schemas.source import RetrievalResult

class TKDLAdapter:
    """
    Dedicated Adapter for Traditional Knowledge Digital Library (TKDL).
    Handles public institutional overview pages while explicitly representing 
    access restrictions for internal formulation databases.
    """
    SOURCE_ID = "IND-TKDL-GUIDELINES"
    OFFICIAL_URL = "https://www.tkdl.res.in"
    ACCESS_STATUS = "RESTRICTED_MIXED"

    @classmethod
    def get_adapter_info(cls) -> Dict[str, Any]:
        return {
            "source_id": cls.SOURCE_ID,
            "adapter_name": "TKDLAdapter",
            "official_url": cls.OFFICIAL_URL,
            "access_type": "mixed",
            "access_status": cls.ACCESS_STATUS,
            "source_category": "SIH_PORTAL_SPECIFIED",
            "has_public_search_capability": False,
            "access_restriction": "Restricted - CSIR Non-Disclosure Access Agreement Required for Full Recipe Database Search"
        }
