from re import compile, escape, IGNORECASE

from .db import get_uncategorized_corps, update_company_category

KEYWORDS = {
    "Automotive Repair": [
        "auto",
        "automotive",
        "auto repair", "mechanic",
        "car",
        "shop",
        "garage",
        "detail",
        "transport",
        "trucking",
        "fleet"
    ],
    "Home Services": [
        "plumbing",
        "hvac",
        "electrical",
        "contractor",
        "home repair",
        "landscaping",
        "home services",
        "cleaning",
        "maintenance"
    ],
    "Legal Services": [
        "law",
        "legal",
        "attorney",
        "firm",
        "counsel",
        "pllc",
        "pa"
    ],
    "Healthcare": [
        "health",
        "medical",
        "clinic",
        "dental",
        "dentist",
        "chiro",
        "therapy",
        "wellness",
        "hospital",
        "pharma"
    ],
    "Real Estate": [
        "real estate",
        "realty",
        "agent",
        "broker",
        "property",
        "homes",
        "investments",
        "housing"
    ],
    "Restaurants & Food Service": [
        "restaurant",
        "cafe",
        "kitchen",
        "food",
        "catering",
        "eatery",
        "grill",
        "bistro",
        "deli",
        "pizza",
        "bar",
        "lounge",
        "juice"],
    "Beauty & Wellness": [
        "beauty",
        "salon",
        "spa",
        "wellness",
        "nails",
        "hair",
        "massage",
        "esthetics",
        "skincare"],
    "Retail": [
        "retail",
        "boutique",
        "shop",
        "store",
        "supplies"
    ],
    "Financial Services": [
        "finance",
        "financial",
        "insurance",
        "capital",
        "advisory",
        "accounting",
        "tax"
    ],
    "Logistics & Distribution": [
        "logistics",
        "distribution",
        "transport",
        "freight",
        "delivery"
    ],
    "Manufacturing": [
        "manufacturing",
        "industrial",
        "fabrication",
        "production"
    ],
}

COMPILED_KEYWORDS = { 
    category:
        compile(r'\b(' + '|'.join(map(escape, keywords)) + r')\b', IGNORECASE)
    for category, keywords in KEYWORDS.items()
}

def categorize_corporations(conn):
    uncategorized_corporations = get_uncategorized_corps(conn)
    for corp in uncategorized_corporations:
        assigned_category = None
        for category, pattern in COMPILED_KEYWORDS.items():
            if pattern.search(corp['corporation_name']):
                assigned_category = category
                break
        if assigned_category:
            update_company_category(conn, corp['corporation_number'], assigned_category)
        else:
            update_company_category(conn, corp['corporation_number'], "Unlisted")
            
