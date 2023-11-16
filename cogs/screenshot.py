import discord
from discord.ext import commands, tasks
from discord import app_commands

import os
from dotenv import load_dotenv

from twitchAPI.twitch import Twitch
from twitchAPI.helper import first

import requests

import cv2
import numpy as np
import time

import io


class Screenshot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.twitch = None

        self.crop_x = None
        self.crop_y = None

        self.cap = None

        self.last_pixel_count = 0
        self.recent_screenshots_array = None

        self.streamer = 'vedal987'
        self.streaming = False

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog {os.path.basename(__file__)[:-3]} loaded.")

        load_dotenv()
        self.twitch = await Twitch(os.getenv("APP_ID"), os.getenv("APP_SECRET"))
        await self.capture_stream.start()

    def count_pixels(self, image) -> int:
        if self.crop_x:
            cropped = image[self.crop_y:1080, self.crop_x:1920]
        else:
            cropped = image[self.crop_y:1080]

        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        treshhold = cv2.threshold(gray, 248, 255, cv2.THRESH_BINARY)[1]
        pixels = np.sum(treshhold == 255)
        return pixels

    async def find_stream_type(self) -> None:
        stream = await first(self.twitch.get_streams(user_login=self.streamer))
        if "dev" or "developer" or "ved" in stream.title:
            pass
        if "collab" in stream.title:
            self.crop_x = round(1080 / 1.8)
            self.crop_y = round(1080 / 2.2)
        if stream.game_name != "Just Chatting":
            pass
        if "@" in stream.title:
            self.crop_x = round(1080 / 1.7)
            self.crop_y = round(1080 / 2.2)
        else:
            self.crop_x = None
            self.crop_y = round(1080 / 1.8)

    async def start_capture(self) -> None:
        r = requests.get(f'https://pwn.sh/tools/streamapi.py?url=https://twitch.tv/{self.streamer}')
        url = (next(reversed(r.json()['urls'].values())))

        self.last_pixel_count = 0
        self.recent_screenshots_array = None

        self.cap = cv2.VideoCapture(url)
        await self.find_stream_type()

    @tasks.loop()
    async def capture_stream(self):
        if self.streaming:

            if not self.cap:
                await self.start_capture()
            if self.cap is None:
                self.streaming = False

            if not self.recent_screenshots_array:
                self.recent_screenshots_array = [self.cap.read()[1]]

            n_white_pix = self.count_pixels(self.cap.read()[1])
            diff = abs(self.last_pixel_count - n_white_pix)

            if n_white_pix - diff < 0:
                for scr in self.recent_screenshots_array:
                    if self.last_pixel_count - 1000 <= self.count_pixels(scr) <= self.last_pixel_count + 1000:

                        guild = self.client.get_guild(1168220243299151912)
                        channel = guild.get_channel(1168228460439797985)
                        thread = channel.get_thread(1174802406358384681)

                        buffer = cv2.imencode(".png", scr)[1]
                        io_buf = io.BytesIO(buffer)

                        file = discord.File(io_buf, 'result.png')
                        await thread.send(f'Timestamp: <t:{round(time.time())}:F>', file=file)

                        self.recent_screenshots_array = []
                        break
            self.last_pixel_count = n_white_pix
            self.recent_screenshots_array.insert(0, self.cap.read()[1])

        elif not self.streaming:
            if self.capture_stream.seconds is None:
                self.capture_stream.change_interval(seconds=1)

            content = requests.get('https://www.twitch.tv/' + self.streamer).content.decode('utf-8')
            if 'isLiveBroadcast' in content:
                self.capture_stream.change_interval(seconds=0)
                self.streaming = True


async def setup(client):
    await client.add_cog(Screenshot(client))
