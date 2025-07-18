import asyncio
import traceback

import config
from pyrogram import enums, filters, errors
from core import app
from utils.database import dB, is_banned_user
from utils.functions import Tools
from utils.keyboard import Button
from utils.decorators import ONLY_GROUP, ONLY_ADMIN
from utils.misc import SUDOERS
from utils.query_group import goodbye_group, welcome_group


@app.on_message(filters.command(["setwelcome", "addwelcome"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def welcome_set(client, message):
    if not message.reply_to_message:
        return await message.reply(f"**Usage command: `/setwelcome` (reply message).**"
        )
    rep = message.reply_to_message
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
        await dB.set_var(message.chat.id, "WELCOME_TEXT", value)
    return await message.reply(f"**Welcome Greetings status set to: [this]({rep.link})", disable_web_page_preview=True)

@app.on_message(filters.command(["welcome"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def status_welcome(client, message):
    data = await dB.get_var(message.chat.id, "WELCOME_TEXT")
    if not data:
        return await message.reply(
            "**You have not set a welcome message for this group.**"
        )
    type = data["type"]
    file_id = data["file_id"]
    teks = data["result"]
    sended = None
    if type == "text":
        sended = await message.reply(
            teks,
            parse_mode=enums.ParseMode.DISABLED,
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
            sended = await kwargs[type](
                file_id,
                caption=teks,
                parse_mode=enums.ParseMode.DISABLED,
            )
    return await message.reply(
        "**This is a welcome greeting in this group**",
        reply_to_message_id=sended.id,
    )

@app.on_message(filters.command(["setgoodbye", "addgoodbye"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def goodbye_cmd(client, message):
    if not message.reply_to_message:
        return await message.reply(
            f"**Usage command: `/setgoodbye` (reply message).**"
        )
    rep = message.reply_to_message
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
        await dB.set_var(message.chat.id, "GOODBYE_TEXT", value)
    return await message.reply(
        f"**Goodbye Greetings status set to: [this]({rep.link})",
        disable_web_page_preview=True,
    )

@app.on_message(filters.command(["goodbye"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def goodbye_status(client, message):
    data = await dB.get_var(message.chat.id, "GOODBYE_TEXT")
    if not data:
        return await message.reply(
            "**You have not set a goodbye message for this group.**"
        )
    type = data["type"]
    file_id = data["file_id"]
    teks = data["result"]
    sended = None
    if type == "text":
        sended = await message.reply(
            teks,
            parse_mode=enums.ParseMode.DISABLED,
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
            sended = await kwargs[type](
                file_id,
                caption=teks,
                parse_mode=enums.ParseMode.DISABLED,
            )
    return await message.reply(
        "**This is a goodbye greeting in this group**",
        reply_to_message_id=sended.id,
    )

@app.on_message(filters.command(["resetwelcome"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def reset_welcome(_, message):
    await dB.remove_var(message.chat.id, "WELCOME_TEXT")
    return await message.reply(">**Succesfully deleted greetings welcome.**")

@app.on_message(filters.command(["resetgoodbye"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def reset_goodbye(_, message):
    await dB.remove_var(message.chat.id, "GOODBYE_TEXT")
    return await message.reply(">**Succesfully deleted greetings goodbye.**")



@app.on_chat_member_updated(filters.group, group=welcome_group)
async def join_members(client, member):
    if (
        member.new_chat_member
        and member.new_chat_member.status not in {enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.RESTRICTED}
        and not member.old_chat_member
    ):
        pass
    else:
        return
    try:
        user = member.new_chat_member.user if member.new_chat_member else member.from_user
        is_gbanned = await is_banned_user(user.id)
        if user.id == client.me.id:
            return
        if user.id in config.OWNER_ID:
            await client.send_animation(
                chat_id=member.chat.id,
                animation="assets/owner_welcome.mp4",
                caption=">😳 My **Owner** has also joined the chat!",
            )
            return
        if user.id in SUDOERS:
            await client.send_animation(
                chat_id=member.chat.id,
                animation="assets/owner_welcome.mp4",
                caption=">😳 **Sudoers** has also joined the chat!",
            )
            return
        if is_gbanned:
            await member.chat.ban_member(user.id)
            await client.send_message(
                member.chat.id,
                f">{user.mention} was globally banned so i banned!",
            )
            return
        if user.is_bot:
            return  # ignore bots
        data = await dB.get_var(member.chat.id, "WELCOME_TEXT")
        if not data:
            return
        msg_text = data["result"]
        data_type, file_id = data["type"], data.get("file_id")
        teks, button = Button.parse_msg_buttons(msg_text)
        teks_formated = await Tools.escape_greetings(member, True, teks, Tools.parse_words)
        if button:
            reply_markup = await Button.create_inline_keyboard(button)
            if data_type == "text":
                await client.send_message(
                    member.chat.id,
                    teks_formated,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                    parse_mode=enums.ParseMode.HTML,
                )
            else:
                kwargs = {
                    "photo": client.send_photo,
                    "voice": client.send_voice,
                    "audio": client.send_audio,
                    "video": client.send_video,
                    "animation": client.send_animation,
                    "document": client.send_document,
                }
                if data_type in kwargs:
                    await kwargs[data_type](
                        member.chat.id,
                        file_id,
                        caption=teks_formated,
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=reply_markup
                    )
        else:
            if data_type == "text":
                await client.send_message(
                    member.chat.id,
                    teks_formated,
                    disable_web_page_preview=True,
                    parse_mode=enums.ParseMode.HTML,
                )
            else:
                kwargs = {
                    "photo": client.send_photo,
                    "voice": client.send_voice,
                    "audio": client.send_audio,
                    "video": client.send_video,
                    "animation": client.send_animation,
                    "document": client.send_document,
                }
                if data_type in kwargs:
                    await kwargs[data_type](
                        member.chat.id,
                        file_id,
                        caption=teks_formated,
                        parse_mode=enums.ParseMode.HTML,
                    )
            
    except Exception:
        pass



@app.on_chat_member_updated(filters.group, group=goodbye_group)
async def leave_members(client, member):
    if (
        not member.new_chat_member
        and member.old_chat_member.status not in {enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.RESTRICTED}
        and member.old_chat_member
    ):
        pass
    else:
        return
    try:
        user = member.old_chat_member.user if member.old_chat_member else member.from_user
        if user.id in config.OWNER_ID:
            await client.send_message(
                member.chat.id,
                ">**Hey master, dont leave me alone 😭**",
            )
            return
        data = await dB.get_var(member.chat.id, "GOODBYE_TEXT")
        if not data:
            return
        msg_text = data["result"]
        data_type, file_id = data["type"], data.get("file_id")
        teks, button = Button.parse_msg_buttons(msg_text)
        teks_formated = await Tools.escape_greetings(member, False, teks, Tools.parse_words)
        if button:
            reply_markup = await Button.create_inline_keyboard(button)
        else:
            reply_markup = None
        if data_type == "text":
            try:
                await client.send_message(
                    member.chat.id,
                    teks_formated,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                    parse_mode=enums.ParseMode.HTML,
                )
            except errors.FloodWait as e:
                await asyncio.sleep(e.value)
                await client.send_message(
                    member.chat.id,
                    teks_formated,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                    parse_mode=enums.ParseMode.HTML,
                )
            except Exception:
                pass

        else:
            kwargs = {
                "photo": client.send_photo,
                "voice": client.send_voice,
                "audio": client.send_audio,
                "video": client.send_video,
                "animation": client.send_animation,
                "document": client.send_document,
            }
            if data_type in kwargs:
                try:
                    await kwargs[data_type](
                        member.chat.id,
                        file_id,
                        caption=teks_formated,
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=reply_markup
                    )
                except errors.FloodWait as e:
                    await asyncio.sleep(e.value)
                    await kwargs[data_type](
                        member.chat.id,
                        file_id,
                        caption=teks_formated,
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=reply_markup
                    )
                except Exception:
                    pass
            
    except Exception:
        pass


__MODULE__ = "Greetings"
__HELP__ = """
<blockquote expandable>
<b>👋 Welcome & Goodbye Messages</b>

<b>★ /setwelcome</b> (reply) – Set a custom welcome message.  
<b>★ /welcome</b> – Check current welcome settings.  
<b>★ /setgoodbye</b> (reply) – Set a custom goodbye message.  
<b>★ /goodbye</b> – Check current goodbye settings.  
<b>★ /resetwelcome</b> – Disable the welcome message.  
<b>★ /resetgoodbye</b> – Disable the goodbye message.

<i>You can use markdown and fill-ins for custom messages.</i>
</blockquote>
"""
