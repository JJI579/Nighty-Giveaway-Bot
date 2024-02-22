from discord import Interaction
from nextcord.ext import commands
import nextcord as discord

from sys import platform
import os
if 'win32' in platform: cwd = os.getcwd()
else: cwd = '/home/opc/nighty_giveaways'

import random
import sqlite3
import datetime
import re
from dateutil import parser
import asyncio
import json

data = json.load(open(f'{cwd}/config.json'))


guilds = data['Guilds']
bot = commands.Bot(command_prefix=data['Prefix'], help_command=None, intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"{bot.user} is ready")


def ISO(seconds: float = 0):
    if seconds == 0:
        return datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    return (datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=seconds)).isoformat()

def UTC():
    return round(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())

class Database:

    def __init__(self) -> None:
        self.database = sqlite3.connect(f'{cwd}/information.db')
        self.cursor = self.database.cursor()
        self.initialiseTables()
        self.database.commit()
    
    def initialiseTables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tblGiveaway (giveawayID INTEGER PRIMARY KEY AUTOINCREMENT, hostID, winners, createdAt, endsAt, title, description, isActive INTEGER DEFAULT 1, messageID INTEGER NOT NULL, channelID INTEGER DEFAULT 0)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tblEntrants (giveawayID, entrantID, joinedAt)")
    
    def format_dict(self, values, table):
        if values == None:
            return values
        elif len(values) == 0:
            return None
        
        quer = self.cursor.execute(f"SELECT * from {table} LIMIT 1")
        headers = [x[0] for x in quer.description]
        return {headers[i]:values[i] or None for i, _ in enumerate(headers)}

    def create_giveaway(self, interaction: discord.Interaction, winners: int, duration: int, title, description, messageID: int=0):
        self.cursor.execute("INSERT INTO tblGiveaway(hostID, winners, createdAt, endsAt, title, description, messageID) VALUES (?,?,?,?,?,?,?)", [interaction.user.id, winners, ISO(), ISO(duration), title, description, messageID])
        self.database.commit()
        return self.format_dict(self.cursor.execute("SELECT * FROM tblGiveaway").fetchall()[-1], "tblGiveaway")

    def update_giveaway(self, giveawayID, messageID: int, channelID: int):
        print(giveawayID, messageID, channelID)
        self.cursor.execute("UPDATE tblGiveaway SET messageID=?, channelID=? WHERE giveawayID=?", [messageID, channelID, giveawayID])
        self.database.commit()

    def fetch_giveaways(self, filtered=False): # filter by active
        resp = self.cursor.execute("SELECT * FROM tblGiveaway") if not filtered else self.cursor.execute("SELECT * FROM tblGiveaway WHERE isActive=1")
        return [self.format_dict(x, "tblGiveaway") for x in resp.fetchall()]

    def fetch_giveaway(self, ID: int):
        resp = self.cursor.execute("SELECT * FROM tblGiveaway WHERE giveawayID=?", [ID]).fetchone()
        return self.format_dict(resp, "tblGiveaway")

    def fetch_entrants(self, giveawayID: int):
        return [self.format_dict(x, "tblEntrants") for x in self.cursor.execute("SELECT * FROM tblEntrants WHERE giveawayID=?", [giveawayID]).fetchall()]

    def fetch_entrant(self, giveawayID: int, userID: int):
        return self.format_dict(self.cursor.execute("SELECT * FROM tblEntrants WHERE giveawayID=? AND entrantID=?", [giveawayID, userID]).fetchone(), "tblEntrants")

    def create_entrant(self, giveawayID: int, interaction: discord.Interaction):
        entrant = self.fetch_entrant(giveawayID, interaction.user.id)
        if entrant:
            return entrant
        self.cursor.execute("INSERT INTO tblEntrants VALUES (?,?,?)", [giveawayID, interaction.user.id, ISO()])
        self.database.commit()
        return self.fetch_entrant(giveawayID, interaction.user.id)

