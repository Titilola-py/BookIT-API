from fastapi import FastAPI
from database.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from middleware.middleware import add_request_id_and_process_time
from routers.user import user_router
from routers.service import service_router
from routers.booking import booking_router
from routers.review import review_router


Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="BookIt API",
    version="1.0.0",
    description="API for a simple bookings platform called BookIt, allowing users to book services, leave reviews, and manage their accounts.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(add_request_id_and_process_time)


@app.get("/", status_code=200)
async def home():
    return {"message": "Welcome to BookIt API"}


app.include_router(user_router, prefix="/api", tags=["Users"])
app.include_router(service_router, prefix="/api", tags=["Services"])
app.include_router(booking_router, prefix="/api", tags=["Bookings"])
app.include_router(review_router, prefix="/api", tags=["Reviews"])
