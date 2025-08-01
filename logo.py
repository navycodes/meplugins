import glob
import os
import random

import config
from config import BANNED_USERS
from core import app

from pyrogram import enums

from PIL import Image, ImageDraw, ImageFont
from pyrogram import enums
from logs import LOGGER

__MODULE__ = "Logo"
__HELP__ = """
<blockquote expandable>

📋 <b>Logo Commands</b>

• <b>/logo</b> – Start To Created A Logo For You.  
📌 <i>Use these commands in group chats to track who is present.</i>

</blockquote>
"""

@app.on_message("logo") & ~BANNED_USERS))
async def logo_cmd(client, message):
    name = client.get_arg(message)

    if not name:
        return await message.reply(
            f"><b>Gunakan Perintah dengan cara:</b>\n\n><b>Contoh:</b> <code>/logo</code> Rawwwrrr</b>"
        )

    pros = await message.reply(
        f"><b>Sedang Proses membuat logo <code>{name}</code>...</b>"
    )

    backgrounds = ""
    fonts = ""

    if message.reply_to_message:
        temp = message.reply_to_message
        if temp.media:
            if temp.document and (
                "font" in temp.document.mime_type
                or temp.document.file_name.endswith((".ttf", ".otf"))
            ):
                fonts = await temp.download()
            elif temp.photo:
                backgrounds = await temp.download()

    if not backgrounds:
        pics = []
        async for i in client.search_messages(
            "RynLogo", filter=enums.MessagesFilter.PHOTO
        ):
            if i.photo:
                pics.append(i)
        if pics:
            pictures = random.choice(pics)
            backgrounds = await pictures.download()

    if not fonts:
        font_path = glob.glob("storage/*")
        valid_fonts = [f for f in font_path if f.endswith((".ttf", ".otf"))]
        if valid_fonts:
            fonts = random.choice(valid_fonts)

    if len(name) <= 8:
        fnt_size = 170
        strke = 15
    elif len(name) <= 12:
        fnt_size = 100
        strke = 10
    else:
        fnt_size = 80
        strke = 5

    try:
        img = Image.open(backgrounds)
        draw = ImageDraw.Draw(img)
    
        if fonts and fonts.endswith((".ttf", ".otf")):
            font = ImageFont.truetype(fonts, fnt_size)
        else:
            return await pros.edit(
                f"><b>File font tidak valid atau tidak ditemukan.</b>"
            )
    
        bbox = draw.textbbox((0, 0), name, font=font, stroke_width=strke)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    
        image_width, image_height = img.size
        x = (image_width - w) / 2
        y = (image_height - h) / 2
    
        draw.text(
            (x, y),
            name,
            font=font,
            fill="white",
            stroke_width=strke,
            stroke_fill="black",
        )
    
        file_name = "logo.png"
        img.save(file_name, "PNG")
    
    except Exception as e:
        LOGGER.error(f"Error saat memproses gambar atau font: {e}")
        return await pros.edit(
            f"><b>Terjadi kesalahan pada saat memproses gambar atau font. Pastikan file gambar dan font valid.</b>"
        )

    await pros.edit(
        f"><b>Sedang Proses unggah hasil ..</b>"
    )

    if os.path.exists(file_name):
        await client.send_photo(
            chat_id=message.chat.id,
            photo=file_name,
            caption=f"><b>Created by: {client.me.mention}</b>",
        )

    for file in [file_name, backgrounds, fonts]:
        if os.path.exists(file) and (file != fonts or not fonts.startswith("assets")):
            os.remove(file)

    return await pros.delete()
