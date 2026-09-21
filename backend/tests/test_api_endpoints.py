from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "SRA Business Lead Finder" in data["service"]


def test_auth_login_admin():
    response = client.post("/api/auth/login", json={"email": "admin@sra.com", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@sra.com"
    assert data["user"]["role"] == "admin"


def test_auth_login_invalid():
    response = client.post("/api/auth/login", json={"email": "admin@sra.com", "password": "wrongpassword"})
    assert response.status_code == 401


def test_categories_endpoint():
    response = client.get("/api/categories")
    assert response.status_code == 200
    cats = response.json()
    assert len(cats) >= 40
    names = [c["name"] for c in cats]
    assert "Restaurants" in names
    assert "Hospitals" in names


def test_locations_districts_endpoint():
    response = client.get("/api/locations/districts")
    assert response.status_code == 200
    districts = response.json()
    assert len(districts) >= 38
    d_names = [d["district"] for d in districts]
    assert "Madurai" in d_names
    assert "Chennai" in d_names
    assert "Coimbatore" in d_names


def test_business_crud_and_crm():
    # 1. Create Business
    payload = {
        "business_name": "SRA Test Supermarket",
        "phone": "+91 94422 55667",
        "email": "test@srasupermarket.com",
        "address": "45, East Veli Street",
        "district": "Madurai",
        "website_url": None,
        "source": "Manual Test",
    }
    create_resp = client.post("/api/businesses", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    biz_id = created["id"]
    assert created["business_name"] == "SRA Test Supermarket"
    assert created["website_status"] == "NO_WEBSITE"
    assert created["lead_score"] >= 60

    # 2. Toggle Save
    save_resp = client.patch(f"/api/businesses/{biz_id}/save")
    assert save_resp.status_code == 200
    assert save_resp.json()["is_saved"] is True

    # 3. Add CRM Note
    note_resp = client.post(f"/api/businesses/{biz_id}/notes", json={"note": "Called business owner. Very interested."})
    assert note_resp.status_code == 201
    assert note_resp.json()["note"] == "Called business owner. Very interested."

    # 4. Update Status
    status_resp = client.patch(f"/api/businesses/{biz_id}/status", json={"status": "INTERESTED", "reason": "High interest in website creation"})
    assert status_resp.status_code == 200
    assert status_resp.json()["lead_status"] == "INTERESTED"

    # 5. List with NO_WEBSITE filter
    list_resp = client.get("/api/businesses?website_status=NO_WEBSITE&district=Madurai")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1

    # 6. Export CSV
    csv_resp = client.get("/api/export/csv?website_status=NO_WEBSITE")
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
    assert "Business Name" in csv_resp.text

    # 7. Export Excel
    excel_resp = client.get("/api/export/excel?website_status=NO_WEBSITE")
    assert excel_resp.status_code == 200
    assert "application/vnd.openxmlformats-officedocument" in excel_resp.headers["content-type"]
