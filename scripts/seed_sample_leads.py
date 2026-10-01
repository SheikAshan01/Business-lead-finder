import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.db import SessionLocal
from app.models.business import Business, Category, Location, LeadStatus, WebsiteStatus

SAMPLE_BUSINESSES = [
    # Coimbatore (Textiles & Machinery)
    {"name": "Sri Lakshmi Textile Mills", "cat": "Textiles", "dist": "Coimbatore", "city": "Coimbatore", "phone": "+91 98422 14589", "email": "contact@lakshmitex.in", "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.NEW, "score": 92},
    {"name": "Kovai Precision Engineering", "cat": "Hardware", "dist": "Coimbatore", "city": "Pollachi", "phone": "+91 97890 23411", "email": None, "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.CONTACTED, "score": 88},
    {"name": "Anand Auto Garage & Spares", "cat": "Auto Service", "dist": "Coimbatore", "city": "Mettupalayam", "phone": "+91 94433 87612", "email": "anandgarage@gmail.com", "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.INTERESTED, "score": 85},
    {"name": "Kongu Grand Sweets & Bakery", "cat": "Bakeries", "dist": "Coimbatore", "city": "Coimbatore", "phone": "+91 99441 55678", "email": "orders@kongugrandsweets.com", "web": "https://kongugrandsweets.com", "web_stat": WebsiteStatus.WEBSITE_FOUND, "stat": LeadStatus.CONVERTED, "score": 45},

    # Chennai (Retail, Medical & Services)
    {"name": "Madras Dental Clinic & Implant Centre", "cat": "Dental Clinics", "dist": "Chennai", "city": "Mylapore", "phone": "+91 98840 91234", "email": "care@madrasdental.com", "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.NEW, "score": 95},
    {"name": "Velan Silks & Readymades", "cat": "Garments", "dist": "Chennai", "city": "T. Nagar", "phone": "+91 94441 23456", "email": None, "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.INTERESTED, "score": 90},
    {"name": "Chennai Fresh Supermarket", "cat": "Supermarkets", "dist": "Chennai", "city": "Anna Nagar", "phone": "+91 98403 44556", "email": "chennaifresh@outlook.com", "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.CONTACTED, "score": 82},
    {"name": "Marina Event Management & Decors", "cat": "Event Management", "dist": "Chennai", "city": "Velachery", "phone": "+91 97911 67890", "email": "events@marinadecors.in", "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.FOLLOW_UP, "score": 87},

    # Madurai (Hotels & Traditional Trade)
    {"name": "Meenakshi Vilas Pure Veg Hotel", "cat": "Restaurants", "dist": "Madurai", "city": "Madurai North", "phone": "+91 94422 78901", "email": None, "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.NEW, "score": 94},
    {"name": "Pandian Gold & Diamonds", "cat": "Jewellery", "dist": "Madurai", "city": "Madurai South", "phone": "+91 98430 55672", "email": "info@pandiangold.com", "web": "https://pandiangold.com", "web_stat": WebsiteStatus.WEBSITE_FOUND, "stat": LeadStatus.CONVERTED, "score": 50},
    {"name": "Vaigai Mobile Hub & Service", "cat": "Mobile Shops", "dist": "Madurai", "city": "Melur", "phone": "+91 96291 88902", "email": "vaigaimobiles@gmail.com", "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.CONTACTED, "score": 79},

    # Tiruppur (Garment Exports & Accessories)
    {"name": "Classic Knitwear Exports", "cat": "Garments", "dist": "Tiruppur", "city": "Tiruppur North", "phone": "+91 98940 33412", "email": "exports@classicknitwear.in", "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.INTERESTED, "score": 96},
    {"name": "Euro Tex Dyes & Chemicals", "cat": "Textiles", "dist": "Tiruppur", "city": "Tiruppur South", "phone": "+91 97877 44510", "email": None, "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.NEW, "score": 89},

    # Salem (Steel, Transports & Agriculture)
    {"name": "Salem Steel & Hardware Traders", "cat": "Hardware", "dist": "Salem", "city": "Salem", "phone": "+91 94432 66780", "email": "sales@salemsteel.co.in", "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.NEW, "score": 91},
    {"name": "Green Valley Nursery & Plants", "cat": "Construction", "dist": "Salem", "city": "Yercaud", "phone": "+91 99420 11223", "email": None, "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.CONTACTED, "score": 83},

    # Dindigul (Locks, Leather & Education)
    {"name": "Dindigul Traditional Lock Works", "cat": "Hardware", "dist": "Dindigul", "city": "Dindigul East", "phone": "+91 98421 99011", "email": "dindigullocks@yahoo.com", "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.NEW, "score": 93},
    {"name": "Palani Hill View Residency", "cat": "Hotels", "dist": "Dindigul", "city": "Palani", "phone": "+91 94431 44567", "email": "booking@palanihillview.in", "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.FOLLOW_UP, "score": 86},

    # Tiruchirappalli (Fabrication & Logistics)
    {"name": "Cauvery Heavy Fabrication Works", "cat": "Construction", "dist": "Tiruchirappalli", "city": "Tiruchirappalli East", "phone": "+91 98424 77890", "email": "cauveryfab@gmail.com", "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.INTERESTED, "score": 90},
    {"name": "Rockfort Logistics & Transports", "cat": "Logistics", "dist": "Tiruchirappalli", "city": "Thuraiyur", "phone": "+91 97880 22345", "email": None, "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.NEW, "score": 84},

    # Erode (Turmeric & Electricals)
    {"name": "Bhavani Power Electricals", "cat": "Electrical Shops", "dist": "Erode", "city": "Bhavani", "phone": "+91 94437 11234", "email": "bhavanielectricals@gmail.com", "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.CONTACTED, "score": 88},
    {"name": "Erode Turmeric Trading Corporation", "cat": "Grocery Stores", "dist": "Erode", "city": "Erode", "phone": "+91 98427 33456", "email": "turmerictrade@erode.in", "web": None, "web_stat": WebsiteStatus.NO_WEBSITE, "stat": LeadStatus.NEW, "score": 95},
]

def seed_sample_leads():
    db = SessionLocal()
    try:
        cats = {c.name: c.id for c in db.query(Category).all()}

        count = 0
        for item in SAMPLE_BUSINESSES:
            existing = db.query(Business).filter(Business.business_name == item["name"]).first()
            if existing:
                continue

            cat_id = cats.get(item["cat"])

            biz = Business(
                business_name=item["name"],
                client_name=f"{item['name'].split()[0]} Proprietor",
                category_id=cat_id,
                district=item["dist"],
                taluk=item["city"],
                area=f"{item['city']} Main Road",
                address=f"Main Road, {item['city']}, {item['dist']} District, Tamil Nadu",
                state="Tamil Nadu",
                phone=item["phone"],
                alternate_phone=None,
                email=item["email"],
                website_url=item["web"],
                website_status=item["web_stat"],
                website_verified=bool(item["web"]),
                lead_status=item["stat"],
                lead_score=item["score"],
                score_reasons="Tamil Nadu Commercial Lead with high qualification metrics.",
                source="Tamil Nadu Business Directory",
                is_saved=False,
            )
            db.add(biz)
            count += 1

        db.commit()
        print(f"[+] Successfully seeded {count} sample business leads across Tamil Nadu!")
    except Exception as e:
        db.rollback()
        print(f"[-] Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_leads()
