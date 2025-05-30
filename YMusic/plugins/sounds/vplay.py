import os
from YMusic import app
from YMusic.core import userbot
from YMusic.utils.ytDetails import search_api, searchYt, extract_video_id
from YMusic.utils.queue import QUEUE, add_to_queue
from YMusic.plugins.sounds.play import ytdl
from pyrogram import filters


import asyncio
import time

import config

VIDEO_PLAY = ["VP", "VPLAY"]

PREFIX = config.PREFIX

RPREFIX = config.RPREFIX


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


async def processReplyToMessage(message):
    msg = message.reply_to_message
    if msg.video or msg.video_note:
        m = await message.reply_text("Please wait... downloading your video...")
        video_original = await msg.download()
        return video_original, m
    else:
        return None


async def playWithLinks(link):
    if "&" in link:
        pass
    if "?" in link:
        pass

    return 0


@app.on_message((filters.command(VIDEO_PLAY, [PREFIX, RPREFIX])) & filters.group)
async def _vPlay(_, message):
    start_time = time.time()
    chat_id = message.chat.id
    if (message.reply_to_message) is not None:
        if message.reply_to_message.video or message.reply_to_message.video_note:
            input_filename, m = await processReplyToMessage(message)
            if input_filename is None:
                await message.reply_text(
                    "Kindly reply to a video file or give song name/yt link"
                )
                return
            await m.edit("Please wait.. Playing your video in a while")
            Status, Text = await userbot.playVideo(chat_id, input_filename)
            if Status == False:
                await m.edit(Text)
            else:
                await message.delete()
                if chat_id in QUEUE:
                    queue_num = add_to_queue(
                        chat_id,
                        message.reply_to_message.video.title[:19],
                        message.reply_to_message.video.duration,
                        message.reply_to_message.video.file_id,
                        message.reply_to_message.link,
                    )
                    await m.edit(
                        f"# {queue_num}\n{message.reply_to_message.video.title[:19]}\nYour song has been added to the queue"
                    )
                    return
                finish_time = time.time()
                total_time_taken = str(int(finish_time - start_time)) + "s"
                await m.edit(
                    f"Playing your video\n\nVideoName:- [{message.reply_to_message.video.title[:19]}]({message.reply_to_message.link})\nDuration:- {message.reply_to_message.video.duration}\nTime taken to play:- {total_time_taken}\n\n Powered by: @HitlerZone_xD",
                    disable_web_page_preview=True,
                )

    elif (len(message.command)) < 2:
        await message.reply_text("Kindly provide song name or link")
    else:
        m = await message.reply_text("Please wait finding your song")
        query = message.text.split(maxsplit=1)[1]
        video_id = extract_video_id(query)
        is_videoId = True if video_id is not None else False
        video_id = query if video_id is None else video_id
        is_alt_method = False
        try:
            title, duration, link = searchYt(video_id, is_videoId)
            if (title, duration, link) == (None, None, None):
                return await m.edit("No results found")
        except Exception as e:
            if "This request was detected as a bot" in str(e):
                await m.edit(
                    "This request was detected as a bot... Switching to alternate method"
                )
                title, duration, ytlink = search_api(video_id, is_videoId, True)
                is_alt_method = True
                link = None
                if (title, duration, ytlink) == (None, None, None):
                    return await m.edit("No results found")
                if ytlink is None:
                    return await m.edit("No results found")
            else:
                await message.reply_text(f"Error:- <code>{e}</code>")
                await m.delete()
                return

        await m.edit("Please wait downloading video of requested song")
        resp = 1
        if not is_alt_method:
            format = "best[height<=?720][width<=?1280]"
            resp, ytlink = await ytdl(format, link)
        if resp == 0:
            await m.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
        else:
            if chat_id in QUEUE:
                queue_num = add_to_queue(chat_id, title[:19], duration, ytlink, link)
                await m.edit(
                    f"# {queue_num}\n{title[:19]}\nYour song has been added to the queue"
                )
                return
            # await asyncio.sleep(2)
            Status, Text = await userbot.playVideo(chat_id, ytlink)
            # Check if the video ended
            if Status == False:
                await m.edit(Text)
            if duration is None:
                duration = "Playing From LiveStream"
            add_to_queue(chat_id, title[:19], duration, ytlink, link)
            finish_time = time.time()
            total_time_taken = str(int(finish_time - start_time)) + "s"
            await m.edit(
                f"Playing your video\n\nVideoName:- [{title[:19]}]({link})\nDuration:- {duration}\nTime taken to play:- {total_time_taken}\n\n Powered by: @HitlerZone_xD",
                disable_web_page_preview=True,
            )
