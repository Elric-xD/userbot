import os
from YMusic import app
from YMusic.core import userbot
from YMusic.utils.ytDetails import search_api, searchYt, extract_video_id
from YMusic.utils.queue import QUEUE, add_to_queue
from YMusic.misc import SUDOERS

from pyrogram import filters

import asyncio
import random
import time

import config

PLAY_COMMAND = ["P", "PLAY"]
PREFIX = config.PREFIX
RPREFIX = config.RPREFIX

# ---------------------------------------------------------
# Helper: Local YTDL Fallback
# ---------------------------------------------------------
async def ytdl(format: str, link: str):
    stdout, stderr = await bash(f'yt-dlp --geo-bypass -g -f "{format}" {link}')
    if stdout:
        return 1, stdout
    return 0, stderr

async def bash(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    err = stderr.decode().strip()
    out = stdout.decode().strip()
    return out, err

# ---------------------------------------------------------
# Helper: Process Telegram Audio Files
# ---------------------------------------------------------
async def processReplyToMessage(message):
    msg = message.reply_to_message
    if msg.audio or msg.voice:
        m = await message.reply_text("📥 Downloading audio file...")
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

    # CASE 1: Reply to an Audio File
    if (message.reply_to_message) is not None:
        if message.reply_to_message.audio or message.reply_to_message.voice:
            input_filename, m = await processReplyToMessage(message)
            if not input_filename:
                return await message.reply_text("Invalid audio file.")
            
            await m.edit("🎸 Playing your audio reply...")
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

    # CASE 2: No Arguments
    if len(message.command) < 2:
        return await message.reply_text("Please provide a song name or YouTube link.")

    # CASE 3: Search and Play via API
    m = await message.reply_text("🔍 Searching...")
    query = message.text.split(maxsplit=1)[1]
    
    video_id = extract_video_id(query)
    is_videoId = video_id is not None
    search_query = video_id if is_videoId else query

    try:
        # Step A: Try Vercel API First (Fastest)
        title, duration, songlink = search_api(search_query, is_videoId)
        yt_link = f"https://www.youtube.com/watch?v={video_id}" if is_videoId else "Search Result"

        # Step B: Fallback to local Search if API fails
        if not songlink:
            await m.edit("🔄 API busy, trying local search...")
            title, duration, local_link = searchYt(search_query, is_videoId)
            
            if not local_link:
                return await m.edit("❌ No results found.")
            
            await m.edit("📥 Extracting audio...")
            resp, songlink = await ytdl("bestaudio", local_link)
            yt_link = local_link
            
            if resp == 0:
                return await m.edit(f"❌ yt-dlp Error: `{songlink}`")

        # Step C: Play the extracted Link
        if chat_id in QUEUE:
            queue_num = add_to_queue(chat_id, title[:19], duration, songlink, yt_link)
            await m.edit(f"# {queue_num}\n{title[:19]}\nAdded to queue!")
        else:
            Status, Text = await userbot.playAudio(chat_id, songlink)
            if not Status:
                return await m.edit(Text)
            
            add_to_queue(chat_id, title[:19], duration, songlink, yt_link)
            finish_time = time.time()
            total_time_taken = str(int(finish_time - start_time)) + "s"
            await m.edit(
                f"**🎵 Playing Song**\n\n**Name:** [{title[:19]}]({yt_link})\n**Duration:** {duration}\n**Processing:** {total_time_taken}",
                disable_web_page_preview=True,
            )

    except Exception as e:
        await m.edit(f"❌ Error: ` {str(e)[:100]} `")

# ---------------------------------------------------------
# Sudo Play Command (Broadcast/Specific Chat)
# ---------------------------------------------------------
@app.on_message((filters.command(PLAY_COMMAND, [PREFIX, RPREFIX])) & SUDOERS)
async def _raPlay(_, message):
    start_time = time.time()
    if len(message.command) < 3:
        return await message.reply_text("Usage: /play [chat_id] [song_name]")

    m = await message.reply_text("🚀 Sudo playing...")
    target_chat_id = message.text.split(" ", 2)[1]
    query = message.text.split(" ", 2)[2]

    # Use API for Sudo as well
    title, duration, songlink = search_api(query)
    
    if not songlink:
        # Fallback to local search
        title, duration, link = searchYt(query)
        resp, songlink = await ytdl("bestaudio", link)
        if resp == 0:
            return await m.edit("Extraction failed.")

    Status, Text = await userbot.playAudio(target_chat_id, songlink)
    if not Status:
        await m.edit(Text)
    else:
        finish_time = time.time()
        await m.edit(f"✅ Playing `{title[:19]}` in `{target_chat_id}`\nTime: {int(finish_time - start_time)}s")
        
