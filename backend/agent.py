import os
import logging
from dotenv import load_dotenv
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# load the .env file so we can grab the API key without hardcoding it
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# grab the API key from the environment you never ever wanna hardcode this
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Please check your .env file.")

# async client so we don't block the server while waiting on OpenAI
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def generate_poster(req) -> dict:
    logger.info(f"Generating wanted poster for {req.name}...")

    # prompt engineered to get consistent structured output from the model
    # the character details get injected from the request object
    prompt = f"""
    You are a fantasy wanted poster generator for a DnD campaign.
    Generate a dramatic wanted poster for the following character:

    Name: {req.name}
    Race: {req.race}
    Class: {req.char_class}
    Physical Description: {req.description}
    Crimes: {req.crimes}
    Last Known Location: {req.location}

    Return exactly these fields:
    BOUNTY: (a gold amount e.g. 5,000 Gold Pieces)
    THREAT_LEVEL: (one of: Petty Criminal, Dangerous, Highly Dangerous, Extremely Dangerous, Legendary Villain)
    ALIAS: (a dramatic nickname)
    POSTER_TEXT: (a dramatic 2-3 sentence wanted poster description written in old English fantasy style)
    CAUTION: (a one sentence warning to bounty hunters)
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": prompt}],
        )
        # pull the text content out of the response object
        content = response.choices[0].message.content.strip()

        # default values in case any fields are missing from the response
        result = {
            "bounty": "",
            "threat_level": "",
            "alias": "",
            "poster_text": "",
            "caution": ""
        }

        # parse each line and map it to the correct field
        # relies on the model returning the exact field headers we asked for
        for line in content.split("\n"):
            if line.startswith("BOUNTY:"):
                result["bounty"] = line.replace("BOUNTY:", "").strip()
            elif line.startswith("THREAT_LEVEL:"):
                result["threat_level"] = line.replace("THREAT_LEVEL:", "").strip()
            elif line.startswith("ALIAS:"):
                result["alias"] = line.replace("ALIAS:", "").strip()
            elif line.startswith("POSTER_TEXT:"):
                result["poster_text"] = line.replace("POSTER_TEXT:", "").strip()
            elif line.startswith("CAUTION:"):
                result["caution"] = line.replace("CAUTION:", "").strip()

        logger.info(f"Poster generated: {result}")
        return result

    except Exception as e:
        # if something goes wrong return N/A for all fields so the app doesn't crash
        logger.error(f"OpenAI API error: {e}")
        return {
            "bounty": "N/A",
            "threat_level": "N/A",
            "alias": "N/A",
            "poster_text": "N/A",
            "caution": "N/A"
        }
async def generate_portrait(description: str, race: str, char_class: str) -> str:
    """generates a fantasy character portrait using DALL-E 3 based on the character description"""
    try:
        response = await client.images.generate(
            model="dall-e-3",
            prompt=f"Fantasy DnD wanted poster portrait of a {race} {char_class}. {description}. Medieval fantasy art style, parchment background. Close up face portrait. No text.",
            n=1,
            size="1024x1024"
        )
        return response.data[0].url
    except Exception as e:
        logger.error(f"DALL-E error: {e}")
        return ""