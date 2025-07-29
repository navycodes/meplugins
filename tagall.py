import random
import asyncio
import config
from core import app
from utils.decorators import ONLY_ADMIN, ONLY_GROUP
from pyrogram import filters, errors, enums

active_tasks = {}
admins_tasks = {}

__MODULE__ = "Mention"
__HELP__ = """
<blockquote expandable>
<b>📣 Mention Users</b>

<b>★ /tagall</b> | <b>/all</b> | <b>/utag</b> [text/reply] – Mention all members.  
<b>★ /tagadmins</b> | <b>/admins</b> [text/reply] – Mention all admins.  
<b>★ /cancel</b> – Stop the mention process.

<i>Mentions automatically stop after 5 minutes.</i>
</blockquote>
"""


def random_emoji():
    emojis = "🍦 🎈 🎸 🌼 🌳 🚀 🎩 📷 💡 🏄‍♂️ 🎹 🚲 🍕 🌟 🎨 📚 🚁 🎮 🍔 🍉 🎉 🎵 🌸 🌈 🏝️ 🌞 🎢 🚗 🎭 🍩 🎲 📱 🏖️ 🛸 🧩 🚢 🎠 🏰 🎯 🥳 🎰 🛒 🧸 🛺 🧊 🛷 🦩 🎡 🎣 🏹 🧁 🥨 🎻 🎺 🥁 🛹".split(" ")
    return random.choice(emojis)

@app.on_message(filters.command(["utag", "all", "tagall"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def tagall_cmd(client, message):
    chat_id = message.chat.id
    proses = await message.reply(">**Please wait ...**")
    replied = message.reply_to_message
    if active_tasks.get(chat_id):
        return await proses.edit(">❌ Mention already running in this chat. Use `/cancel` to stop it.")
    text = None
    if len(message.command) >= 2:
        text = message.text.split(maxsplit=1)[1]
    elif replied:
        text = replied.text or replied.caption
    if not text:
        return await proses.edit(">**Please reply to a message or provide text!**")


    await proses.edit(">🔔 Mention running. Type `/cancel` to stop. Auto timeout in 5 minutes.")

    active_tasks[chat_id] = True

    async def tag_members():
        usernum = 0
        usertxt = ""

        try:
            async for m in client.get_chat_members(chat_id):
                if not active_tasks.get(chat_id):
                    return await proses.edit(">❌ Mention was cancelled!")

                if m.user.is_deleted or m.user.is_bot:
                    continue

                usernum += 1
                usertxt += f"<blockquote>[{random_emoji()}](tg://user?id={m.user.id})</blockquote>"

                if usernum == 7:
                    if replied:
                        await replied.reply_text(usertxt, disable_web_page_preview=True)
                    else:
                        text = message.text.split(maxsplit=1)[1]
                        await client.send_message(chat_id, f"<blockquote><b>{text}</b></blockquote>\n<blockquote><b>{usertxt}</blockquote></b>", disable_web_page_preview=True)
                    await asyncio.sleep(5)
                    usernum = 0
                    usertxt = ""

            if usernum != 0:
                if replied:
                    await replied.reply_text(usertxt, disable_web_page_preview=True)
                else:
                    text = message.text.split(maxsplit=1)[1]
                    await client.send_message(chat_id, f"<blockquote><b>{text}\n{usertxt}</b></blockquote>", disable_web_page_preview=True)

        except errors.FloodWait as e:
            await asyncio.sleep(e.value)

        finally:
            active_tasks.pop(chat_id, None)

    try:
        await asyncio.wait_for(tag_members(), timeout=300)
    except asyncio.TimeoutError:
        active_tasks.pop(chat_id, None)
        await proses.edit(">⏰ Task timeout after 5 minutes!")
        return

    await proses.delete()


@app.on_message(filters.command("cancel") & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def cancel_tagall(_, message):
    chat_id = message.chat.id
    if active_tasks.pop(chat_id, None):
        return await message.reply(">**✅ Mention cancelled!**")
    elif admins_tasks.pop(chat_id, None):
        return await message.reply(">**✅ Mention admin cancelled!**")
    else:
        return await message.reply(">**⚠️ No active mention running.**")



@app.on_message(filters.command(["tagadmins"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def tagadmins_cmd(client, message):
    chat_id = message.chat.id
    proses = await message.reply(">**Please wait ...**")
    replied = message.reply_to_message
    if admins_tasks.get(chat_id):
        return await proses.edit(">❌ Mention already running in this chat. Use `/cancel` to stop it.")
    text = None
    if len(message.command) >= 2:
        text = message.text.split(maxsplit=1)[1]
    elif replied:
        text = replied.text or replied.caption
    if not text:
        return await proses.edit(">**Please reply to a message or provide text!**")
    await proses.edit(">🔔 Mention running. Type `/cancel` to stop. Auto timeout in 5 minutes.")
    admins_tasks[chat_id] = True
    usernum = 0
    usertxt = ""
    try:
        async for m in client.get_chat_members(
            message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS
        ):
            if not admins_tasks.get(chat_id):
                return await proses.edit(">❌ Mention was cancelled!")
            if m.user.is_deleted or m.user.is_bot:
                continue
            usernum += 1
            usertxt += f"<blockquote>[{random_emoji()}](tg://user?id={m.user.id})</blockquote>"
            if usernum == 7:
                if replied:
                    await replied.reply_text(usertxt, disable_web_page_preview=True)
                else:
                    text = message.text.split(maxsplit=1)[1]
                    await client.send_message(chat_id, f"<blockquote>{text}</blockquote>\n<blockquote>{usertxt}</blockquote>", disable_web_page_preview=True)
                await asyncio.sleep(2)
                usernum = 0
                usertxt = ""
        if usernum != 0:
            if replied:
                await replied.reply_text(usertxt, disable_web_page_preview=True)
            else:
                text = message.text.split(maxsplit=1)[1]
                await client.send_message(chat_id, f"<blockquote>{text}</blockquote>\n<blockquote>{usertxt}</blockquote>", disable_web_page_preview=True)
    except errors.FloodWait as e:
        await asyncio.sleep(e.value)
    finally:
        admins_tasks.pop(chat_id, None)
    return await proses.delete()
