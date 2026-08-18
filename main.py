import os
import json
import time
import secrets
import urllib.request
from email.utils import parsedate_to_datetime
from collections import deque
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from datetime import datetime
import pytz
import holidays
import calendar
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Advanced FastAPI Boshqaruv Tizimi")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

DB_FILE = "db.json"

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "SuperSecretAdminPassword2026!")

state = {
    "api_status": {
        "month": True,
        "time": True,
        "holidays": True
    },
    "rate_limit": 3,
    "blocked_ips": [],
    "ip_api_blocks": {}
}

ip_logs = {}
recent_requests = deque(maxlen=1000)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                state["api_status"] = data.get("api_status", state["api_status"])
                state["rate_limit"] = data.get("rate_limit", 3)
                state["blocked_ips"] = data.get("blocked_ips", [])
                state["ip_api_blocks"] = data.get("ip_api_blocks", {})
        except:
            pass

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump({
            "api_status": state["api_status"],
            "rate_limit": state["rate_limit"],
            "blocked_ips": state["blocked_ips"],
            "ip_api_blocks": state["ip_api_blocks"]
        }, f)

load_db()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    is_user_ok = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    is_pass_ok = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (is_user_ok and is_pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri login yoki parol",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.middleware("http")
async def request_middleware(request: Request, call_next):
    if request.url.path.startswith("/api"):
        client_ip = request.client.host
        path = request.url.path
        
        api_name = "unknown"
        if "/api/month" in path: api_name = "month"
        elif "/api/time" in path: api_name = "time"
        elif "/api/holidays" in path: api_name = "holidays"
        
        req_info = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": client_ip,
            "endpoint": path,
            "api_name": api_name
        }
        recent_requests.appendleft(req_info)

        if client_ip in state["blocked_ips"]:
            return JSONResponse(status_code=403, content={"detail": "Sizning IP manzilingiz to'liq bloklangan."})
            
        if client_ip in state["ip_api_blocks"] and api_name in state["ip_api_blocks"][client_ip]:
             return JSONResponse(status_code=403, content={"detail": f"Bu IP uchun {api_name} API bloklangan."})
             
        if api_name in state["api_status"] and not state["api_status"][api_name]:
            return JSONResponse(status_code=503, content={"detail": f"{api_name} API vaqtinchalik o'chirilgan."})
            
        current_time = time.time()
        if client_ip not in ip_logs:
            ip_logs[client_ip] = []
            
        ip_logs[client_ip] = [t for t in ip_logs[client_ip] if current_time - t <= 1]
        ip_logs[client_ip].append(current_time)
        
        if len(ip_logs[client_ip]) > state["rate_limit"]:
            if client_ip not in state["blocked_ips"]:
                state["blocked_ips"].append(client_ip)
                save_db()
            return JSONResponse(status_code=429, content={"detail": "Limitdan oshib ketdingiz. IP avtomatik bloklandi."})
            
    response = await call_next(request)
    return response

def get_tz(region: str):
    region_upper = region.upper()
    tz_names = pytz.country_timezones.get(region_upper)
    if tz_names:
        return pytz.timezone(tz_names[0])
    try:
        return pytz.timezone(region)
    except:
        return pytz.UTC

@app.get("/api/month/{region}")
async def get_month_data(region: str):
    tz = get_tz(region)
    now = datetime.now(tz)
    
    cal = calendar.monthcalendar(now.year, now.month)
    work_days = 0
    weekend_days = 0
    days_list = []
    
    for week in cal:
        for i, day in enumerate(week):
            if day != 0:
                is_weekend = i >= 5 
                if is_weekend: weekend_days += 1
                else: work_days += 1
                days_list.append({
                    "date": f"{now.year}-{now.month:02d}-{day:02d}",
                    "is_weekend": is_weekend
                })
                
    return {
        "region": region,
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "total_work_days": work_days,
        "total_weekend_days": weekend_days,
        "calendar": days_list
    }

@app.get("/api/time/{region}")
async def get_current_time(region: str):
    tz = get_tz(region)
    try:
        req = urllib.request.Request("https://google.com", method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as response:
            date_str = response.headers.get("Date")
            google_utc_time = parsedate_to_datetime(date_str)
            now = google_utc_time.astimezone(tz)
    except Exception:
        now = datetime.now(tz)
        
    return {
        "region": region,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "week_number": now.isocalendar()[1],
        "month_number": now.month,
        "year": now.year
    }
    
@app.get("/api/holidays/{region}")
async def get_holidays(region: str, year: int = None):
    if not year: year = datetime.now().year
    try:
        country_holidays = holidays.country_holidays(region.upper(), years=year)
        holiday_list = [{"date": str(date), "name": name, "month": date.month} for date, name in sorted(country_holidays.items())]
        return {"region": region.upper(), "year": year, "holidays": holiday_list}
    except Exception as e:
        return {"error": f"Bunday hudud topilmadi: {region}. Iltimos, ISO kod kiriting (masalan: UZ, US)."}

@app.get("/admin/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, admin: str = Depends(verify_admin)):
    return templates.TemplateResponse(request=request, name="admin.html")

@app.get("/admin/api/state")
async def get_state(admin: str = Depends(verify_admin)):
    return {
        "state": state,
        "recent_requests": list(recent_requests)
    }

@app.post("/admin/api/toggle_api")
async def toggle_api(request: Request, admin: str = Depends(verify_admin)):
    data = await request.json()
    api_name = data.get("api")
    status = data.get("status")
    if api_name in state["api_status"]:
        state["api_status"][api_name] = status
        save_db()
    return {"success": True}

@app.post("/admin/api/set_limit")
async def set_limit(request: Request, admin: str = Depends(verify_admin)):
    data = await request.json()
    new_limit = data.get("limit")
    if new_limit and isinstance(new_limit, int) and new_limit > 0:
        state["rate_limit"] = new_limit
        save_db()
    return {"success": True}

@app.post("/admin/api/block_ip")
async def block_ip(request: Request, admin: str = Depends(verify_admin)):
    data = await request.json()
    ip = data.get("ip")
    if ip and ip not in state["blocked_ips"]:
        state["blocked_ips"].append(ip)
        save_db()
    return {"success": True}

@app.post("/admin/api/unblock_ip")
async def unblock_ip(request: Request, admin: str = Depends(verify_admin)):
    data = await request.json()
    ip = data.get("ip")
    if ip in state["blocked_ips"]:
        state["blocked_ips"].remove(ip)
        save_db()
    return {"success": True}
    
@app.post("/admin/api/block_specific")
async def block_specific(request: Request, admin: str = Depends(verify_admin)):
    data = await request.json()
    ip = data.get("ip")
    apis = data.get("apis")
    if ip:
        state["ip_api_blocks"][ip] = apis
        save_db()
    return {"success": True}
