import os
import shutil
import traceback
import config

from core import app
from logs import LOGGER

from pyrogram import filters, types
from utils.bingtools import Bing
from utils.database import get_lang
from utils.decorators import Checklimit
from utils.functions import update_user_data
from strings import command, get_string

__MODULE__ = "Bing-AI"

__HELP__ = "BINGAI_HELPER"



@app.on_message(command("BINGAI_COMMAND") & ~config.BANNED_USERS)
@Checklimit("bingquery")
async def bingai_cmd(client, message):
    language = await get_lang(message.chat.id)
    _ = get_string(language)
    user_id = message.from_user.id if message.from_user else None
    if not user_id or message.sender_chat:
        return await message.reply_text(_["general_4"])
    prompt = client.get_text(message)
    if not prompt:
        return await message.reply(
            _["bingai_1"].format(message.text.split()[0])
        )
    pros = await message.reply(
        _["bingai_2"].format(prompt)
    )
    folder_name = f"downloads/{user_id}/"
    try:
        folder_name, imgs = await Bing.generate_images(folder_name, prompt)
        if imgs:
            media_group = []
            for img in imgs:
                if os.path.exists(img):
                    caption = _["bingai_3"].format(app.me.mention)
                    media_group.append(types.InputMediaPhoto(media=img, caption=caption))

            if media_group:
                await client.send_media_group(
                    chat_id=message.chat.id,
                    media=media_group,
                    reply_to_message_id=message.id,
                )
                await update_user_data(client, user_id, "bingquery", True)

            await pros.delete()

            if folder_name:
                shutil.rmtree(folder_name)
            for img in imgs:
                if os.path.exists(img):
                    os.remove(img)
        else:
            return await pros.edit(
                _["bingai_4"]
            )
    except Exception as e:
        error_message = str(e)
        LOGGER.error(f"Bing error: {traceback.format_exc()}")
        if "Failed to decode" in error_message:
            return await pros.edit(
                _["bingai_5"]
            )
        else:
            return await pros.edit(
                _["general_7"].format(error_message)
            )
    return