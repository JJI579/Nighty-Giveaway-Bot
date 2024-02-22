from nextcord.ext import commands
import nextcord as discord

from sys import platform
import os
if 'win32' in platform: cwd = os.getcwd()
else: cwd = ''
import json

from playwright.async_api import async_playwright

data = json.load(open(f'{cwd}/config.json'))


guilds = data['Guilds']

bot = commands.Bot(command_prefix=data['Prefix'], help_command=None, intents=discord.Intents.all())

def AICHAT():

    @bot.listen('on_ready')
    async def AICHAT_READY():
        print(f"STARTING AI CHAT")
        bot.playwright = await async_playwright().start()
        bot.browser = await bot.playwright.chromium.launch(headless=True)
        bot.page = await bot.browser.new_page()
        bot.divIndex = 0

        await bot.page.goto("https://deepai.org/chat")
        await bot.page.frame_locator("iframe[title=\"SP Consent Message\"]").get_by_label("Accept").click()
        await bot.page.locator("[id=\"deepai\\.org_header\"]").click()
        
    @bot.slash_command(name='ask', guild_ids=guilds, description='ask ai anything')
    async def askCMD(interaction: discord.Interaction, request):
        await interaction.response.defer()

        await bot.page.locator(f"#chatboxWrapperId_{bot.divIndex}").get_by_placeholder("Chat with AI...").fill(request)
        await bot.page.get_by_role("button", name="Go").click()
        async with bot.page.expect_response(lambda response: "hacking_is_a_serious_crime" in response.url and response.status == 200) as response_info:
            response_info = await response_info.value
            await interaction.send((await response_info.body()).decode())
            bot.divIndex+=1

AICHAT()

bot.run(data['Token'])