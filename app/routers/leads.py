from fastapi import APIRouter
import requests

router = APIRouter()

@router.get("/leads")
def get_leads(limit: int = 30):

    url = "https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json"

    try:
        print("Fetching university data...")

        response = requests.get(url, timeout=10)
        data = response.json()

        companies = []

        for item in data[:limit]:
            companies.append({
                "company_name": item.get("name", "N/A"),
                "location": item.get("country", "N/A"),
                "website": item.get("web_pages", ["N/A"])[0],
                "source": "University Dataset"
            })

        return companies

    except Exception as e:
        print("Error:", e)
        return get_sample_companies()


def get_sample_companies():
    return [
        {"company_name": "TechCorp", "location": "USA", "website": "techcorp.com", "source": "Sample"},
        {"company_name": "InnovateLabs", "location": "UK", "website": "innovatelabs.co.uk", "source": "Sample"}
    ]