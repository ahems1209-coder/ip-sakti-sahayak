from typing import Dict, Any

class IndiaCodeAdapter:
    """
    Dedicated Adapter Interface for India Code Digital Repository (https://www.indiacode.nic.in).
    Distinguishes static statutory Act PDFs from live India Code portal API search capability.
    """
    SOURCE_ID = "IND-INDIA-CODE-PORTAL"
    OFFICIAL_URL = "https://www.indiacode.nic.in"
    ACCESS_STATUS = "NOT_CURRENTLY_ACCESSIBLE" # Live India Code portal API not connected

    @classmethod
    def get_adapter_info(cls) -> Dict[str, Any]:
        return {
            "source_id": cls.SOURCE_ID,
            "adapter_name": "IndiaCodeAdapter",
            "official_url": cls.OFFICIAL_URL,
            "access_type": "public",
            "access_status": cls.ACCESS_STATUS,
            "source_category": "SIH_PORTAL_SPECIFIED",
            "has_public_search_capability": False,
            "note": "Static Central Acts (Patents Act, DCA, BDA) ingested from verified source files; live India Code portal API integration pending."
        }
