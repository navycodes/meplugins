import config
import traceback
from core import app
from gpytranslate import Translator
from pyrogram import filters
from utils.functions import Tools
from utils.database import dB
from textwrap import shorten
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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


emoji_flags = {
    "af": "🇿🇦",
    "is": "🇮🇸",
    "jv": "🇮🇩",
    "jw": "🇮🇩",
    "la": "🇱🇦",
    "my": "🇲🇲",
    "ne": "🇳🇵",
    "su": "🇮🇩",
    "sv": "🇸🇪",
    "tl": "🇵🇭",
    "ca": "🎗️",
    "da": "🇩🇰",
    "fi": "🇫🇮",
    "uk": "🇺🇦",
    "hu": "🇭🇺",
    "en": "🇬🇧",
    "id": "🇮🇩",
    "ja": "🇯🇵",
    "ko": "🇰🇷",
    "ru": "🇷🇺",
    "de": "🇩🇪",
    "es": "🇪🇸",
    "fr": "🇫🇷",
    "ar": "🇸🇦",
    "tr": "🇹🇷",
    "hi": "🇮🇳",
    "pt": "🇵🇹",
    "it": "🇮🇹",
    "zh": "🇨🇳",
    "nl": "🇳🇱",
    "th": "🇹🇭",
    "vi": "🇻🇳",
    "cs": "🇨🇿",
    "el": "🇬🇷",
    "pl": "🇵🇱",
    "zh-cn": "🇨🇳",
    "zh-tw": "🇹🇼",
}


def get_language_keyboard(user_id: int, lang_dict: dict, row_width=3):
    buttons = []
    row = []
    for name, code in lang_dict.items():
        flag = emoji_flags.get(code.lower(), "🏳️")
        label = f"{flag} {code.upper()}"
        row.append(InlineKeyboardButton(label, callback_data=f"setlang_{code}_{user_id}"))
        if len(row) == row_width:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


@app.on_message(filters.command(["setlang"]) & ~config.BANNED_USERS)
async def setlang_cmd(client, message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text(
            "><b>🌐 Please Choose a language on the Button Below:</b>",
            reply_markup=get_language_keyboard(message.from_user.id, Tools.kode_bahasa)
        )

    pros = await message.reply("**Processing...**")
    kd = args[1].lower()
    for lang, code in Tools.kode_bahasa.items():
        if kd == code.lower():
            await dB.set_var(client.me.id, "_translate", kd)
            return await pros.edit(
                "<b>✅ Language set to:</b> "
                f"<code>{lang} ({code})</code>"
            )
    return await pros.edit(
        f"<b>⚠️ Language code not recognized:</b> <code>{kd}</code>\n"
        f"Use <code>/setlang</code> to view available options."
    )


@app.on_callback_query(filters.regex(r"^setlang_([^_]+)_(\d+)$"))
async def setlang_cb(client, callback):
    code, user_id = callback.matches[0].group(1), int(callback.matches[0].group(2))

    if callback.from_user.id != user_id:
        return await callback.answer("⚠️ You are not allowed to use this button.", show_alert=True)

    for lang, c in Tools.kode_bahasa.items():
        if code == c.lower():
            await dB.set_var(user_id, "_translate", code)
            return await callback.message.edit(
                f"<b>✅ Language set to:</b> <code>{lang}</code> (<code>{code.upper()}</code>)",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚮 Close", callback_data="close")]
                ])
            )
    return await callback.answer("❌ Invalid language!", show_alert=True)


# @app.on_message(filters.command(["setlang"]) & ~config.BANNED_USERS)
# async def setlang_cmd(_, message):
#     try:
#         if len(message.command) < 2:
#             return await message.reply(">**Please give me lang code or type /trlang to view lang code**")
#         for lang, code in Tools.kode_bahasa.items():
#             kd = message.text.split(None, 1)[1]
#             if kd.lower() == code.lower():
#                 await dB.set_var(message.from_user.id, "_translate", kd.lower())
#                 return await message.reply(f"**Successfully changed your translate language to: {lang}-{kd} and saved in database.**")
#     except Exception:
#         print(traceback.format_exc())
