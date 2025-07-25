import config
import asyncio
import traceback

from core import app, userbot
from pyrogram import filters, errors, enums
from logs import LOGGER


from utils.decorators import ONLY_GROUP, ONLY_ADMIN

__MODULE__ = "Group-Tools"
__HELP__ = """
<blockquote expandable>
<b>👥 Group Management Commands</b>

<b>★ /setgcname</b> (reply to text)  
Set the group title.

<b>★ /setgcdesc</b> (reply to text)  
Set the group description.

<b>★ /setgcpic</b> (reply to photo/video)  
Set group profile picture.

<b>★ /settitle</b> or <b>/title</b> (reply user or userID) (title)  
Set custom admin title for a user.

<b>★ /kickme</b>  
Leave the group (unless you're an admin/owner).

<b>★ /cc</b> (reply or userID)  
Clear message history of the replied user.

<b>★ /cekmember</b>  
Check total members in group.

<b>★ /cekonline</b>  
Check online members (userbot will be used).

<b>★ /cekmsg</b> (userID/username or reply)  
Check how many messages a user has sent in the group.
</blockquote>
"""


@app.on_message(filters.command(["setgcname", "setgcdesc", "setgcpic"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def group_cmd(client, message):
    command = message.command[0].lower()
    reply = message.reply_to_message
    if command == "setgcname":
        if not (reply and (reply.text or reply.caption)):
            return await message.reply(
                "><b>Example:</b> <code>/setgcname</code> (reply to text message)"
            )
        content = (reply.text or reply.caption).strip()
        await message.chat.set_title(content)
        return await message.reply(
            f"><b>Group title changed to:</b> <code>{content}</code>"
        )

    elif command == "setgcdesc":
        if not (reply and (reply.text or reply.caption)):
            return await message.reply(
                "><b>Example:</b> <code>/setgcdesc</code> (reply to text message)"
            )
        content = (reply.text or reply.caption).strip()
        await message.chat.set_description(content)
        return await message.reply(
            f"><b>Group description updated to:</b> <code>{content}</code>"
        )

    elif command == "setgcpic":
        if not (reply and (reply.photo or reply.video)):
            return await message.reply(
                "><b>Example:</b> <code>/setgcpic</code> (reply to photo or video)</b>"
            )
        media = reply.photo or reply.video
        kwargs = {"photo": media.file_id} if reply.photo else {"video": media.file_id}
        await client.set_chat_photo(message.chat.id, **kwargs)
        return await message.reply(
            f"><b>Group photo updated successfully from:</b> [media]({reply.link})",
            disable_web_page_preview=True,
        )


@app.on_message(filters.command(["settitle", "title"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def handle_title(client, message):
    reply = message.reply_to_message
    if reply and reply.sender_chat:
        return await message.reply("><b>Please reply to user.</b>")
    user_id, title = await client.extract_user_and_reason(message)
    if not all([user_id, title]):
        return await message.reply(
            "><b>Please give me title to set!</b>\n\n><b>Example:</b> <code>/title [username/reply user] [title] or reply to user with title!</code>"
        )
    try:
        user = await client.get_users(user_id)
        current_title = (
            await client.get_chat_member(message.chat.id, user.id)
        ).custom_title
        mention = await client.get_mention_from_user(user)
        if not title:
            title = f"{user.first_name} {user.last_name or ''}"
        if len(title) > 16:
            title = title[:16]
        await client.set_administrator_title(
            message.chat.id,
            user.id,
            title
        )
        return await message.reply(
            f"><b>Successfully set title user: {mention} `{current_title}` to: `{title}`</b>"
        )
    except Exception as e:
        return await message.reply(
            f"<b>ERROR:</b>\n\n<pre><code>{str(e)}</code></pre>"
        )


@app.on_message(filters.command(["kickme"]) & ~config.BANNED_USERS)
async def kickme_cmd(client, message):
    chat_id = message.chat.id
    status = None
    user_id = message.from_user.id
    mention = message.from_user.mention
    try:
        chat_id = int(chat_id)
    except ValueError:
        chat_id = str(chat_id)
    try:
        chat_member = await client.get_chat_member(chat_id, user_id)
        if chat_member.status == enums.ChatMemberStatus.ADMINISTRATOR:
            status = "admin"
        elif chat_member.status == enums.ChatMemberStatus.OWNER:
            status = "owner"
        elif chat_member.status == enums.ChatMemberStatus.MEMBER:
            status = "member"
    except Exception as er:
        return await message.reply(
            f"><b>Error:</b>\n\n<code>{str(er)}</code>"
        )
    if status in ["admin", "owner"]:
        return await message.reply(
            f"><b>Sorry you cant leave this chat because you as: {status} in this chat.</b>"
        )
    else:
        await message.chat.ban_member(user_id)
        await asyncio.sleep(0.5)
        await message.chat.unban_member(user_id)
        return await message.reply(
            f"><b>Sepertinya {mention} depresi, ingin bunuh diri.</b>"
        )


@app.on_message(filters.command(["cc"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def cc_cmd(client, message):
    reply = message.reply_to_message
    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        return  await message.reply_text("><b>Please reply to valid user_id!</b>")
    try:
        target, _ = await client.extract_user_and_reason(message)
    except (AttributeError, IndexError):
        return await message.reply("><b>Please reply to valid user_id!</b>")
    try:
        user = await client.get_users(target)
        user_id = user.id
    except (errors.PeerIdInvalid, KeyError, errors.UsernameInvalid, errors.UsernameNotOccupied):
        return await message.reply("><b>Please reply to valid user_id!</b>")
    try:
        await client.delete_user_history(message.chat.id, user_id)
        return await message.reply(
            "><b>Succesfully delete message from user.</b>"
        )
    except Exception:
        return await message.reply(
            "><b>I dont have enough permission.</b>"
        )


@app.on_message(filters.command(["cekmember"]) & ~config.BANNED_USERS)
async def cekmember_cmd(client, message):
    chat_id, _ = await client.extract_chat_and_reason(client, message)
    proses = await message.reply("><b>Please wait...</b>")
    try:
        member_count = await client.get_chat_members_count(chat_id)
        await asyncio.sleep(1)
        return await proses.edit(
            f"<b>Total members in group: {chat_id} is <code>{member_count}</code> members.</b>"
        )
    except Exception as e:
        return await proses.edit(
            f"><b>ERROR:</b>\n\n<code>{str(e)}</code>"
        )


@app.on_message(filters.command(["cekonline"]) & ~config.BANNED_USERS)
async def cekonline_cmd(client, message):
    proses = await message.reply("><b>Please wait ...</b>")
    client2 = userbot.clients[0]
    chat_id, _ = await client.extract_chat_and_reason(client, message)
    admin_ids = await client.admin_list_by_id(client, chat_id)
    if client.me.id not in admin_ids:
        return await proses.edit(
            f"><b>Failed, maybe i dont have enough permission in <code>{chat_id}</code></b>"
        )
    get = await client.get_chat_member(chat_id, client2.me.id)
    if get.status in [
        enums.ChatMemberStatus.BANNED,
        enums.ChatMemberStatus.RESTRICTED,
    ]:
        await client.unban_chat_member(chat_id, client2.me.id)
    try:
        link = await client.export_chat_invite_link(chat_id)
        await client2.join_chat(link)
    except errors.UserAlreadyParticipant:
        pass
    except Exception as err:
        LOGGER.errot(f"ERROR: {traceback.format_exc()}")
        return await proses.edit(
            f"><b>Error:</b>:\n\n<code>{str(err)}</code>"
        )

    try:
        member_online = await client2.get_chat_online_count(chat_id)
        await asyncio.sleep(1)
        return await proses.edit(
            f"><b>Total members online in group: <code>{chat_id}</code> is <code>{member_online}</code> members.</b>"
        )
    except Exception as e:
        return await proses.edit(
            f"><b>ERROR:</b>\n\n<code>{str(e)}</code>"
        )


@app.on_message(filters.command(["cekmsg"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def cekmsg_cmd(client, message):
    proses = await message.reply("><b>Please wait ...</b>")
    chat_id = None
    user_id = None
    client2 = userbot.clients[0]

    if len(message.command) > 1:
        chat_id = message.command[1] if message.command[1].isdigit() else chat_id
        user_id = message.command[2] if len(message.command) > 2 else message.command[1]
    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        chat_id = message.chat.id

    if not user_id:
        return await proses.edit("><b>Please reply to a user or provide a username/ID!</b>")
    admin_ids = await client.admin_list_by_id(client, chat_id)
    if client.me.id not in admin_ids:
        return await proses.edit(
            f"><b>Failed, maybe i dont have enough permission in <code>{chat_id}</code></b>"
        )
    get = await client.get_chat_member(chat_id, client2.me.id)
    if get.status in [
        enums.ChatMemberStatus.BANNED,
        enums.ChatMemberStatus.RESTRICTED,
    ]:
        await client.unban_chat_member(chat_id, client2.me.id)
    try:
        link = await client.export_chat_invite_link(chat_id)
        await client2.join_chat(link)
    except errors.UserAlreadyParticipant:
        pass
    except Exception as err:
        LOGGER.error(f"ERROR: {traceback.format_exc()}")
        return await proses.edit(
            f"><b>Error:</b>:\n\n<code>{str(err)}</code>"
        )

    try:
        user = await client2.get_users(user_id)
        umention = await client.get_mention_from_user(user)
    except (errors.PeerIdInvalid, KeyError):
        return await proses.edit(
            "><b>Error: PeerIdInvalid or invalid user ID/username.</b>"
        )
    try:

        total_msg = await client2.search_messages_count(chat_id, from_user=user.id)
        await asyncio.sleep(1)
        return await proses.edit(
            f"><b>Total messages by {umention} in chat <code>{chat_id}</code>: <code>{total_msg}</code> messages.</b>"
        )
    except Exception as e:
        return await proses.edit(
            f"><b>Error:</b>\n\n<code>{str(e)}</code>"
        )
