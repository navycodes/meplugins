

import os
import config
import asyncio

from core import app
from pyrogram import filters, errors, types, enums

from utils.decorators import ONLY_GROUP, ONLY_ADMIN


__MODULE__ = "Admin-Tools"
__HELP__ = """
<blockquote expandable>
<b>🔧 Admin Tools</b>

<b>★ /promote</b> [reply/user_id] (custom title optional) - Promote a user to admin with basic rights.
<b>★ /fullpromote</b> [reply/user_id] (custom title optional) - Promote with full rights.
<b>★ /demote</b> [reply/user_id] - Revoke admin rights from a user.

<b>★ /staff</b> - Show structured list of admins, including bots and custom titles.

<b>★ /purge</b> [reply message] - Delete all messages from the replied message to the current one.
<b>★ /del</b> [reply message] - Delete the replied message only.

<b>★ /pin</b> [reply message] - Pin a message.
<b>★ /unpin</b> [reply message] - Unpin a message.

<i>All commands must be used by group admins or sudo users.</i>
</blockquote>
"""


@app.on_message(filters.command(["promote", "fullpromote", "demote"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def promote_cmd(client, message):
    reply = message.reply_to_message
    if reply and reply.sender_chat:
        return await message.reply(
            "><b>Please reply to a non-Anonymous user's message or provide your userID/userName..</b>"
        )
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply("><b>You need to specify a user (either by reply or username/ID)!</b>")
    try:
        user = await client.get_users(target)
    except (errors.PeerIdInvalid, KeyError, errors.UsernameInvalid, errors.UsernameNotOccupied, IndexError):
        return await message.reply("><b>You need meet before interact!!</b>")
    user_id = user.id
    mention = await client.get_mention_from_user_id(client, user_id)
    if user_id == client.me.id:
        return await message.reply_text("><b>How can I promote myself?</b>")
    command = message.command[0].lower()
    pros = await message.reply_text(f"><b>Process <code>{command}</b> {mention} ..</b>")
    if command != "demote":
        is_right = await client.get_chat_member(message.chat.id, client.me.id)
        if not is_right.privileges.can_promote_members:
            return await pros.edit_text(
                f"><b>I don't have right permissions to promote {mention} in {message.chat.titile or 'this group'}!</b>"
            )
    else:
        admin_ids = await client.admin_list(message)
        if user_id not in admin_ids:
            return await pros.edit_text(
                f"><b>Yes {mention} is still member!</b>"
            )

    try:
        if message.chat.type in [enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]:
            if len(message.text.split()) >= 3 and not message.reply_to_message:
                title = " ".join(message.text.split()[2:16])
            elif len(message.text.split()) >= 2 and message.reply_to_message:
                title = " ".join(message.text.split()[1:16])
            else:
                title = f"{user.first_name} {user.last_name or ''}".split()[:16]
            if command in ["promote", "fullpromote"]:
                privileges = types.ChatPrivileges(
                    can_manage_chat=True,
                    can_delete_messages=True,
                    can_manage_video_chats=True,
                    can_restrict_members=True,
                    can_promote_members=command == "fullpromote",
                    can_change_info=command == "fullpromote",
                    can_post_messages=command == "fullpromote",
                    can_edit_messages=command == "fullpromote",
                    can_manage_topics=command == "fullpromote",
                    can_post_stories=command == "fullpromote",
                    can_edit_stories=command == "fullpromote",
                    can_delete_stories=command == "fullpromote",
                    can_invite_users=True,
                    can_pin_messages=True,
                    is_anonymous=False,
                )
                try:
                    await client.promote_chat_member(
                        chat_id=message.chat.id,
                        user_id=user_id,
                        privileges=privileges,
                        title=title,
                    )
                except errors.AdminRankEmojiNotAllowed:
                    await client.promote_chat_member(
                        chat_id=message.chat.id,
                        user_id=user_id,
                        privileges=privileges,
                        title="Anak Kambing",
                    )
                return await pros.edit_text(
                    f"><b>Successfully promoted user {user.mention} to admin!</b>"
                )

            else: 
                await client.promote_chat_member(
                    chat_id=message.chat.id,
                    user_id=user_id,
                    privileges=types.ChatPrivileges(
                        can_change_info=False,
                        can_invite_users=False,
                        can_delete_messages=False,
                        can_restrict_members=False,
                        can_pin_messages=False,
                        can_promote_members=False,
                        can_manage_chat=False,
                        can_manage_video_chats=False,
                    ),
                )
                return await pros.edit_text(
                    f"><b>Successfully demoted user {mention} from admin!</b>"
                )
    except Exception as er:
        return await pros.edit_text(
            f"><b>ERROR:</b>\n\n<pre><code>{str(er)}</code></pre>"
        )


@app.on_message(filters.command(["staff"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def staff_cmd(client, message):
    chat = message.chat
    if chat.username:
        uname = chat.username
    else:
        uname = chat.id
    owner = []
    co_founder = []
    admin = []
    bot = []
    pros = await message.reply("><b>Please wait...</b>")
    await asyncio.sleep(1)
    if uname:
        chat_link = f"<a href='t.me/{uname}'>{chat.title}</a>"
    else:
        chat_link = f"<a href='{message.link}'>{chat.title}</a>"
    async for dia in client.get_chat_members(chat.id):
        user = dia.user
        ijin = dia.privileges
        status = dia.status
        title = dia.custom_title
        botol = user.is_bot
        mention = await client.get_mention_from_user(user)
        if (
            status == enums.ChatMemberStatus.ADMINISTRATOR
            and ijin.can_promote_members
            and ijin.can_manage_chat
            and ijin.can_delete_messages
            and ijin.can_manage_video_chats
            and ijin.can_restrict_members
            and ijin.can_change_info
            and ijin.can_invite_users
            and ijin.can_pin_messages
            and not botol
        ):
            if title:
                co_founder.append(f" ┣ {mention} <u>as</u> <i>{title}</i>")
            else:
                co_founder.append(f" ┣ {mention} <u>as</u> <i>Co-Founder</i>")
        elif status == enums.ChatMemberStatus.ADMINISTRATOR and not botol:
            if title:
                admin.append(f" ┣ {mention} <u>as</u> <i>{title}</i>")
            else:
                admin.append(f" ┣ {mention} <u>as</u> <i>Admin</i>")
        elif status == enums.ChatMemberStatus.OWNER:
            if title:
                owner.append(f" ┣ {mention} <u>as</u> <i>{title}</i>")
            else:
                owner.append(f" ┣ {mention} <u>as</u> <i>Founder</i>")
        elif botol:
            if title:
                bot.append(f" ┣ {mention} <u>as</u> <i>{title}</i>")
            else:
                bot.append(f" ┣ {mention} <u>as</u> <i>Bot Admin</i>")

    result = "<b>Administrator Structure in {}</b>\n\n\n".format(chat_link)
    if owner:
        on = owner[-1].replace(" ┣", "┗")
        owner.pop(-1)
        owner.append(on)
        result += "<b>👑 Founder : </b>\n ┃\n {}\n\n".format(owner[0])
    if co_founder:
        cof = co_founder[-1].replace(" ┣", " ┗")
        co_founder.pop(-1)
        co_founder.append(cof)
        result += "<b>👨🏻‍💻 Co-Founder : </b>\n ┃\n" + "\n".join(co_founder) + "\n\n"
    if admin:
        adm = admin[-1].replace(" ┣", " ┗")
        admin.pop(-1)
        admin.append(adm)
        result += "<b>🧑🏻‍💻 Admin : </b>\n ┃\n" + "\n".join(admin) + "\n\n"
    if bot:
        botak = bot[-1].replace(" ┣", " ┗")
        bot.pop(-1)
        bot.append(botak)
        result += "<b>🤖 Bots : </b>\n ┃\n" + "\n".join(bot) + "\n"

    photo_path = None
    if message.chat.photo:
        try:
            photo_path = await client.download_media(message.chat.photo.big_file_id)
            await client.send_photo(
                message.chat.id,
                photo=photo_path,
                caption=f"{result}",
            )
        except Exception:
            await message.reply(f"{result}", disable_web_page_preview=True)
    else:
        await message.reply(f"{result}", disable_web_page_preview=True)

    if photo_path and os.path.exists(photo_path):
        os.remove(photo_path)

    return await pros.delete()


@app.on_message(filters.command(["purge"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def purge_cmd(client, message):
    rep = message.reply_to_message
    if not rep:
        return await message.delete()

    chat_id = message.chat.id
    try:
        start_id = rep.id
        end_id = message.id
        message_ids = list(range(start_id, end_id))
        for i in range(0, len(message_ids), 100):
            await client.delete_messages(
                chat_id=chat_id, message_ids=message_ids[i : i + 100], revoke=True
            )
    except Exception:
        await message.delete()
    finally:
        await message.delete()


@app.on_message(filters.command(["del"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def del_cmd(_, message):
    await message.delete()
    try:
        return await message.reply_to_message.delete()
    except Exception:
        return


@app.on_message(filters.command(["pin", "unpin"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def pin_cmd(_, message):
    if not message.reply_to_message:
        return await message.reply_text("><b>Please reply to message!</b>")
    r = message.reply_to_message
    if message.command[0][0] == "u":
        await r.unpin()
        return await message.reply_text(
            f"><b>Unpinned [this]({r.link}) message!</b>",
            disable_web_page_preview=True,
        )
    if message.chat.type == enums.ChatType.PRIVATE:
        await r.pin(disable_notification=False, both_sides=True)
    else:
        await r.pin(
            disable_notification=False,
        )
    return await message.reply(
        f"><b>Pinned [this]({r.link}) message!</b>",
        disable_web_page_preview=True,
    )
