from pyrogram import Client, filters
import datetime
import time
from database.users_chats_db import db
from info import ADMINS
from utils import users_broadcast, groups_broadcast, temp, get_readable_time
import asyncio
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup 

# 🛠️ सुधार 1: एक लॉक की जगह दो अलग-अलग लॉक बनाए गए हैं
users_lock = asyncio.Lock()
groups_lock = asyncio.Lock()

@Client.on_callback_query(filters.regex(r'^broadcast_cancel'))
async def broadcast_cancel(bot, query):
    _, ident = query.data.split("#")
    if ident == 'users':
        await query.message.edit("ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ᴜsᴇʀs ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...")
        temp.USERS_CANCEL = True
    elif ident == 'groups':
        temp.GROUPS_CANCEL = True
        await query.message.edit("ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ɢʀᴏᴜᴘs ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...")
       
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_users(bot, message):
    # 🛠️ सुधार 2: users_lock का उपयोग करके चेक किया जा रहा है
    if users_lock.locked(): 
        return await message.reply('Currently users broadcast processing. Wait for completion.')

    p = await message.reply('<b>Do you want pin this message in users?</b>', reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True))
    msg = await bot.listen(chat_id=message.chat.id, user_id=message.from_user.id)
    if msg.text == 'Yes':
        is_pin = True
    elif msg.text == 'No':
        is_pin = False
    else:
        await p.delete()
        return await message.reply_text('Wrong Response!')
    await p.delete()
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    b_sts = await message.reply_text(text='<b>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ʏᴏᴜʀ ᴍᴇssᴀɢᴇs ᴛᴏ ᴜsᴇʀs ⌛️</b>')
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0
    success = 0

    # 🛠️ सुधार 3: users_lock का उपयोग करके ब्रॉडकास्ट शुरू किया जा रहा है
    async with users_lock:
        async for user in users:
            time_taken = get_readable_time(time.time()-start_time)
            if temp.USERS_CANCEL:
                temp.USERS_CANCEL = False
                await b_sts.edit(f"Users broadcast Cancelled!\nCompleted in {time_taken}\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done} / {total_users}</code>\nSuccess: <code>{success}</code>")
                return
            
            # यहाँ 'sts' में 'Blocked'/'Deleted' स्टेटस को भी ट्रैक करने के लिए 
            # आपको 'users_broadcast' फंक्शन को अपडेट करना होगा, 
            # लेकिन अभी के लिए यह 'Success' या 'Error' ही मानेगा।
            sts = await users_broadcast(int(user['id']), b_msg, is_pin)
            
            if sts == 'Success':
                success += 1
            elif sts == 'Error':
                failed += 1
            done += 1
            if not done % 20:
                btn = [[
                    InlineKeyboardButton('CANCEL', callback_data=f'broadcast_cancel#users')
                ]]
                await b_sts.edit(f"Users broadcast in progress...\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done} / {total_users}</code>\nSuccess: <code>{success}</code>", reply_markup=InlineKeyboardMarkup(btn))
                
        # ⚠️ नोट: blocked और deleted काउंट्स को दिखाने के लिए आपको 
        # users_broadcast फंक्शन को अपडेट करना होगा।
        await b_sts.edit(f"Users broadcast completed.\nCompleted in {time_taken}\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done} / {total_users}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>")

@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_group(bot, message):
    # 🛠️ सुधार 4: groups_lock का उपयोग करके चेक किया जा रहा है
    if groups_lock.locked():
        return await message.reply('Currently groups broadcast processing. Wait for completion.')
        
    p = await message.reply('<b>Do you want pin this message in groups?</b>', reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True))
    msg = await bot.listen(chat_id=message.chat.id, user_id=message.from_user.id)
    if msg.text == 'Yes':
        is_pin = True
    elif msg.text == 'No':
        is_pin = False
    else:
        await p.delete()
        return await message.reply_text('Wrong Response!')
    await p.delete()
    chats = await db.get_all_chats()
    b_msg = message.reply_to_message
    b_sts = await message.reply_text(text='<b>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ʏᴏᴜʀ ᴍᴇssᴀɢᴇs ᴛᴏ ɢʀᴏᴜᴘs ⏳</b>')
    start_time = time.time()
    total_chats = await db.total_chat_count()
    done = 0
    failed = 0
    success = 0
    
    # 🛠️ सुधार 5: groups_lock का उपयोग करके ब्रॉडकास्ट शुरू किया जा रहा है
    async with groups_lock:
        async for chat in chats:
            time_taken = get_readable_time(time.time()-start_time)
            if temp.GROUPS_CANCEL:
                temp.GROUPS_CANCEL = False
                await b_sts.edit(f"Groups broadcast Cancelled!\nCompleted in {time_taken}\n\nTotal Groups: <code>{total_chats}</code>\nCompleted: <code>{done} / {total_chats}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>")
                return
            sts = await groups_broadcast(int(chat['id']), b_msg, is_pin)
            if sts == 'Success':
                success += 1
            elif sts == 'Error':
                failed += 1
            done += 1
            if not done % 20:
                btn = [[
                    InlineKeyboardButton('CANCEL', callback_data=f'broadcast_cancel#groups')
                ]]
                await b_sts.edit(f"Groups groadcast in progress...\n\nTotal Groups: <code>{total_chats}</code>\nCompleted: <code>{done} / {total_chats}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>", reply_markup=InlineKeyboardMarkup(btn))    
        await b_sts.edit(f"Groups broadcast completed.\nCompleted in {time_taken}\n\nTotal Groups: <code>{total_chats}</code>\nCompleted: <code>{done} / {total_chats}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>")
