from flask import Flask, render_template, request, redirect, url_for, abort
from datetime import datetime, date
import secrets

app = Flask(__name__)

FEATURES = [
    "Wheelchair access",
    "AV equipment",
    "Kitchen",
    "Wi-Fi",
    "Parking",
    "Outdoor area",
    "On-site staff",
    "Licensed bar",
]

VENUES = [
    {
        "id": "v_oxford_hall",
        "name": "Example Venue 2",
        "city": "London",
        "area": "Shoreditch",
        "type": "Hall",
        "capacity": 180,
        "price_per_hour": 120,
        "min_hours": 3,
        "deposit_pct": 20,
        "features": ["Wheelchair access", "AV equipment", "Wi-Fi", "On-site staff"],
        "images": [
            "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1400&q=60",
            "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1400&q=60",
        ],
        "description": "A bright, flexible hall for workshops, talks and community events. Easy transport links and modern AV.",
        "availability": {
            "mon": [{"start": "09:00", "end": "21:00"}],
            "tue": [{"start": "09:00", "end": "21:00"}],
            "wed": [{"start": "09:00", "end": "21:00"}],
            "thu": [{"start": "09:00", "end": "21:00"}],
            "fri": [{"start": "09:00", "end": "22:00"}],
            "sat": [{"start": "10:00", "end": "23:00"}],
            "sun": [{"start": "10:00", "end": "18:00"}],
        },
        "notes": "Noise policy after 10pm. BYO catering allowed.",
    },
    {
        "id": "v_riverside_loft",
        "name": "Example Venue 1",
        "city": "London",
        "area": "South Bank",
        "type": "Loft",
        "capacity": 90,
        "price_per_hour": 200,
        "min_hours": 4,
        "deposit_pct": 25,
        "features": ["Wi-Fi", "Kitchen", "Outdoor area", "Parking"],
        "images": [
            "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=1400&q=60",
            "https://images.unsplash.com/photo-1558008258-3256797b43f3?auto=format&fit=crop&w=1400&q=60",
        ],
        "description": "Loft-style space with river views for private dinners, launches and networking. Includes kitchen prep area.",
        "availability": {
            "mon": [{"start": "12:00", "end": "22:00"}],
            "tue": [{"start": "12:00", "end": "22:00"}],
            "wed": [{"start": "12:00", "end": "22:00"}],
            "thu": [{"start": "12:00", "end": "23:00"}],
            "fri": [{"start": "12:00", "end": "23:00"}],
            "sat": [{"start": "11:00", "end": "23:00"}],
            "sun": [{"start": "11:00", "end": "21:00"}],
        },
        "notes": "Security staff required for events over 70 guests (can be arranged).",
    },
    {
        "id": "v_studio_green",
        "name": "Example Venue 3",
        "city": "Manchester",
        "area": "Northern Quarter",
        "type": "Studio",
        "capacity": 45,
        "price_per_hour": 65,
        "min_hours": 2,
        "deposit_pct": 15,
        "features": ["Wheelchair access", "Wi-Fi", "AV equipment"],
        "images": [
            "https://images.unsplash.com/photo-1526948128573-703ee1aeb6fa?auto=format&fit=crop&w=1400&q=60",
            "https://images.unsplash.com/photo-1529336953121-4f37c9f16c68?auto=format&fit=crop&w=1400&q=60",
        ],
        "description": "A clean, adaptable studio for rehearsals, meetups and pop-ups. Great value with optional projector and sound.",
        "availability": {
            "mon": [{"start": "08:00", "end": "20:00"}],
            "tue": [{"start": "08:00", "end": "20:00"}],
            "wed": [{"start": "08:00", "end": "20:00"}],
            "thu": [{"start": "08:00", "end": "20:00"}],
            "fri": [{"start": "08:00", "end": "20:00"}],
            "sat": [{"start": "10:00", "end": "18:00"}],
            "sun": [{"start": "10:00", "end": "16:00"}],
        },
        "notes": "Bring your own PA; quiet building after 8pm.",
    },
]

BOOKINGS = []  # in-memory demo only

def get_venue(venue_id: str):
    return next((v for v in VENUES if v["id"] == venue_id), None)

def gbp(n: int) -> str:
    return f"£{n:,}"

@app.template_filter("gbp")
def gbp_filter(value):
    return gbp(int(value))

