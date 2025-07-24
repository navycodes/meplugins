import re
import traceback

from pyrogram import enums, filters

from core import app
from utils.database import dB
from utils.functions import Tools
from utils.keyboard import Button
from logs import LOGGER
from utils.decorators import ONLY_GROUP, ONLY_ADMIN
from utils.query_group import filter_group

from config import BANNED_USERS


@app.on_message(filters.command(["savefilter", "addfilter", "filter"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def filter_cmd(_, message):
    rep = message.reply_to_message
    if len(message.command) < 2 or not rep:
        return await message.reply("><b>Please reply message and give filter name ..</b>")
    xx = await message.reply("><b>Please wait...</b>")
    nama = message.text.split()[1]
    getfilter = await dB.get_var(message.chat.id, nama, "FILTER")
    if getfilter:
        return await xx.edit(
            f"><b>Filter <code>{nama}</code> already exist!</b>"
        )
    value = None

    text = rep.text or rep.caption or ""
    if rep.media and rep.media != enums.MessageMediaType.WEB_PAGE_PREVIEW:
        media = Tools.get_file_id(rep)
        value = {
            "type": media["message_type"],
            "file_id": media["file_id"],
            "result": text,
        }
    else:
        value = {"type": "text", "file_id": "", "result": text}
    if value:
        await dB.set_var(message.chat.id, nama, value, "FILTER")
        return await xx.edit(
            f"><b>Successfully Save New Filter as <code>{nama}</code>.</b>"
        )
    else:
        return await xx.edit(
            "><b>Please reply message and give filter name!</b>"
        )

@app.on_message(filters.command(["getfilter"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def getfilter_cmd(client, message):
    xx = await message.reply("><b>Please wait...</b>")
    try:
        if len(message.text.split()) == 3 and (message.text.split())[2] in [
            "noformat",
            "raw",
        ]:
            filter_name = message.text.split()[1]
            data = await dB.get_var(message.chat.id, filter_name, "FILTER")
            if not data:
                return await xx.edit(
                    f"><b>Filter <code>{filter_name}</code> not found!</b>"
                )
            return await get_raw_filter(client, message, xx, data)
        else:
            return await xx.edit(
                f"><b>Command Invalid!</b>\n><b>Example:</b>\n\n> •<code>{message.text.split()[0]} ciah noformat</code>."
            )
    except Exception as e:
        return await xx.edit(
            f"><b>ERROR</b>:\n\n<pre><code>{str(e)}</code></pre>"
        )


async def get_raw_filter(_, message, xx, data):
    try:
        teks = data["result"]
        type = data["type"]
        file_id = data["file_id"]

        if type == "text":
            await message.reply(
                teks,
                parse_mode=enums.ParseMode.DISABLED,
            )
        elif type == "sticker":
            await message.reply_sticker(
                file_id,
            )
        elif type == "video_note":
            await message.reply_video_note(
                file_id,
            )
        else:
            kwargs = {
                "photo": message.reply_photo,
                "voice": message.reply_voice,
                "audio": message.reply_audio,
                "video": message.reply_video,
                "animation": message.reply_animation,
                "document": message.reply_document,
            }

            if type in kwargs:
                await kwargs[type](
                    file_id,
                    caption=teks,
                    parse_mode=enums.ParseMode.DISABLED,
                )
    except Exception as er:
        LOGGER.info(f"ERROR: {traceback.format_exc()}")
        return await message.reply(f">**ERROR**: {str(er)}")
    return await xx.delete()


@app.on_message(filters.command(["filters", "allfilter"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def filters_cmd(_, message):
    xx = await message.reply("><b>Please wait...</b>")
    getfilter = await dB.all_var(message.chat.id, "FILTER")
    if not getfilter:
        return await xx.edit(
            f"><b>This {message.chat.title or 'Chat'} dont have any filter!</b>"
        )
    rply = "><b>List of Filters:</b>\n\n"
    for x, data in getfilter.items():
        type = await dB.get_var(message.chat.id, x, "FILTER")
        rply += f"<b>• Name: <code>{x}</code> | Type: <code>{type['type']}</code></b>\n"
    return await xx.edit(rply)


@app.on_message(filters.command(["stopfilter", "clearfilter"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def stopfilter_cmd(client, message):
    args_text = client.get_arg(message) or ""
    args = args_text.split(",")

    xx = await message.reply("><b>Please wait...</b>")

    if not args_text.strip():
        return await xx.edit("><b>Which filter do you want to delete?</b>")

    if len(message.command) > 1 and message.command[1].lower() == "all":
        all_filters = await dB.all_var(message.chat.id, "FILTER")
        if not all_filters:
            return await xx.edit("><b>You don't have any filters!</b>")
        for name in all_filters:
            await dB.remove_var(message.chat.id, name, "FILTER")
        return await xx.edit("><b>Successfully deleted all filters!</b>")

    gagal_list = []
    sukses_list = []

    for arg in args:
        arg = arg.strip()
        if not arg:
            continue
        data = await dB.get_var(message.chat.id, arg, "FILTER")
        if not data:
            gagal_list.append(arg)
        else:
            await dB.remove_var(message.chat.id, arg, "FILTER")
            sukses_list.append(arg)

    if sukses_list:
        return await xx.edit(
            f"><b>Filter <code>{', '.join(sukses_list)}</code> successfully deleted.</b>"
        )

    if gagal_list:
        return await xx.edit(
            f"><b>Filter <code>{', '.join(gagal_list)}<code> not found!</code>"
        )


@app.on_message(filters.incoming & filters.group & ~filters.bot & ~filters.via_bot & ~BANNED_USERS, group=filter_group)
async def FILTERS(_, message):
    try:
        text = message.text or message.caption
        if not text:
            return

        getfilter = await dB.all_var(message.chat.id, "FILTER")
        if not getfilter:
            return
        for word in getfilter:
            pattern = rf"\b{re.escape(word)}\b"
            if not re.search(pattern, text, flags=re.IGNORECASE):
                continue

            _filter = await dB.get_var(message.chat.id, word, "FILTER")
            data_type, file_id = _filter["type"], _filter.get("file_id")
            data = _filter["result"]
            if data_type != "text" and not file_id:
                continue
            teks, button = Button.parse_msg_buttons(data)
            teks_formated = await Tools.escape_filter(message, teks, Tools.parse_words)
            if button:
                reply_markup = await Button.create_inline_keyboard(button)
            else:
                reply_markup = None
            if data_type == "text":
                await message.reply(
                    teks_formated,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                    parse_mode=enums.ParseMode.HTML,
                )
            else:
                reply_senders = {
                    "photo": message.reply_photo,
                    "voice": message.reply_voice,
                    "audio": message.reply_audio,
                    "video": message.reply_video,
                    "animation": message.reply_animation,
                    "document": message.reply_document,
                    "sticker": message.reply_sticker,
                    "video_note": message.reply_video_note,
                }
                kwargs = {"reply_to_message_id": message.id, "reply_markup": reply_markup}
                if data_type not in ["sticker", "video_note"]:
                    kwargs["caption"] = teks_formated
                    kwargs["parse_mode"] = enums.ParseMode.HTML

                await reply_senders[data_type](file_id, **kwargs)
    except Exception:
        LOGGER.error(
            f"Eror filter pada pesan: {message.text}\n{traceback.format_exc()}"
        )


__MODULE__ = "Filters"

__HELP__ = """
<blockquote expandable>

📬 <b>Auto Reply Filters</b>

• <b>/savefilter</b> (keyword) (reply message) – Save a filter.
• <b>/filters</b> – View all active filters.
• <b>/getfilter</b> (name) raw – Get raw content of a filter.
• <b>/stopfilter</b> (name) – Remove a specific filter.
• <b>/stopfilter all</b> – Delete all filters in this chat.

<i>Supports markdown & custom response formatting.</i>

</blockquote>
"""
