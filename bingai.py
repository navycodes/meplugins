
import os
import shutil
import traceback
import config

from core import app
from logs import LOGGER

from pyrogram import filters, types
from utils.bingtools import Bing
from utils.decorators import Checklimit
from utils.functions import update_user_data

__MODULE__ = "Bing-AI"

__HELP__ = "BINGAI_HELPER"



@app.on_message(filters.command(["bingai", "genai"]) & ~config.BANNED_USERS)
@Checklimit("bingquery")
async def bingai_cmd(client, message):
    prompt = client.get_text(message)
    if not prompt:
        return await message.reply(
            f"><b>Give the query you want to make!\n\nExample: \n<code>{message.text.split()[0]} Picture a handsome Japanese man sitting on a bench, wearing a black hoodie with 'Navy Code' emblazoned on the front and glasses, casually smoking a cigarette. The background features a lush rainforest, with soft light filtering through the foliage, creating a serene and alluring atmosphere. Add the effect of cigarette smoke wafting through the air, giving the image a mysterious feel. Image quality should be 4K high with sharp details.</code></b>"
        )
    if message.sender_chat:
        return await message.reply_text(">**Unable to use the channel account.**")
    user_id = message.from_user.id
    pros = await message.reply(
        f"<blockquote expandable><b>Proses generate <code>{prompt}</code> ..</b></blockquote>"
    )
    folder_name = f"downloads/{user_id}/"
    try:
        folder_name, imgs = await Bing.generate_images(folder_name, prompt)
        if imgs:
            media_group = []
            for img in imgs:
                if os.path.exists(img):
                    caption = "><b>Successfully generate image:</b>"
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
                "><b>Images are not found or failed generate images.</b>"
            )
    except Exception as e:
        error_message = str(e)
        LOGGER.error(f"Bing error: {traceback.format_exc()}")
        if "Failed to decode" in error_message:
            return await pros.edit(
                "><b>Failed generate image.Please repeat again...</b>"
            )
        else:
            return await pros.edit(
                f"><b>Error:</b>\n <code>{error_message}</code>"
            )
    return