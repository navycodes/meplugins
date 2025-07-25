import traceback
from typing import List, Literal, Optional, Tuple
import httpx
import mimetypes
import random
from core import app
import config
from utils.database import dB

from pyrogram import filters

from logs import LOGGER


__MODULE__ = "Waifu"
__HELP__ = """
<blockquote expandable>
<b>🎌 Anime 📖</b>

<b>🌸 SFW</b>
★ /slap [Optipnal(Reply to User Message)] Send Random Media slapping.
★ /waifu [Optipnal(Reply to User Message)] Send Random Media Waifu.
★ /shinobu [Optipnal(Reply to User Message)] Send Random Media Shinobu.
★ /megumin [Optipnal(Reply to User Message)] Send Random Media Megumin.
★ /bully [Optipnal(Reply to User Message)] Send Random Media Bully.
★ /cuddle [Optipnal(Reply to User Message)] Send Random Media Cuddle.
★ /cry [Optipnal(Reply to User Message)] Send Random Media Cry.
★ /hug [Optipnal(Reply to User Message)] Send Random Media Hug.
★ /awoo [Optipnal(Reply to User Message)] Send Random Media Awoo.
★ /kiss [Optipnal(Reply to User Message)] Send Random Media Kiss.
★ /lick [Optipnal(Reply to User Message)] Send Random Media Lick.
★ /pat [Optipnal(Reply to User Message)] Send Random Media Pat.
★ /smug [Optipnal(Reply to User Message)] Send Random Media Smug.
★ /boonk [Optipnal(Reply to User Message)] Send Random Media Boonk.
★ /yeet [Optipnal(Reply to User Message)] Send Random Media Yeet.
★ /blush [Optipnal(Reply to User Message)] Send Random Media Blush.
★ /smile [Optipnal(Reply to User Message)] Send Random Media Smile.
★ /wave [Optipnal(Reply to User Message)] Send Random Media Wave.
★ /highfive [Optipnal(Reply to User Message)] Send Random Media HighFive.
★ /handhold [Optipnal(Reply to User Message)] Send Random Media HandHold.
★ /nom [Optipnal(Reply to User Message)] Send Random Media Nom.
★ /bite [Optipnal(Reply to User Message)] Send Random Media Bite.
★ /glomp [Optipnal(Reply to User Message)] Send Random Media Glomp.
★ /kill [Optipnal(Reply to User Message)] Send Random Media Kill.
★ /happy [Optipnal(Reply to User Message)] Send Random Media Happy.
★ /wink [Optipnal(Reply to User Message)] Send Random Media Wink.
★ /poke [Optipnal(Reply to User Message)] Send Random Media Poke.
★ /dance [Optipnal(Reply to User Message)] Send Random Media Dance.
★ /cringe [Optipnal(Reply to User Message)] Send Random Media Cringe.
<b> ---------------------------------------</b>
<b>🔞 NSFW</b>
★ /waifu [Optipnal(Reply to User Message)] Send Random Nsfw Media Waifu.
★ /neko [Optipnal(Reply to User Message)] Send Random Nsfw Media Neko.
★ /trap [Optipnal(Reply to User Message)] Send Random Nsfw Media Trap.
★ /blowjob [Optipnal(Reply to User Message)] Send Random Nsfw Media BlowJob.
"""


SFW_ENDPOINTS = [
    "slap", "waifu", "shinobu", "megumin", "bully", "cuddle", "cry", "hug",
    "awoo", "kiss", "lick", "pat", "smug", "boonk", "yeet", "blush", "smile",
    "wave", "highfive", "handhold", "nom", "bite", "glomp", "kill", "happy",
    "wink", "poke", "dance", "cringe",
]

NSFW_ENDPOINTS = ["waifu", "neko", "trap", "blowjob"]

COMMAND_PATTERN = list(dict.fromkeys(SFW_ENDPOINTS + NSFW_ENDPOINTS))


async def get_mime_type(url: str) -> str:
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(5.0), follow_redirects=True
        ) as client:
            res = await client.head(url)
            content_type = res.headers.get("Content-Type", "")
            if content_type:
                return content_type.lower()
    except Exception as e:
        LOGGER.error(f"Error: {e}")

    mime, _ = mimetypes.guess_type(url)
    return mime or "application/octet-stream"



class AnimePics:
    BASE_URL = "https://api.waifu.pics"

    def __init__(self, timeout: httpx.Timeout = 10):
        self.client = httpx.AsyncClient(timeout=timeout)

    async def get_image(
        self, category: Literal["sfw", "nsfw"] = "sfw", endpoint: str = "waifu"
    ) -> Optional[str]:
        url = f"{self.BASE_URL}/{category}/{endpoint}"
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            url = response.json().get("url")
            LOGGER.info(f"Url: {url}")
            return url
        except Exception as e:
            LOGGER.error(f"Error get_image: {e}")
            return None

    async def get_many(
        self,
        category: Literal["sfw", "nsfw"] = "sfw",
        endpoint: str = "waifu",
        count: int = 5,
    ) -> List[str]:
        url = f"{self.BASE_URL}/many/{category}/{endpoint}"
        try:
            response = await self.client.post(url, json={"exclude": [], "num": count})
            response.raise_for_status()
            return response.json().get("files", [])
        except Exception as e:
            LOGGER.error(f"Error get_many: {e}")
            return []

    async def close(self):
        await self.client.aclose()


animp = AnimePics()


@app.on_message(filters.command(COMMAND_PATTERN) & ~config.BANNED_USERS)
async def waifu_command(client, message):
    cmd = message.command[0].lower()
    category = "sfw" if cmd in SFW_ENDPOINTS else "nsfw"
    url = await animp.get_image(category, cmd)
    database_links = cmd.upper() + "DB"
    urls = await dB.get_list_from_var(config.BOT_ID, database_links)
    if not url:
        if urls:
            url = random.choice(urls)
        else:
            return await message.reply(
                f"><b>Gagal mengambil media <code>{cmd}</code></b>"
            )

    if url not in urls:
        await dB.add_to_var(config.BOT_ID, database_links, url)

    mime_type = await get_mime_type(url)

    try:
        reply_id = await client.ReplyCheck(message)
        if mime_type == "image/gif" or mime_type.startswith("video/"):
            await message.reply_video(url, reply_to_message_id=reply_id)
        elif mime_type.startswith("image/"):
            await message.reply_photo(url, reply_to_message_id=reply_id)
        else:
            await message.reply(url, reply_to_message_id=reply_id)
        return await message.delete()
    except Exception as e:
        return await message.reply(
            f"<b>Gagal kirim media:</b>\n\n<pre><code>{e}</code></pre>"
        )
