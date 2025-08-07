import traceback
import config

from pyrogram import filters
from core import app
from utils.functions import Tools
from logs import LOGGER


__MODULE__ = "ChatGPT"

__HELP__ = """
<blockquote expandable>

🤖 <b>Ask ChatGPT</b>

• <b>/ask</b> (question) – Ask anything to ChatGPT (v3).

</blockquote>
"""


@app.on_message(filters.command(["ask"]) & ~config.BANNED_USERS)
async def chatgpt_cmd(client, message):
    proses = await message.reply(">**Proses your request...**")
    if len(message.command) < 2:
        return await proses.edit(
            f">**Please give a prompt or question.**"
        )
    prompt = client.get_text(message)
    payload = [{"role": "system", "content": f"kamu adalah asisten virtual diaplikasi telegram bernama {client.name} yang ceria"}, {"role": "user", "content": prompt.strip()}]
    try:
        r = await Tools.fetch.post("https://api.siputzx.my.id/api/ai/gpt3", json=payload)
        if r.status_code != 200:
            return await proses.edit(">**Please try again later, maybe server is down.**")
        data = r.json()
        return await proses.edit(data.get("data"))
    except Exception as e:
        LOGGER.error(traceback.format_exc())
        return await proses.edit(f">**Terjadi kesalahan:**\n`{e}`")
