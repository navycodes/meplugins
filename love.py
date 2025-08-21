import config
import random
from core import app

from pyrogram import filters


__MODULE__ = "Love-Tools"
__HELP__ = """
<blockquote><code>★ /love</code> <b>[Provide Username Or Name, Minimum Two Names.]</b>
    <b>Example:</b> • `/love [name1] [name2]`: Calculates The Percentage Of Love Between Two People,</blockquote>
"""

def get_random_message(love_percentage):
    if love_percentage <= 30:
        return random.choice(
            [
                "Love is in the air but needs a little spark.",
                "A good start but there's room to grow.",
                "It's just the beginning of something beautiful.",
            ]
        )
    elif love_percentage <= 70:
        return random.choice(
            [
                "A strong connection is there. Keep nurturing it.",
                "You've got a good chance. Work on it.",
                "Love is blossoming, keep going.",
            ]
        )
    else:
        return random.choice(
            [
                "Wow! It's a match made in heaven!",
                "Perfect match! Cherish this bond.",
                "Destined to be together. Congratulations!",
            ]
        )


@app.on_message(filters.command("truth") & ~config.BANNED_USERS)
async def love_cmd(client, message):
    cmd, *args = message.text.split(" ")
    user = message.from_user 
    user_first_name = user.first_name
    love_percentage = random.randint(10, 100)
    love_message = get_random_message(love_percentage)
    text = random.choice(love_percentage)
    return await message.reply(
        f"<blockquote expandable>{user} + {user} = {text}%\n\n{love_message}</blockquote>",
        app.send_message(message.chat.id, text)
    )