class GiveawayModal(discord.ui.Modal):

    def __init__(self, giveaway) -> None:
        self.giveaway = giveaway
        self.options = [ [ "140 + 61 = ?", 201 ], [ "130 + 22 = ?", 152 ], [ "101 + 39 = ?", 140 ], [ "69 + 42 = ?", 111 ], [ "70 + 150 = ?", 220 ], [ "104 + 53 = ?", 157 ], [ "127 + 102 = ?", 229 ], [ "41 + 116 = ?", 157 ], [ "140 + 125 = ?", 265 ], [ "85 + 188 = ?", 273 ], [ "57 + 55 = ?", 112 ], [ "30 + 34 = ?", 64 ], [ "92 + 190 = ?", 282 ], [ "77 + 117 = ?", 194 ], [ "39 + 79 = ?", 118 ], [ "81 + 50 = ?", 131 ], [ "160 + 178 = ?", 338 ], [ "182 + 85 = ?", 267 ], [ "154 + 197 = ?", 351 ], [ "193 + 164 = ?", 357 ], [ "65 + 184 = ?", 249 ], [ "135 + 97 = ?", 232 ], [ "81 + 153 = ?", 234 ], [ "166 + 96 = ?", 262 ], [ "105 + 93 = ?", 198 ], [ "42 + 175 = ?", 217 ], [ "175 + 88 = ?", 263 ], [ "151 + 158 = ?", 309 ], [ "185 + 141 = ?", 326 ], [ "33 + 163 = ?", 196 ], [ "70 + 39 = ?", 109 ], [ "182 + 190 = ?", 372 ], [ "92 + 183 = ?", 275 ], [ "141 + 192 = ?", 333 ], [ "183 + 107 = ?", 290 ], [ "146 + 71 = ?", 217 ], [ "20 + 103 = ?", 123 ], [ "71 + 61 = ?", 132 ], [ "91 + 144 = ?", 235 ], [ "163 + 130 = ?", 293 ], [ "122 + 198 = ?", 320 ], [ "174 + 181 = ?", 355 ], [ "160 + 163 = ?", 323 ], [ "107 + 162 = ?", 269 ], [ "25 + 176 = ?", 201 ], [ "151 + 162 = ?", 313 ], [ "196 + 168 = ?", 364 ], [ "195 + 59 = ?", 254 ], [ "92 + 102 = ?", 194 ], [ "94 + 77 = ?", 171 ], [ "97 + 177 = ?", 274 ], [ "199 + 50 = ?", 249 ], [ "109 + 63 = ?", 172 ], [ "83 + 63 = ?", 146 ], [ "89 + 159 = ?", 248 ], [ "177 + 161 = ?", 338 ], [ "196 + 169 = ?", 365 ], [ "135 + 124 = ?", 259 ], [ "58 + 169 = ?", 227 ], [ "30 + 171 = ?", 201 ], [ "99 + 140 = ?", 239 ], [ "74 + 141 = ?", 215 ], [ "171 + 103 = ?", 274 ], [ "60 + 159 = ?", 219 ], [ "79 + 111 = ?", 190 ], [ "106 + 88 = ?", 194 ], [ "44 + 194 = ?", 238 ], [ "97 + 88 = ?", 185 ], [ "87 + 162 = ?", 249 ], [ "158 + 186 = ?", 344 ], [ "103 + 78 = ?", 181 ], [ "86 + 77 = ?", 163 ], [ "129 + 162 = ?", 291 ], [ "178 + 145 = ?", 323 ], [ "96 + 150 = ?", 246 ], [ "129 + 149 = ?", 278 ], [ "81 + 68 = ?", 149 ], [ "91 + 109 = ?", 200 ], [ "116 + 176 = ?", 292 ], [ "49 + 153 = ?", 202 ], [ "168 + 85 = ?", 253 ], [ "186 + 127 = ?", 313 ], [ "111 + 35 = ?", 146 ], [ "88 + 180 = ?", 268 ], [ "184 + 167 = ?", 351 ], [ "184 + 102 = ?", 286 ], [ "160 + 137 = ?", 297 ], [ "172 + 63 = ?", 235 ], [ "126 + 31 = ?", 157 ], [ "113 + 193 = ?", 306 ], [ "160 + 155 = ?", 315 ], [ "66 + 23 = ?", 89 ], [ "197 + 170 = ?", 367 ], [ "53 + 78 = ?", 131 ], [ "139 + 55 = ?", 194 ], [ "153 + 35 = ?", 188 ], [ "178 + 153 = ?", 331 ], [ "28 + 191 = ?", 219 ], [ "94 + 187 = ?", 281 ], [ "83 + 159 = ?", 242 ], [ "47 + 119 = ?", 166 ], [ "136 + 60 = ?", 196 ], [ "134 + 88 = ?", 222 ], [ "184 + 147 = ?", 331 ], [ "169 + 78 = ?", 247 ], [ "93 + 150 = ?", 243 ], [ "81 + 27 = ?", 108 ], [ "124 + 78 = ?", 202 ], [ "126 + 163 = ?", 289 ], [ "154 + 115 = ?", 269 ], [ "178 + 104 = ?", 282 ], [ "98 + 80 = ?", 178 ], [ "195 + 113 = ?", 308 ], [ "173 + 91 = ?", 264 ], [ "141 + 95 = ?", 236 ], [ "53 + 188 = ?", 241 ], [ "127 + 104 = ?", 231 ], [ "187 + 40 = ?", 227 ], [ "43 + 156 = ?", 199 ], [ "141 + 111 = ?", 252 ], [ "43 + 130 = ?", 173 ], [ "178 + 63 = ?", 241 ], [ "102 + 176 = ?", 278 ], [ "131 + 140 = ?", 271 ], [ "63 + 42 = ?", 105 ], [ "62 + 93 = ?", 155 ], [ "185 + 101 = ?", 286 ], [ "107 + 162 = ?", 269 ], [ "72 + 139 = ?", 211 ], [ "91 + 146 = ?", 237 ], [ "151 + 84 = ?", 235 ], [ "103 + 86 = ?", 189 ], [ "51 + 93 = ?", 144 ], [ "195 + 96 = ?", 291 ], [ "76 + 89 = ?", 165 ], [ "61 + 129 = ?", 190 ], [ "115 + 107 = ?", 222 ], [ "43 + 60 = ?", 103 ], [ "165 + 110 = ?", 275 ], [ "99 + 71 = ?", 170 ], [ "61 + 96 = ?", 157 ], [ "65 + 109 = ?", 174 ], [ "113 + 168 = ?", 281 ], [ "83 + 83 = ?", 166 ], [ "160 + 157 = ?", 317 ], [ "141 + 138 = ?", 279 ], [ "103 + 34 = ?", 137 ], [ "109 + 140 = ?", 249 ], [ "159 + 54 = ?", 213 ], [ "192 + 108 = ?", 300 ], [ "187 + 182 = ?", 369 ], [ "84 + 142 = ?", 226 ], [ "197 + 61 = ?", 258 ], [ "128 + 106 = ?", 234 ], [ "44 + 129 = ?", 173 ], [ "171 + 167 = ?", 338 ], [ "54 + 199 = ?", 253 ], [ "111 + 37 = ?", 148 ], [ "140 + 36 = ?", 176 ], [ "49 + 72 = ?", 121 ], [ "39 + 144 = ?", 183 ], [ "164 + 192 = ?", 356 ], [ "39 + 183 = ?", 222 ], [ "143 + 105 = ?", 248 ], [ "165 + 94 = ?", 259 ], [ "123 + 52 = ?", 175 ], [ "42 + 88 = ?", 130 ], [ "190 + 141 = ?", 331 ], [ "123 + 175 = ?", 298 ], [ "54 + 21 = ?", 75 ], [ "41 + 93 = ?", 134 ], [ "118 + 44 = ?", 162 ], [ "33 + 70 = ?", 103 ], [ "67 + 166 = ?", 233 ], [ "163 + 194 = ?", 357 ], [ "169 + 112 = ?", 281 ], [ "45 + 133 = ?", 178 ], [ "172 + 161 = ?", 333 ], [ "198 + 109 = ?", 307 ], [ "160 + 189 = ?", 349 ], [ "114 + 34 = ?", 148 ], [ "161 + 137 = ?", 298 ], [ "153 + 174 = ?", 327 ], [ "128 + 68 = ?", 196 ], [ "172 + 69 = ?", 241 ], [ "108 + 68 = ?", 176 ], [ "42 + 64 = ?", 106 ], [ "76 + 73 = ?", 149 ], [ "39 + 47 = ?", 86 ], [ "21 + 129 = ?", 150 ], [ "95 + 145 = ?", 240 ], [ "128 + 181 = ?", 309 ], [ "127 + 114 = ?", 241 ], [ "170 + 107 = ?", 277 ], [ "24 + 114 = ?", 138 ], [ "130 + 97 = ?", 227 ], [ "157 + 79 = ?", 236 ], [ "148 + 100 = ?", 248 ], [ "41 + 103 = ?", 144 ], [ "160 + 85 = ?", 245 ] ]
        self.question, self.answer = random.choice(self.options)


        super().__init__("welcome", timeout=None)
        textinput = discord.ui.TextInput(label=f"What is {self.question}?", required=True, custom_id="modal:text-input", placeholder="Answer Here...", style=discord.TextInputStyle.short)
        self.add_item(textinput)
    
    async def callback(self, interaction: discord.Interaction):
        entrant = database.fetch_entrant(self.giveaway['giveawayID'], interaction.user.id)
        # if entrant:
        #     return await interaction.send("You are already in this Giveaway!", ephemeral=True)

        responseValue = interaction.data['components'][0]["components"][0]["value"]
        if responseValue.isdigit():
            responseValue = int(responseValue)
            if responseValue == self.answer:
                
                database.create_entrant(self.giveaway['giveawayID'], interaction)
                self.giveaway = database.fetch_giveaway(self.giveaway['giveawayID'])
                msg = await interaction.channel.fetch_message(self.giveaway['messageID'])
                x = re.sub("Entries: \*\*([0-9]+)\*\*", f"Entries: **{len(database.fetch_entrants(self.giveaway['giveawayID']))}**", msg.embeds[0].description)
                msg.embeds[0].description = x
                await msg.edit(embeds=msg.embeds)
                return await interaction.send("You have been entered into the giveaway!", ephemeral=True)
        return await interaction.send("Got the answer wrong you plonker", ephemeral=True)

