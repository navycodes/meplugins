import traceback

from pyrogram import enums, filters

from core import app
from utils.database import dB
from utils.functions import Tools
from utils.keyboard import Button
from logs import LOGGER
from utils.decorators import ONLY_GROUP, ONLY_ADMIN

from config import BANNED_USERS

@app.on_message(filters.command(["savenote", "addnote", "note"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def addnote_cmd(_, message):
    xx = await message.reply(">**Please wait...**")
    rep = message.reply_to_message
    if len(message.command) < 2 or not rep:
        return await xx.edit(f">**Please reply message and give note name**")
    nama = message.text.split()[1]
    getnotes = await dB.get_var(message.chat.id, nama, "NOTES")
    if getnotes:
        return await xx.edit(f">**Note {nama} already exist!**")
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
        await dB.set_var(message.chat.id, nama, value, "NOTES")
        return await xx.edit(f">**Saved {nama} note!!**")
    else:
        return await xx.edit(f">**Please reply message and give note name**")


@app.on_message(filters.command(["getnote", "get"]) & ~BANNED_USERS)
async def getnote_cmd(client, message):
    xx = await message.reply(">**Please wait...**")
    try:
        if len(message.text.split()) == 2:
            note = message.text.split()[1]
            data = await dB.get_var(message.chat.id, note, "NOTES")
            if not data:
                return await xx.edit(f">**Note {note} not found!**")
            return await get_notes(client, message, xx, data)
        
        elif len(message.text.split()) == 3 and (message.text.split())[2] in [
            "noformat",
            "raw",
        ]:
            note = message.text.split()[1]
            data = await dB.get_var(message.chat.id, note, "NOTES")
            if not data:
                return await xx.edit(f">**Note {note} not found!**")
            return await get_raw_note(client, message, xx, data)
        else:
            return await xx.edit(
                f">**Please valid command.\nExample: `{message.text.split()[0]} ciah noformat`.**"
            )
    except Exception as e:
        return await xx.edit(f">**ERROR**: {str(e)}")



#@app.on_message(filters.incoming & filters.group & ~filters.bot & ~filters.via_bot & ~BANNED_USERS, group=14)
async def getnote_cmd(client, message):
    text = message.text
    if not text:
        return
    if not text.startswith("#"):
        return
    xx = await message.reply(">**Please wait...**")
    try:
        note = text.strip().replace("#", "")
        data = await dB.get_var(message.chat.id, note, "NOTES")
        if not data:
            return await xx.edit(f">**Note {note} not found!**")
        return await get_notes(client, message, xx, data)
    except Exception as e:
        return await xx.edit(f">**ERROR**: {str(e)}")

async def get_notes(_, message, xx, data):
    try:
        teks = data["result"]
        type = data["type"]
        file_id = data["file_id"]
        main_text, button = Button.parse_msg_buttons(teks)
        formatted_text = await Tools.escape_filter(message, main_text, Tools.parse_words)
        if button:
            button = await Button.create_inline_keyboard(button, message.chat.id)
        else:
            button = None
        if type == "text":
            await message.reply(
                formatted_text,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=button
            )
        elif type == "sticker":
            await message.reply_sticker(
                file_id,
                reply_markup=button
            )
        elif type == "video_note":
            await message.reply_video_note(
                file_id,
                reply_markup=button
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
                    caption=formatted_text,
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=button
                )
    except Exception as er:
        LOGGER.info(f"ERROR: {traceback.format_exc()}")
        return await message.reply(f">**ERROR**: {str(er)}")
    return await xx.delete()


async def get_raw_note(_, message, xx, data):
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

@app.on_message(filters.command(["notes", "allnote"]) & ~BANNED_USERS)
async def notes_cmd(_, message):
    xx = await message.reply(">**Please wait...**")
    getnotes = await dB.all_var(message.chat.id, "NOTES")
    if not getnotes:
        return await xx.edit(f">**Thits chat dont have any note!**")
    rply = f">**List of Notes:**\n\n"
    for x, data in getnotes.items():
        type = await dB.get_var(message.chat.id, x, "NOTES")
        rply += f"**• Name: `{x}` | Type: `{type['type']}`**\n"
    return await xx.edit(rply)

@app.on_message(filters.command(["clearnote", "delnote"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def clearnote_cmd(client, message):
    args = client.get_arg(message).split(",")
    xx = await message.reply(">**Please wait...**")
    if len(args) == 0 or (len(args) == 1 and args[0].strip() == ""):
        return await xx.edit(f">**Which note do you want to delete?**")
    if message.command[1] == "all":
        if not await dB.all_var(message.chat.id, "NOTES"):
            return await xx.edit(f">**You dont have any note!**")
        for nama in await dB.all_var(message.chat.id, "NOTES"):
            data = await dB.get_var(message.chat.id, nama, "NOTES")
            await dB.remove_var(message.chat.id, nama, "NOTES")
        return await xx.edit(f">**Succesfully deleted all note!**")
    else:
        gagal_list = []
        sukses_list = []

        for arg in args:
            arg = arg.strip()
            if not arg:
                continue
            data = await dB.get_var(message.chat.id, arg, "NOTES")
            if not data:
                gagal_list.append(arg)
            else:
                await dB.remove_var(message.chat.id, arg, "NOTES")
                sukses_list.append(arg)

        if sukses_list:
            return await xx.edit(
                f">**Note `{', '.join(sukses_list)}` successfully deleted.**"
            )

        if gagal_list:
            return await xx.edit(
                f">**Note `{', '.join(gagal_list)}` not found!**"
            )
        

__MODULE__ = "Notes"
__HELP__ = """
<blockquote expandable>
<b>★ /savenote [name]</b> - Save replied message as a note.  
<b>★ /getnote [name]</b> - Get note by name with formatting & buttons.  
<b>★ /getnote [name] noformat</b> - Get note without formatting/buttons.  
<b>★ /notes</b> or <b>/allnote</b> - Show list of saved notes in group.  
<b>★ /clearnote [name1,name2,...]</b> - Delete specific notes (comma separated).  
<b>★ /clearnote all</b> - Delete all notes in group.

✅ Notes can contain:
- Text
- Media (photo, video, voice, file, sticker, animation)
- Inline buttons

💡 Buttons supported via format:
    <i>Supports markdown & custom response formatting.</i>
</blockquote>
"""
