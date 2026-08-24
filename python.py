import json
import aiohttp
import asyncio
from pyppeteer import launch
import time
#import discord

#webhook_url = ""

#Who cares about watching chats and Discord?
#We just want to send messages, amirite?

#async def watch_chat(page):
#    seen = set()
#
#    # initialize baseline
#    initial = await page.evaluate("""
#        () => Array.from(document.querySelector('.chatHistory')?.children || [])
#            .map(x => x.innerText)
#    """)
#
#    for msg in initial:
#        seen.add(msg)
#
#    while True:
#        messages = await page.evaluate("""
#            () => Array.from(document.querySelector('.chatHistory')?.children || [])
#                .map(x => x.innerText)
#        """)
#
#        for msg in messages:
#            if not msg or msg in seen:
#                continue
#
#            seen.add(msg)
#            return msg
#
#        await asyncio.sleep(0.5)  # prevent CPU spam


async def login(page, usern, passw):
    # username
    selector = 'input._2GBWeup5cttgbTw8FM3tfx[type="text"]'
    await page.waitForSelector(selector)
    await page.type(selector, usern)

    # password
    selector = 'input._2GBWeup5cttgbTw8FM3tfx[type="password"]'
    await page.waitForSelector(selector)
    await page.type(selector, passw)

    # submit
    selector = 'button[type="submit"]'
    await page.waitForSelector(selector, {'visible': True})
    await asyncio.sleep(0.2)

    await page.evaluate("""
        () => {
            const btn = document.querySelector('button[type="submit"]');
            if (btn && !btn.disabled) btn.click();
        }
    """)


#async def webhook_message(msg):
#    async with aiohttp.ClientSession() as session:
#        await session.post(webhook_url, json={"content": msg})


#async def relay_message(time, name, msg):
#    async with aiohttp.ClientSession() as session:
#        await session.post(webhook_url, json={
#            "content": f"[{time}] {name}: {msg}"
#        })

async def sayInChat(text, page):
    textarea_selector = 'textarea.chatentry_chatTextarea_113iu.Focusable'
    button_selector = 'button.chatentry_chatSubmitButton_RVIs8.Focusable[type="submit"]'
    await page.waitForSelector(textarea_selector)
    await page.evaluate("""
        (sel, value) => {
            const el = document.querySelector(sel);
            if (!el) return;

            el.focus();
            el.value = value;

            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
    """, textarea_selector, text)
    await page.keyboard.press(' ')
    await page.click(button_selector)

async def main():
    global webhook_url  # FIXED scope

    # load config
    with open("config.json", "r") as f:
        data = json.load(f)

    usern = data["user"]
    passw = data["pass"]
    #webhook_url = data["webhook"]
    #spym = data["spy"]
    #bot_token = data["bot"]
    #channel_id = data["channel"]
    browser_path = data["browser"]
    raid_msg = data["message"]
    delay = data["delay"]
    
    #holy shit so... much... data...
    #well not anymore, me from like 2 months ago
    
    browser = await launch(
        headless=False,
        executablePath=browser_path,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-default-apps',
            '--disable-extensions',
            '--disable-component-extensions-with-background-pages',
            '--disable-notifications',
            '--window-size=1200,800'
        ]
    )

    # clean default tab
    pages = await browser.pages()
    if pages:
        await pages[0].close()

    page = await browser.newPage()

    # block notifications
    client = await page.target.createCDPSession()
    await client.send("Browser.setPermission", {
        "permission": {"name": "notifications"},
        "setting": "denied"
    })

    # go to steam chat
    await page.goto('https://steamcommunity.com/login/home/?goto=%2Fchat%2F')

    # login
    await login(page, usern, passw)

    await asyncio.sleep(10)
    input("Press enter once you're inside the chat...")
    await asyncio.sleep(2)

    print("Logged in, starting raid...")

    selector = ".chatRoomGroupHeaderName"
    element = await page.waitForSelector(selector, {"visible": True})
    text = await page.evaluate('(el) => el.textContent', element)

    #await webhook_message("Raiding in chatroom: " + text)

    #if spym == "false":
    #    #setup bot shit
    #    intents = discord.Intents.default()
    #    intents.message_content = True
    #
    #    bot = discord.Client(intents=intents)
    # 
    #    @bot.event
    #    async def on_ready():
    #        print(f"Bot launched as {bot.user}")
    #        print(f"Listening on channel ID: {channel_id}")
    # 
    #    @bot.event
    #    async def on_message(msg):
    #        if msg.author == client.user:
    #            return
    # 
    #       if msg.channel.id != channel_id:
    #            return
    # 
    #        sayInChat(f"{msg.author.display_name} ({msg.author_name}): {msg.content}",page)
    #
    #    bot.run(bot_token)

    while True:
        sayInChat(f"{raid_msg},page)
        time.sleep(delay)#this might be the intended way to do it or not the intended way,
                         #considering that asyncio exists here

print("Initializing SteamRaider V1...")
asyncio.run(main())
