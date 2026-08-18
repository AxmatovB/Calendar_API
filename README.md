# FastAPI Boshqaruv Tizimi va API

Bu loyiha turli xil ma'lumotlarni (oylik taqvim, joriy vaqt, bayramlar) taqdim etuvchi hamda ushbu API'larni to'liq nazorat qilish imkonini beruvchi kuchli **Admin Panel** bilan ta'minlangan FastAPI dasturidir. 

Loyiha to'liq Dockerizatsiya qilingan bo'lib, o'rnatish va ishga tushirish juda oson.

---

## 📂 Loyiha Strukturasi

```text
apilare/
│
├── main.py                # Asosiy dastur kodi (FastAPI)
├── run.py                 # Lokal ishga tushirish uchun yordamchi skript
├── requirements.txt       # Kerakli Python kutubxonalari
├── db.json                # API holati va cheklovlarni saqlaydigan ma'lumotlar bazasi
├── .env                   # Maxfiy kalitlar va parollar
├── Dockerfile             # Docker image yaratish uchun ko'rsatmalar
├── docker-compose.yml     # Dasturni Docker orqali ishga tushirish uchun konfiguratsiya
├── .dockerignore          # Docker'ga o'tkazilmaydigan fayllar ro'yxati
└── templates/
    └── admin.html         # Admin panel sahifasi uchun HTML shablon
```

---

## 🌐 Ochiq API'lar (Public Endpoints)

Oddiy foydalanuvchilar / mijozlar tomonidan ishlatiladigan API'lar. Hudud sifatida ISO kod (masalan: `UZ`, `US`) yoki vaqt mintaqasi (`Asia/Tashkent`) kiritish mumkin.

### 1. Oylik Kalendar va Ma'lumotlar
- **Endpoint**: `GET /api/month/{region}`
- **Vazifasi**: Kiritilgan hudud bo'yicha joriy oydagi barcha kunlar, jami ish kunlari va dam olish kunlari sonini hisoblab qaytaradi.
- **Misol**: `http://localhost:8000/api/month/UZ`

### 2. Joriy Vaqt API
- **Endpoint**: `GET /api/time/{region}`
- **Vazifasi**: Kiritilgan hudud uchun soat, minut, sekund, oy, va yilning nechinchi haftasi ekanligini aniq ko'rsatib beradi.
- **Misol**: `http://localhost:8000/api/time/Asia/Tashkent`

### 3. Bayramlar API
- **Endpoint**: `GET /api/holidays/{region}`
- **Vazifasi**: Kiritilgan davlatning joriy yildagi barcha bayramlari, ularning nomlari va sanalarini qaytaradi (python `holidays` kutubxonasi yordamida).
- **Misol**: `http://localhost:8000/api/holidays/US`

---

## 🛠 Admin REST API'lar (Secured)

Admin paneli ishlashi uchun mo'ljallangan va faqat **HTTP Basic Auth** orqali himoyalangan API'lar (boshqalar bu API'larga kira olmaydi).

- `GET /admin/api/state` - Tizimning umumiy holatini va so'nggi kelib tushgan so'rovlar tarixini (log) qaytaradi.
- `POST /admin/api/toggle_api` - Muayyan ochiq API ni yoqish yoki o'chirish.
- `POST /admin/api/set_limit` - Foydalanuvchilar uchun umumiy sekundlik so'rovlar limitini o'zgartirish.
- `POST /admin/api/block_ip` - Qoidabuzar IP manzilni to'liq bloklash.
- `POST /admin/api/unblock_ip` - Bloklangan IP manzilni blokdan chiqarish.
- `POST /admin/api/block_specific` - Muayyan IP manzil uchun tanlangan API'larni bloklash.

---

## 🔐 Admin Panel (Boshqaruv oynasi)

Dasturga kelayotgan barcha so'rovlarni kuzatish, zararli foydalanuvchilarni bloklash va tizimni boshqarish uchun juda qulay GUI (Grafik interfeys) qilingan.

- **URL Manzil:** [http://localhost:8000/admin/admin](http://localhost:8000/admin/admin)
- **Login:** `admin`
- **Parol:** `SuperSecretAdminPassword2026!`

*(Parolni istalgan vaqtda `.env` fayli orqali o'zgartirishingiz mumkin).*

### Panel imkoniyatlari:
- **Live Requests (Jonli so'rovlar):** API ga qilingan barcha so'rovlar, qaysi IP dan qachon qilingani real vaqtda ko'rsatiladi.
- **Qidirish & Filtr:** IP'lar va URL bo'yicha qidirish, faqat betakror (unique) IP'larni ajratib olish.
- **Tezkor Bloklash (Double Click):** So'rov yuborgan IP ustiga ikki marta bosib to'liq bloklash mumkin.
- **Qisman Bloklash (Right Click):** Sichqonchaning o'ng tugmasini bosib shu IP uchun faqat bitta (yoki bir nechta) API'ga ruxsatni cheklash mumkin.
- **Cheklovlar:** Soniyasiga keladigan limitni (Rate Limit) o'zgartirish yoki barcha API'larni alohida-alohida o'chirib qo'yish (toggle).

---

## 🚀 Ishga Tushirish

### 1-usul: Docker orqali (Tavsiya etiladi)
Docker o'rnatilgan bo'lsa, terminalda loyiha papkasiga kirib shunchaki quydagilarni yozing:
```bash
docker-compose up -d --build
```
Dastur orqa fonda avtomatik ravishda ishga tushadi. To'xtatish uchun: `docker-compose down`.

### 2-usul: Lokal kompyuterda (Docker'siz)
Barcha kutubxonalarni o'rnating:
```bash
pip install -r requirements.txt
```
Keyin loyihani ishga tushiring:
```bash
python run.py
```
*API avtomatik hujjatlari (Swagger UI) ga kirish uchun: `http://localhost:8000/docs` manziliga o'ting.*
