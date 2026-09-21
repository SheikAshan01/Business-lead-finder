import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.security import hash_password
from app.db import SessionLocal
from app.models.business import Category, Location, Source, User, UserRole

# All 38 Districts of Tamil Nadu with sample taluks
TAMIL_NADU_DISTRICTS = {
    "Chennai": ["Egmore", "Mylapore", "T. Nagar", "Guindy", "Velachery", "Anna Nagar", "Tondiarpet"],
    "Coimbatore": ["Coimbatore North", "Coimbatore South", "Pollachi", "Mettupalayam", "Sulur", "Annur"],
    "Madurai": ["Madurai North", "Madurai South", "Melur", "Thirumangalam", "Usilampatti", "Vadipatti"],
    "Tiruchirappalli": ["Tiruchirappalli East", "Tiruchirappalli West", "Srirangam", "Lalgudi", "Manapparai", "Thuraiyur"],
    "Salem": ["Salem", "Attur", "Mettur", "Omalur", "Sankari", "Yercaud"],
    "Tirunelveli": ["Tirunelveli", "Palayamkottai", "Ambasamudram", "Nanguneri", "Radhapuram"],
    "Tiruppur": ["Tiruppur North", "Tiruppur South", "Avinashi", "Dharapuram", "Kangeyam", "Udumalaipettai"],
    "Erode": ["Erode", "Bhavani", "Gobichettipalayam", "Perundurai", "Sathyamangalam"],
    "Vellore": ["Vellore", "Gudiyatham", "Katpadi", "Anaicut", "K.V. Kuppam"],
    "Thanjavur": ["Thanjavur", "Kumbakonam", "Papanasam", "Pattukkottai", "Orathanadu"],
    "Dindigul": ["Dindigul East", "Dindigul West", "Palani", "Kodaikanal", "Nilakottai", "Oddanchatram"],
    "Kanchipuram": ["Kanchipuram", "Sriperumbudur", "Walajabad", "Kundrathur", "Uthiramerur"],
    "Chengalpattu": ["Chengalpattu", "Tambaram", "Pallavaram", "Madurantakam", "Thiruporur", "Cheyyur"],
    "Tiruvallur": ["Tiruvallur", "Avadi", "Ponneri", "Gummidipoondi", "Poonamallee", "Tiruttani"],
    "Cuddalore": ["Cuddalore", "Chidambaram", "Panruti", "Virudhachalam", "Neyveli", "Bhuvanagiri"],
    "Dharmapuri": ["Dharmapuri", "Harur", "Palacode", "Pennagaram", "Pappireddipatti"],
    "Krishnagiri": ["Krishnagiri", "Hosur", "Pochampalli", "Uthangarai", "Denkanikottai"],
    "Kanyakumari": ["Agastheeswaram", "Kalkulam", "Killiyoor", "Thiruvattar", "Vilavancode"],
    "Karur": ["Karur", "Aravakurichi", "Kulithalai", "Manmangalam", "Pugalur"],
    "Namakkal": ["Namakkal", "Rasipuram", "Tiruchengode", "Paramathi Velur", "Kolli Hills"],
    "Nilgiris": ["Udhagamandalam (Ooty)", "Coonoor", "Kotagiri", "Gudalur", "Pandalur"],
    "Perambalur": ["Perambalur", "Kunnam", "Alathur", "Veppanthattai"],
    "Pudukkottai": ["Pudukkottai", "Aranthangi", "Alangudi", "Gandarvakottai", "Iluppur", "Kulathur"],
    "Ramanathapuram": ["Ramanathapuram", "Paramakudi", "Rameswaram", "Kamuthi", "Mudukulathur", "Kadaladi"],
    "Ranipet": ["Ranipet", "Arcot", "Walajah", "Arakkonam", "Nemili"],
    "Sivaganga": ["Sivaganga", "Karaikudi", "Devakottai", "Manamadurai", "Ilayangudi", "Tirupathur"],
    "Tenkasi": ["Tenkasi", "Sankarankovil", "Ambasamudram", "Kadayanallur", "Alangulam", "Shenkottai"],
    "Theni": ["Theni", "Periyakulam", "Bodinayakanur", "Uthamapalayam", "Andipatti"],
    "Thoothukudi": ["Thoothukudi", "Kovilpatti", "Tiruchendur", "Srivaikuntam", "Ettayapuram"],
    "Tirupathur": ["Tirupathur", "Vaniyambadi", "Ambur", "Natrampalli"],
    "Tiruvannamalai": ["Tiruvannamalai", "Arani", "Cheyyar", "Polur", "Chengam", "Vandavasi"],
    "Tiruvarur": ["Tiruvarur", "Mannargudi", "Thiruthuraipoondi", "Nannilam", "Kudavasal"],
    "Viluppuram": ["Viluppuram", "Tindivanam", "Gingee", "Vanur", "Vikravandi"],
    "Virudhunagar": ["Virudhunagar", "Sivakasi", "Rajapalayam", "Aruppukkottai", "Sattur"],
    "Ariyalur": ["Ariyalur", "Udayarpalayam", "Sendurai", "Andimadam"],
    "Kallakurichi": ["Kallakurichi", "Sankarapuram", "Chinnasalem", "Ulundurpet", "Tirukoilur"],
    "Mayiladuthurai": ["Mayiladuthurai", "Sirkazhi", "Tharangambadi", "Kuthalam"],
    "Nagapattinam": ["Nagapattinam", "Kilvelur", "Vedaranyam", "Thirukkuvalai"],
}

