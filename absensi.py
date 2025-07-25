import config
import pytz
import traceback

from pyrogram.helpers import ikb
from pyrogram import filters
from datetime import datetime

from utils.decorators import ONLY_GROUP, ONLY_ADMIN
from utils.database import dB
from core import app


__MODULE__ = "Absensi"
__HELP__ = """
<blockquote expandable>

📋 <b>Attendance Commands</b>

• <b>/mulai</b> – Start attendance session.  
• <b>/selesai</b> – End the current attendance session.  
• <b>/refresh</b> – Refresh the attendance message if it's buried.

📌 <i>Use these commands in group chats to track who is present.</i>

</blockquote>
"""


def format_absen_list(data):
    if not data:
        return "Belum ada yang absen."
    return "\n".join([
        f"{i+1}. {u['name']}  ({u['time']})." for i, u in enumerate(data)
    ])


def format_tanggal_indo(dt: datetime) -> str:
    hari = {
        "Monday": "Senin",
        "Tuesday": "Selasa",
        "Wednesday": "Rabu",
        "Thursday": "Kamis",
        "Friday": "Jumat",
        "Saturday": "Sabtu",
        "Sunday": "Minggu",
    }
    bulan = {
        "January": "Januari",
        "February": "Februari",
        "March": "Maret",
        "April": "April",
        "May": "Mei",
        "June": "Juni",
        "July": "Juli",
        "August": "Agustus",
        "September": "September",
        "October": "Oktober",
        "November": "November",
        "December": "Desember",
    }

    nama_hari = hari[dt.strftime("%A")]
    nama_bulan = bulan[dt.strftime("%B")]
    return f"{nama_hari}, tanggal {dt.day} {nama_bulan} {dt.year}"


@app.on_message(filters.command("mulai") & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def mulai_absen(_, message):
    now = datetime.now(pytz.timezone("Asia/Jakarta"))
    date_str = format_tanggal_indo(now)
    
    chat_id = message.chat.id
    data = await dB.get_var(chat_id, "ABSENSI") or []

    absen_text = f"""{message.chat.title}
Daftar hadir hari {date_str}.

<blockquote expandable>
{format_absen_list(data)}
</blockquote>

Waktu dalam timezone WIB (UTC+7).
Yang telah hadir, silakan klik tombol HADIR di bawah ini."""
    
    keyboard = ikb([[("☑️  Hadir", "Hadir")]])
    return await message.reply(absen_text, reply_markup=keyboard)


@app.on_message(filters.command("refresh") & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def refresh_absen(_, message):
    now = datetime.now(pytz.timezone("Asia/Jakarta"))
    date_str = format_tanggal_indo(now)
    chat_id = message.chat.id
    data = await dB.get_var(chat_id, "ABSENSI") or []
    data = sorted(data, key=lambda x: x["time"])

    absen_text = f"""{message.chat.title}
Daftar hadir hari {date_str}.

<blockquote expandable>
{format_absen_list(data)}
</blockquote>

Waktu dalam timezone WIB (UTC+7).
Yang telah hadir, silakan klik tombol HADIR di bawah ini."""
    
    keyboard = ikb([[("☑️  Hadir", "Hadir")]])
    return await message.reply(absen_text, reply_markup=keyboard)


@app.on_message(filters.command("selesai") & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def selesai_absen(_, message):
    now = datetime.now(pytz.timezone("Asia/Jakarta"))
    date_str = format_tanggal_indo(now)
    chat_id = message.chat.id
    data = await dB.get_var(chat_id, "ABSENSI") or []
    data = sorted(data, key=lambda x: x["time"])
    absen_text = f"""{message.chat.title}
Daftar hadir hari {date_str}.

<blockquote expandable>
{format_absen_list(data)}
</blockquote>

Waktu dalam timezone WIB (UTC+7)."""
    return await message.reply(absen_text)


@app.on_callback_query(filters.regex(r"^Hadir"))
async def hadir_callback(client, callback_query):
    user = callback_query.from_user
    user_id = user.id
    name = user.first_name if not user.last_name else f"{user.first_name} {user.last_name}"
    chat_id = callback_query.message.chat.id

    data = await dB.get_var(chat_id, "ABSENSI") or []

    existing = next((u for u in data if u["user_id"] == user_id), None)
    if existing:
        data = [u for u in data if u["user_id"] != user_id]
    else:
        now_time = datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%H:%M")
        data.append({"user_id": user_id, "name": name, "time": now_time})

    data = sorted(data, key=lambda x: x["time"])
    await dB.set_var(chat_id, "ABSENSI", data)

    try:
        now = datetime.now(pytz.timezone("Asia/Jakarta"))
        date_str = format_tanggal_indo(now)
        text = f"""{callback_query.message.chat.title}
Daftar hadir hari {date_str}.

<blockquote expandable>
{format_absen_list(data)}
</blockquote>

Waktu dalam timezone WIB (UTC+7).
Yang telah hadir, silakan klik tombol HADIR di bawah ini."""
        
        keyboard = ikb([[("☑️  Hadir", "Hadir")]])
        if chat_id not in await dB.get_list_from_var(client.me.id, "ABSENSI_CHAT"):
            await dB.add_to_var(client.me.id, "ABSENSI_CHAT", chat_id)
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception:
        print(f"ERROR: {traceback.format_exc()}")
