from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agent import generate_poster, generate_portrait
import logging
import asyncio

# set up logging so we can see what's happening in the terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# initialize the FastAPI app
app = FastAPI()

# only allow requests from the Vue dev server
origins = ["http://localhost:5173"]

# CORS middleware lets the Vue frontend talk to the FastAPI backend
# without this the browser would block the requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# defines the shape of the request body coming from the Vue frontend
# pydantic handles validation automatically
class PosterRequest(BaseModel):
    name: str
    race: str
    char_class: str
    description: str
    crimes: str
    location: str
    photo: str | None = None  # optional base64 photo

# main endpoint that the Vue frontend calls to generate a wanted poster
@app.post("/generate_poster")
async def create_poster(req: PosterRequest):
    logger.info(f"Generating poster for: {req.name}")
    
    if req.photo:
        # user uploaded a photo - just use it directly, no AI generation needed
        result = await generate_poster(req)
        result["portrait_url"] = ""
    else:
        # no photo uploaded - generate an AI portrait from the description
        poster_task = generate_poster(req)
        portrait_task = generate_portrait(req.description, req.race, req.char_class)
        result, portrait_url = await asyncio.gather(poster_task, portrait_task)
        result["portrait_url"] = portrait_url
    
    return result

# simple health check to confirm the backend is running
@app.get("/")
def home():
    return {"message": "DnD Wanted Poster Backend is running."}