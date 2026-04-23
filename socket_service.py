import socketio
import uuid
import time
from fastapi import FastAPI

# =========================
# CREATE FASTAPI FIRST
# =========================
fastapi_app = FastAPI()

# =========================
# SOCKET.IO SETUP
# =========================
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*"
)

# =========================
# MOUNT SOCKET.IO ON FASTAPI
# =========================
app = socketio.ASGIApp(sio)
fastapi_app.mount("/", app)

# =========================
# HEALTH CHECK (THIS WILL WORK NOW)
# =========================
@fastapi_app.get("/health")
async def health():
    return {"status": "Backend running 🚀"}

# =========================
# STORAGE
# =========================
active_rides = {}

# =========================
# SOCKET EVENTS
# =========================
@sio.event
async def connect(sid, environ):
    print("✅ Connected:", sid)

@sio.event
async def disconnect(sid):
    print("❌ Disconnected:", sid)

@sio.event
async def register_user(sid, data):
    print("👤 User:", data)

@sio.event
async def join_ride(sid, data):
    ride_id = data["ride_id"]
    await sio.enter_room(sid, ride_id)
    active_rides.setdefault(ride_id, [])

@sio.event
async def send_offer(sid, data):
    message = {
        "id": str(uuid.uuid4()),
        "ride_id": data["ride_id"],
        "fare": data["fare"],
        "role": data["role"],
        "time": time.time()
    }

    active_rides.setdefault(data["ride_id"], []).append(message)

    await sio.emit("receive_offer", message, room=data["ride_id"])

@sio.event
async def accept_offer(sid, data):
    await sio.emit("offer_accepted", data, room=data["ride_id"])

@sio.event
async def reject_offer(sid, data):
    await sio.emit("offer_rejected", data, room=data["ride_id"])