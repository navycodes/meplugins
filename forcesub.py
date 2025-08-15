import asyncio
import config
import traceback

from core import app
from utils.database import dB
from utils.misc import SUDOERS
from utils.decorators import ONLY_GROUP, ONLY_ADMIN

from pyrogram import filters, errors, enums, types
from pyrogram.helpers import ikb




@app.on_callback_query(filters.regex("^RequestUnMute") & ~config.BANNED_USERS)
async def callback_unmute(client, callback):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    force_subs = await dB.get_var(chat_id, "IS_FORCESUB")

    if force_subs:
        chat_member = await client.get_chat_member(chat_id, user_id)

        if chat_member.restricted_by:
            if chat_member.restricted_by.id == client.me.id:
                try:
                    await client.get_chat_member(force_subs, user_id)
                    await client.unban_chat_member(chat_id, user_id)
                    await callback.message.delete()
                    if callback.message.reply_to_message.from_user.id == user_id:
                        await callback.message.delete()
                except errors.UserNotParticipant:
                    await callback.answer(f"Bergabunglah dengan kami {force_subs}\n\nLalu tekan tombol : Suarakan Saya.", True)
            else:
                await callback.answer("Anda telah dibisukan oleh admin karena alasan lain.", True)
        else:
            me_status = (await client.get_chat_member(chat_id, client.me.id)).status
            if me_status != enums.ChatMemberStatus.ADMINISTRATOR:
                await client.send_message(chat_id, ">**Saya bukan admin disini..\nBeri saya izin larangan dan coba lagi.**")
            else:
                await callback.answer("Peringatan! Jangan tekan tombol saat Anda bisa berbicara.", True)


@app.on_message(filters.incoming & ~filters.private, group=-2)
async def check_member(client, message):
    chat_id = message.chat.id
    force_subs = await dB.get_var(chat_id, "IS_FORCESUB")
    
    if force_subs:
        user_id = message.from_user.id
        try:
            user_status = (await client.get_chat_member(chat_id, user_id)).status
        except errors.ChatAdminRequired:
            await dB.remove_var(chat_id, "IS_FORCESUB")
            return await client.send_message(chat_id, f">**Saya bukan admin `{force_subs}` channel.\nJadikan saya admin disaluran itu.**")
        if user_status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and user_id not in SUDOERS:
            try:
                await app.get_chat_member(force_subs, user_id)
            except errors.UserNotParticipant:
                try:
                    fsub_chat = await client.get_chat(int(force_subs) if force_subs.startswith("-100") else force_subs)
                    fsub_title = fsub_chat.title or "Saluran Kami"
                    if fsub_chat.username:
                        invite_url = f"https://t.me/{fsub_chat.username}"
                    else:
                        invite_link = await client.create_chat_invite_link(fsub_chat.id)
                        invite_url = invite_link.invite_link

                    sent_message = await message.reply_text(
f"""👋 Selamat Datang {message.from_user.mention}

Anda belum bergabung dengan channel kami **{fsub_title}**.

Silahkan bergabung [disini]({invite_url}) dan tekan tombol **🙏🏻 Suarakan Saya**.""",
                        disable_web_page_preview=True,
                        reply_markup=ikb([
                            [("❤️ Join Channel", invite_url, "url")],
                            [("🙏🏻 Suarakan Saya", "RequestUnMute")]
                        ])
                    )
                    return await client.restrict_chat_member(chat_id, user_id, types.ChatPermissions())
                except errors.ChatAdminRequired: 
                    return await sent_message.edit(">**Saya bukan admin disini..\nBeri saya izin larangan dan coba lagi.**")
            except errors.ChatAdminRequired:
                return await client.send_message(chat_id, f">**Saya bukan admin `{force_subs}` channel.\nJadikan saya admin disaluran itu.**")


@app.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def forsub_cmd(client, message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply(">**Gunakan format /fsub @username untuk mengaktifkan wajib join ke saluran yang dituju, atau /fsub off untuk mematikan wajib join paksa.**")
    input_str = message.command[1]
    is_on = await dB.get_var(chat_id, "IS_FORCESUB")
    if input_str.lower() == "off":
         if not is_on:
             return await message.reply(">**Wajib paksa join memang belum diatur.**")
         await dB.remove_var(chat_id, "IS_FORCESUB")
         return await message.reply(f">**Wajib join paksa ke `{is_on}` berhasil dihapus dan dimatikan.**")
    elif input_str.lower() == "clear":
        sent_message = await message.reply_text(">**Tunggu sebentar sedang membunyikan pengguna yang bisu...**")
        count = 0
        try:
            async for chat_member in client.get_chat_members(
                chat_id, filter=enums.ChatMembersFilter.RESTRICTED
            ):
                if chat_member.restricted_by.id == client.me.id:
                    try:
                        await client.unban_chat_member(chat_id, chat_member.user.id)
                        count += 1
                        await asyncio.sleep(1)
                    except errors.FloodWait as e:
                        await asyncio.sleep(e.value)
                        await client.unban_chat_member(chat_id, chat_member.user.id)
                        count += 1
            return await sent_message.edit(f">**Berhasil membunyikan pengguna yang bisu, total `{count}` pengguna bisu.**")
        except errors.ChatAdminRequired:
            return await sent_message.edit(">Saya bukan admin di chat ini.\nSaya tidak dapat mengaktifkan suara anggota karena saya bukan admin dalam obrolan ini, jadikan saya admin dan berikan izin ban pengguna.")
    else:
        try:
            if input_str.startswith("-100"):
                fsub_chat_id = int(input_str)
                chat_info = await client.get_chat(fsub_chat_id)
            else:
                fsub_chat_id = input_str
                chat_info = await client.get_chat(fsub_chat_id)

            await client.get_chat_member(chat_info.id, "me")
            await dB.set_var(chat_id, "IS_FORCESUB", str(chat_info.id))
            title = chat_info.title or "Chat"
            return await message.reply_text(
                f">**Paksa Berlangganan Diaktifkan.**\n\n"
                f"Semua anggota harus join ke **{title}** agar bisa mengirim pesan di grup ini.",
                disable_web_page_preview=True
            )

        except errors.UserNotParticipant:
            return await message.reply_text(f">**Saya bukan admin di `{chat_info.id}`. Tambahkan saya sebagai admin untuk mengaktifkan Forcesubs.**")
        except (errors.UsernameNotOccupied, errors.PeerIdInvalid):
            return await message.reply_text(">**Nama Pengguna Saluran Tidak Valid.**")
        except Exception as err:
            print(f"ERROR: {traceback.format_exc()}")
            return await message.reply_text(f"**ERROR:** {str(err)}")
        

__MODULE__ = "Force-Subs"
__HELP__ = """
<blockquote expandable>
<b>🔗 Force Subscription</b>

<b>★ /fsub</b> @channel_username or <code>-100xxxxxxxxxx</code>  
Enable forced subscription to a specific channel.

<b>★ /fsub off</b>  
Disable forced subscription.

<b>★ /fsub clear</b>  
Unmute all users previously muted for not joining the required channel.
</blockquote>
"""