# 45+ Business Categories required by user specification
CATEGORIES = [
    "Restaurants",
    "Hotels",
    "Hospitals",
    "Clinics",
    "Dental Clinics",
    "Pharmacies",
    "Garments",
    "Textiles",
    "Jewellery",
    "Furniture",
    "Electronics",
    "Mobile Shops",
    "Bike Dealers",
    "Car Dealers",
    "Auto Service",
    "Mechanics",
    "Schools",
    "Colleges",
    "Coaching Centres",
    "Beauty Parlours",
    "Salons",
    "Event Management",
    "Wedding Services",
    "Catering",
    "Bakeries",
    "Supermarkets",
    "Grocery Stores",
    "Hardware",
    "Electrical Shops",
    "Construction",
    "Interior Designers",
    "Real Estate",
    "Travel Agencies",
    "Taxi Services",
    "Logistics",
    "Courier Services",
    "Printing",
    "Photography",
    "Digital Marketing",
    "CA Offices",
    "Law Firms",
    "Insurance",
    "Finance",
    "Fitness & Gyms",
    "Pet Care",
    "Security Services",
]

DEFAULT_SOURCES = [
    {
        "name": "OpenStreetMap Overpass TN",
        "source_type": "OPEN_DATA",
        "enabled": True,
        "rate_limit": 30,
        "terms_url": "https://www.openstreetmap.org/copyright",
        "config_json": '{"endpoint": "https://overpass-api.de/api/interpreter", "region": "Tamil Nadu"}',
    },
    {
        "name": "Google Places API",
        "source_type": "API",
        "enabled": False,
        "rate_limit": 60,
        "terms_url": "https://cloud.google.com/maps-platform/terms",
        "config_json": '{"requires_key": true, "env_var": "GOOGLE_PLACES_API_KEY"}',
    },
]


def seed_database():
    from app.db import Base, engine
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("[*] Seeding Users...")
        admin = db.query(User).filter(User.email == "admin@sra.com").first()
        if not admin:
            admin = User(
                email="admin@sra.com",
                hashed_password=hash_password("admin123"),
                full_name="SRA Administrator",
                role=UserRole.ADMIN.value,
                is_active=True,
            )
            db.add(admin)
            print("    -> Created default Admin (admin@sra.com / admin123)")

        agent = db.query(User).filter(User.email == "agent@sra.com").first()
        if not agent:
            agent = User(
                email="agent@sra.com",
                hashed_password=hash_password("agent123"),
                full_name="Lead Qualification Agent",
                role=UserRole.AGENT.value,
                is_active=True,
            )
            db.add(agent)
            print("    -> Created default Agent (agent@sra.com / agent123)")

        print("[*] Seeding Categories...")
        cat_count = 0
        for name in CATEGORIES:
            slug = name.lower().replace(" & ", "-").replace(" ", "-")
            existing = db.query(Category).filter(Category.name == name).first()
            if not existing:
                db.add(Category(name=name, slug=slug, enabled=True))
                cat_count += 1
        print(f"    -> Added {cat_count} categories (Total: {len(CATEGORIES)})")

        print("[*] Seeding Tamil Nadu Locations...")
        loc_count = 0
        for district, taluks in TAMIL_NADU_DISTRICTS.items():
            for taluk in taluks:
                existing = db.query(Location).filter(
                    Location.state == "Tamil Nadu",
                    Location.district == district,
                    Location.taluk == taluk,
                ).first()
                if not existing:
                    db.add(Location(
                        state="Tamil Nadu",
                        district=district,
                        taluk=taluk,
                        area=f"{taluk} Central",
                        pincode=None,
                        is_active=True,
                    ))
                    loc_count += 1
        print(f"    -> Added {loc_count} location records across 38 districts")

        print("[*] Seeding Data Sources...")
        for src in DEFAULT_SOURCES:
            existing = db.query(Source).filter(Source.name == src["name"]).first()
            if not existing:
                db.add(Source(**src))
                print(f"    -> Added source: {src['name']}")

        db.commit()
        print("[+] Database seeding successfully completed!")
    except Exception as e:
        db.rollback()
        print(f"[-] Seeding error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
