import uvicorn

if __name__ == "__main__":
    print("🚀 API va Admin Panel ishga tushirilmoqda...")
    print("🌐 Admin Panel manzili: http://localhost:2006/admin")
    print("📘 API Dokumentatsiya: http://localhost:2006/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=2006, reload=True)