class GiveawayEntry_button(discord.ui.Button):

    def __init__(self, giveaway):
        self.giveaway = giveaway
        super().__init__(style=discord.ButtonStyle.blurple, label="🎉", custom_id=f"button:{self.giveaway['giveawayID']}")

    async def callback(self, interaction: Interaction):
        return await interaction.response.send_modal(GiveawayModal(self.giveaway))

class GiveawayEntry(discord.ui.View):

    def __init__(self, giveaway: dict):
        self.giveaway = giveaway
        super().__init__(timeout=None, auto_defer=True)
        self.add_item(GiveawayEntry_button(self.giveaway))




durationOptions = {
    "Seconds": 1,
    "Minutes": 60, 
    "Hours": 3600,
    "Days": 86400,
    "Weeks": 604800
}

database = Database()


async def giveaway_finish(giveaway: dict):
    endingAt = parser.parse(giveaway['endsAt']).timestamp()
    totalSeconds = endingAt - UTC()
    await asyncio.sleep(totalSeconds)
    giveaway = database.fetch_giveaway(giveaway['giveawayID']) # update info
    entrants = database.fetch_entrants(giveaway['giveawayID'])
    try:
        winners = random.sample(entrants, k=giveaway['winners'])
    except:
        winners = entrants[:giveaway['winners']]
    winners = '\n'.join([f'<@{x["entrantID"]}>' for x in winners])

    channel = await bot.fetch_channel(giveaway['channelID'])
    msg = await channel.fetch_message(giveaway['messageID'])
    await msg.reply(f"Congratulations! The winner{'s' if giveaway['winners'] > 1 else ''} for **{giveaway['title']}** {'is' if giveaway['winners'] == 1 else 'are'}\n>>> {winners}")
    try:
        msg.embeds[0].description = msg.embeds[0].description.replace('Ends: ', "Ended At: ")
        await msg.edit(view=None, embeds=msg.embeds)
    except:
        pass
    database.cursor.execute("UPDATE tblGiveaway SET isActive=0 WHERE giveawayID=?", [giveaway['giveawayID']])
    database.database.commit()

