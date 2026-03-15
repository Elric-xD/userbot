import os
import time
import asyncio
from pyrogram import filters

from YMusic import app
from YMusic.core import userbot
from YMusic.utils.ytDetails import search_api, extract_video_id
from YMusic.utils.queue import QUEUE, add_to_queue
from YMusic.misc import SUDOERS
import config

# Command Configuration
PLAY_COMMAND = ["P", "PLAY"]
PREFIX = config.PREFIX
RPREFIX = config.RPREFIX

# ---------------------------------------------------------
# Helper: Process Telegram Audio Files
# ---------------------------------------------------------
async def processReplyToMessage(message):
    msg = message.reply_to_message
    if msg.audio or msg.voice:
        m = await message.reply_text("📥 Downloading audio from Telegram...")
        audio_original = await msg.download()
        return audio_original, m
    return None, None

# ---------------------------------------------------------
# Main Play Command (Group Users)
# ---------------------------------------------------------
@app.on_message((filters.command(PLAY_COMMAND, [PREFIX, RPREFIX])) & filters.group)
async def _aPlay(_, message):
    start_time = time.time()
    chat_id = message.chat.id

    # 1. Handle Replies to Telegram Audio
    if message.reply_to_message:
        if message.reply_to_message.audio or message.reply_to_message.voice:
            input_filename, m = await processReplyToMessage(message)
            if not input_filename:
                return await message.reply_text("Failed to process audio reply.")
            
            await m.edit("🎸 Playing audio...")
            Status, Text = await userbot.playAudio(chat_id, input_filename)
            
            if not Status:
                return await m.edit(Text)

            title = (message.reply_to_message.audio.title or "Telegram Audio")[:19]
            duration = message.reply_to_message.audio.duration or 0
            
            if chat_id in QUEUE:
                queue_num = add_to_queue(chat_id, title, duration, input_filename, message.reply_to_message.link)
                await m.edit(f"# {queue_num}\n{title}\nAdded to queue!")
            else:
                add_to_queue(chat_id, title, duration, input_filename, message.reply_to_message.link)
                finish_time = time.time()
                await m.edit(f"✅ Playing Audio\nTime taken: {int(finish_time - start_time)}s")
            return

    # 2. Check for Search Query
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/play [song name or link]`")

    # 3. Search and Play via Vercel API ONLY
    m = await message.reply_text("🔍 Searching via API...")
    query = message.text.split(maxsplit=1)[1]
    
    video_id = extract_video_id(query)
    is_videoId = video_id is not None
    search_query = video_id if is_videoId else query

    try:
        # Get data from your Vercel API
        title, duration, songlink = search_api(search_query, is_videoId)
        yt_link = f"https://www.youtube.com/watch?v={video_id}" if is_videoId else "Search Result"

        if not songlink:
            return await m.edit("❌ API Error: Could not find or extract this song.")

        # Handle Queue or Instant Play
        if chat_id in QUEUE:
            queue_num = add_to_queue(chat_id, title[:19], duration, songlink, yt_link)
            await m.edit(f"# {queue_num}\n{title[:19]}\nAdded to queue!")
        else:
            Status, Text = await userbot.playAudio(chat_id, songlink)
            if not Status:
                return await m.edit(Text)
            
            # Record in Queue system
            add_to_queue(chat_id, title[:19], duration, songlink, yt_link)
            
            finish_time = time.time()
            total_time_taken = str(int(finish_time - start_time)) + "s"
            await m.edit(
                f"**🎵 Playing Song**\n\n**Name:** [{title[:19]}]({yt_link})\n**Duration:** {duration}\n**Processing:** {total_time_taken}",
                disable_web_page_preview=True,
            )

    except Exception as e:
        await m.edit(f"❌ API Down or Error: `{str(e)[:100]}`")

# ---------------------------------------------------------
# Sudo Play Command
# ---------------------------------------------------------
@app.on_message((filters.command(PLAY_COMMAND, [PREFIX, RPREFIX])) & SUDOERS)
async def _raPlay(_, message):
    start_time = time.time()
    if len(message.command) < 3:
        return await message.reply_text("Usage: `/play [chat_id] [song name]`")

    m = await message.reply_text("🚀 Sudo playing via API...")
    target_chat_id = message.text.split(" ", 2)[1]
    query = message.text.split(" ", 2)[2]

    title, duration, songlink = search_api(query)
    
    if not songlink:
        return await m.edit("❌ API could not extract this query.")

    Status, Text = await userbot.playAudio(target_chat_id, songlink)
    if not Status:
        await m.edit(Text)
    else:
        finish_time = time.time()
        await m.edit(f"✅ Playing `{title[:19]}` in `{target_chat_id}`\nTime: {int(finish_time - start_time)}s")
            
