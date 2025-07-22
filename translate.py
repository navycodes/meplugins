import config
import traceback
from core import app
from gpytranslate import Translator
from pyrogram import filters
from utils.functions import Tools
from utils.database import dB

__MODULE__ = "Translate"
__HELP__ = """
<blockquote expandable>
<b>🌐 Translate Text</b>

<b>★ /tr</b> [text/reply] – Translate the given text.  
<b>★ /trlang</b> – View available language codes.  
<b>★ /setlang</b> (lang code) – Set your default translation language.
</blockquote>
"""


async def get_translate(chat_id):
    data = await dB.get_var(chat_id, "_translate")
    if data:
        return data
    return "id"

@app.on_message(filters.command(["tr"]) & ~config.BANNED_USERS)
async def tr_cmd(client, message):
    try:
        trans = Translator()
        user_id = message.from_user.id if message.from_user else message.sender_chat.id
        bhs = await get_translate(user_id)
        if message.reply_to_message:
            txt = message.reply_to_message.text or message.reply_to_message.caption
            src = await trans.detect(txt)
        else:
            if len(message.command) < 2:
                return await message.reply(">**Please reply to message text or give text!**")
            else:
                txt = message.text.split(None, 1)[1]
                src = await trans.detect(txt)
        trsl = await trans(txt, sourcelang=src, targetlang=bhs)
        reply = f"**Translated:**\n\n<blockquote expandable>{trsl.text}</blockquote>"
        rep = message.reply_to_message or message
        return await client.send_message(message.chat.id, reply, reply_to_message_id=rep.id)
    except Exception:
        print(traceback.format_exc())


@app.on_message(filters.command(["trlang"]) & ~config.BANNED_USERS)
async def lang_cmd(_, message):
    try:
        try:
            bhs_list = "\n".join(
                f"- **{lang}**: `{code}`" for lang, code in Tools.kode_bahasa.items()
            )
            return await message.reply(f"**Language codes:**\n\n<blockquote expandable>{bhs_list}</blockquote>")
        except Exception as e:
            return await message.reply(f"**Error: {str(e)}**")
    except Exception:
        print(traceback.format_exc())


@app.on_message(filters.command(["setlang"]) & ~config.BANNED_USERS)
async def setlang_cmd(_, message):
    try:
        if len(message.command) < 2:
            return await message.reply(">**Please give me lang code or type /trlang to view lang code**")
        for lang, code in Tools.kode_bahasa.items():
            kd = message.text.split(None, 1)[1]
            if kd.lower() == code.lower():
                await dB.set_var(message.from_user, "_translate", kd.lower())
                return await message.reply(f"**Successfully changed your translate language to: {lang}-{kd} and saved in database.**")
    except Exception:
        print(traceback.format_exc())