@app.get("/")
def index():
    q = (request.args.get("q") or "").strip().lower()
    city = request.args.get("city") or "all"
    vtype = request.args.get("type") or "all"
    cap_min = int(request.args.get("cap_min") or 10)
    cap_max = int(request.args.get("cap_max") or 200)
    price_max = int(request.args.get("price_max") or 250)

    # features as repeated query param: ?feature=Wi-Fi&feature=Kitchen
    required_features = request.args.getlist("feature")

    venues = []
    for v in VENUES:
        if city != "all" and v["city"] != city:
            continue
        if vtype != "all" and v["type"] != vtype:
            continue
        if not (cap_min <= v["capacity"] <= cap_max):
            continue
        if v["price_per_hour"] > price_max:
            continue
        if required_features and not all(f in v["features"] for f in required_features):
            continue
        if q:
            hay = f'{v["name"]} {v["city"]} {v["area"]} {v["type"]} {v["description"]}'.lower()
            if q not in hay:
                continue
        venues.append(v)

    cities = sorted(set(v["city"] for v in VENUES))
    types = sorted(set(v["type"] for v in VENUES))

    return render_template(
        "index.html",
        venues=venues,
        cities=cities,
        types=types,
        features=FEATURES,
        filters={
            "q": request.args.get("q", ""),
            "city": city,
            "type": vtype,
            "cap_min": cap_min,
            "cap_max": cap_max,
            "price_max": price_max,
            "required_features": required_features,
        },
    )

@app.get("/venue/<venue_id>")
def venue_page(venue_id):
    v = get_venue(venue_id)
    if not v:
        abort(404)
    return render_template("venue.html", venue=v)

@app.get("/book/<venue_id>")
def booking_page(venue_id):
    v = get_venue(venue_id)
    if not v:
        abort(404)

    # sensible defaults
    today = date.today().isoformat()
    return render_template(
        "booking.html",
        venue=v,
        default_date=today,
    )

@app.post("/book/<venue_id>")
def submit_booking(venue_id):
    v = get_venue(venue_id)
    if not v:
        abort(404)

    # No DB: basic server-side validation + in-memory storage
    organiser_name = (request.form.get("organiser_name") or "").strip()
    organiser_email = (request.form.get("organiser_email") or "").strip()
    phone = (request.form.get("phone") or "").strip()

    booking_date = request.form.get("date") or ""
    start = request.form.get("start") or "18:00"
    hours = int(request.form.get("hours") or v["min_hours"])
    attendees = int(request.form.get("attendees") or 1)
    notes = (request.form.get("notes") or "").strip()
    agree = request.form.get("agree") == "on"

    errors = []
    if len(organiser_name) < 2:
        errors.append("Please enter your name.")
    if "@" not in organiser_email or "." not in organiser_email:
        errors.append("Please enter a valid email.")
    if len(phone) < 8:
        errors.append("Please enter a phone number.")
    if hours < v["min_hours"]:
        errors.append(f"Minimum booking is {v['min_hours']} hours.")
    if attendees > v["capacity"]:
        errors.append(f"Maximum capacity is {v['capacity']}.")
    if not agree:
        errors.append("You must agree to the policies to continue.")

    if errors:
        return render_template(
            "booking.html",
            venue=v,
            default_date=booking_date or date.today().isoformat(),
            errors=errors,
            form=request.form,
        ), 400

    base = hours * v["price_per_hour"]
    service_fee = round(base * 0.06)
    total = base + service_fee
    deposit = round(base * v["deposit_pct"] / 100)

    ref = f"BAS-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}"
    BOOKINGS.append({
        "ref": ref,
        "venue_id": v["id"],
        "venue_name": v["name"],
        "created_at": datetime.utcnow().isoformat() + "Z",
        "date": booking_date,
        "start": start,
        "hours": hours,
        "attendees": attendees,
        "organiser_name": organiser_name,
        "organiser_email": organiser_email,
        "phone": phone,
        "notes": notes,
        "pricing": {
            "base": base,
            "service_fee": service_fee,
            "total": total,
            "deposit": deposit,
        },
        "status": "requested",
    })

    return redirect(url_for("confirmation", ref=ref))

@app.get("/confirmation")
def confirmation():
    ref = request.args.get("ref")
    booking = next((b for b in BOOKINGS if b["ref"] == ref), None)
    if not booking:
        abort(404)
    return render_template("confirmation.html", booking=booking)

if __name__ == "__main__":
    app.run(debug=True)
