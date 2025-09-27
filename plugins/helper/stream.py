from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from info import URL, LOG_CHANNEL
# --- ZAROORI IMPORTS YAHAN ADD KIYE GAYE HAIN ---
from users_chats_db import db 
from Script import script 
# ------------------------------------------------
from urllib.parse import quote_plus
from Jisshu.util.file_properties import get_name, get_hash, get_media_file_size
from Jisshu.util.human_readable import humanbytes
import humanize
import random

@Client.on_message(filters.private & filters.command("streams"))
async def stream_start(client, message):
    user_id = message.from_user.id
    
    # --- PREMIUM CHECK LOGIC START ---
    
    # Database se check karein ki user premium hai ya nahi
    if not await db.has_premium_access(user_id):
        # Agar user premium nahi hai, toh use mana kar dein aur aage ka code rok dein
        return await message.reply_text(
            text=script.PREMIUM_REQUIRED_TXT, 
            quote=True
        )
    
    # --- PREMIUM CHECK LOGIC END ---
    
    # Agar user premium hai, toh woh yahan se aage badhega aur link generate hoga
    msg = await client.ask(message.chat.id, "**Now send me your file/video to get stream and download link**")
    
    if not msg.media:
        return await message.reply("**Please send me supported media.**")
    if msg.media in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.DOCUMENT]:
        file = getattr(msg, msg.media.value)
        filename = file.file_name
        filesize = humanize.naturalsize(file.file_size) 
        fileid = file.file_id
        username =  message.from_user.mention 

        log_msg = await client.send_cached_media(
            chat_id=LOG_CHANNEL,
            file_id=fileid,
        )
        fileName = {quote_plus(get_name(log_msg))}
        stream = f"{URL}watch/{str(log_msg.id)}?hash={get_hash(log_msg)}"
        download = f"{URL}{str(log_msg.id)}?hash={get_hash(log_msg)}"
 
        await log_msg.reply_text(
            text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Fast Download 🚀", url=download),  # we download Link
                                                InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)]])  # web stream Link
        )
        rm=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("sᴛʀᴇᴀᴍ 🖥", url=stream),
                    InlineKeyboardButton('ᴅᴏᴡɴʟᴏᴀᴅ 📥', url=download)
                ]
            ] 
        )
        msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{}</i>\n\n<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{}</i>\n\n<b>📥 Dᴏᴡɴʟᴏᴀᴅ :</b> <i>{}</i>\n\n<b> 🖥ᴡᴀᴛᴄʜ  :</b> <i>{}</i>\n\n<b>🚸 Nᴏᴛᴇ : ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ ᴛɪʟʟ ɪ ᴅᴇʟᴇᴛᴇ</b>"""

        await message.reply_text(text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(msg)), download, stream), quote=True, disable_web_page_preview=True, reply_markup=rm)
