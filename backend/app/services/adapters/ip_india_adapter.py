from typing import Dict, Any

class IPIndiaPublicDatabaseAdapter:
    """
    Dedicated Adapter Interface for IP India Public Search Databases:
    - InPASS (Indian Patent Advanced Search System)
    - Trade Marks Registry Public Search
    - Designs Registry Search
    - Geographical Indications Registry Search
    
    Explicitly distinguishes live public search databases from static statutory Acts.
    """
    SOURCE_ID = "IND-IP-INDIA-PUBLIC-DATABASES"
    OFFICIAL_URL = "https://ipindiaservices.gov.in"
    ACCESS_STATUS = "NOT_CURRENTLY_ACCESSIBLE" # Live CAPTCHA/session-protected portal search not programmatically connected

    @classmethod
    def get_adapter_info(cls) -> Dict[str, Any]:
        return {
            "source_id": cls.SOURCE_ID,
            "adapter_name": "IPIndiaPublicDatabaseAdapter",
            "official_url": cls.OFFICIAL_URL,
            "access_type": "public_interactive_portal",
            "access_status": cls.ACCESS_STATUS,
            "source_category": "SIH_PORTAL_SPECIFIED",
            "has_public_search_capability": False,
            "sub_databases": [
                {"name": "InPASS Patent Search", "url": "https://ipindiaservices.gov.in/publicsearch", "status": "NOT_CURRENTLY_ACCESSIBLE"},
                {"name": "Trade Mark Public Search", "url": "https://ipindiaservices.gov.in/tmrpublicsearch", "status": "NOT_CURRENTLY_ACCESSIBLE"},
                {"name": "Design Search", "url": "https://ipindiaservices.gov.in/designsearch", "status": "NOT_CURRENTLY_ACCESSIBLE"},
                {"name": "GI Registry Search", "url": "https://ipindiaservices.gov.in/giregistry", "status": "NOT_CURRENTLY_ACCESSIBLE"}
            ],
            "note": "Static Patent/TM/GI Acts are ingested; live InPASS/TM/Design/GI public search portal scrapers are not connected to prevent CAPTCHA violations."
        }
