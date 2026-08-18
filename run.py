import uvicorn

if __name__ == "__main__":
    print("🚀 API va Admin Panel ishga tushirilmoqda...")
    print("🌐 Admin Panel manzili: http://localhost:8000/admin")
    print("📘 API Dokumentatsiya: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