@bot.event
async def on_ready():
    giveaways = database.fetch_giveaways(True)
    for giveaway in giveaways:
        bot.add_view(GiveawayEntry(giveaway))
        await giveaway_finish(giveaway)
    print("bot is ready")

@bot.slash_command(name='start', guild_ids=guilds, description='Start Giveaway')
async def startCMD(interaction: discord.Interaction, title, description, duration = discord.SlashOption(required=True, name="duration", description="Autocomplete"), winners: int=discord.SlashOption(required=True, min_value=1)):
    if not any([x.id in data['Whitelisted Roles'] for x in interaction.user.roles]): return await interaction.send("You are not whitelisted to do this command!", ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    secondsTotal = 0
    for option, conv in durationOptions.items():
        if option[:-1] in duration:
            inf = re.findall("([0-9]+)", duration)
            secondsTotal = float(inf[0]) * conv
            break
    if secondsTotal == 0:
        return await interaction.send("Seems duration was inputted wrong mate.", ephemeral=True)
    
    newdescription = description+ f'\n\nEnds: <t:{int(UTC()+secondsTotal)}:R>\nHost: {interaction.user.mention}\nEntries: **0**\nWinners: **{winners}**'
    giveaway = database.create_giveaway(interaction, winners, secondsTotal, title, description)
    message = await interaction.channel.send(embed=discord.Embed(colour=0x26c7ff, title=title, description=newdescription), view=GiveawayEntry(giveaway))
    database.update_giveaway(giveaway['giveawayID'], message.id, interaction.channel.id)
    await giveaway_finish(giveaway)
    await interaction.send(f"aye mate it has been completed, ID: {giveaway['giveawayID']}", ephemeral=True)

@startCMD.on_autocomplete("duration")
async def favorite_dog(interaction: Interaction, duration: str):
    inf = re.findall("([0-9]+)", duration)
    if inf:
        return await interaction.response.send_autocomplete([f'{inf[0]} {a if inf[0] != "1" else a[:-1]}' for a in durationOptions.keys()])
    return await interaction.response.send_autocomplete(["Enter Numbers"])

from playwright.async_api import async_playwright

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
            await interaction.send(f"{request}\n\n> {(await response_info.body()).decode()}")
            bot.divIndex+=1

AICHAT()

bot.run(data['Token'])