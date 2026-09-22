import os
import time
import random
import asyncio
import threading
import aiohttp
import discord
from discord.ext import commands
from flask import Flask

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BYPASS_CHANNEL_ID = 1551336576649396274
BYPASS_API = "https://api.bypass.vip/bypass"

app = Flask(__name__)

@app.route('/')
def health_check():
    return "OK", 200

def run_server():
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!byp ", intents=intents, help_command=None)

HEADER_MSG = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "**🚫 ESSE CANAL É DE AUTO BYPASS**\n"
    "**🚫 THIS CHANNEL IS AUTO BYPASS**\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "**🇧🇷 PT:**\n"
    "ESSE CANAL É DE AUTO BYPASS. SE EU DEMORAR PARA MANDAR É PORQUE ISSO SE CHAMA 'PARA NÃO ACIONAR ANTI-BOT'!\n\n"
    "**🇺🇸 EN:**\n"
    "THIS CHANNEL IS AUTO BYPASS. IF I TAKE A LONG TIME TO SEND IT, IT'S BECAUSE IT'S CALLED 'NOT TO TRIGGER ANTI-BOT'!\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "**PT:** Mande um link encurtado e o bot vai bypassar automaticamente.\n"
    "**EN:** Send a shortened link and the bot will bypass it automatically.\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)

SERVICES_MSG = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "**📋 SERVIÇOS SUPORTADOS / SUPPORTED SERVICES**\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "**🔑 KEYSYSTEM**\n"
    "`auth.platorelay.com` `auth.platoboost.app` `auth.platoboost.me`\n"
    "`ads.pandauth.com` `pandadevelopment.net` `new.pandadevelopment.net`\n"
    "`trigonevo.com` `violated.lol` `blox-script.com` `boblox-script.com`\n"
    "`hydrogen.lat` `key.codex.lol`\n\n"
    "**🔗 ADLINK**\n"
    "`linkvertise.com` `link-to.net` `link-hub.net` `link-target.org`\n"
    "`link-target.net` `link-center.net` `direct-link.net` `loot-link.com`\n"
    "`links.lootlabs.gg` `lootdest.org` `free-content.pro` `lootdest.com`\n"
    "`bleleadersto.com` `daughablelea.com` `fast-links.org` `best-links.org`\n"
    "`free-leaks.com` `discordlink.cc` `rapid-links.net` `onlylinksmegas.xyz`\n"
    "`lootlinks.co` `redeem-nitro.com` `lootdest.net` `tonordersitye.com`\n"
    "`mega-redirect.com` `butthedshookh.org` `certainlywhenev.org`\n"
    "`ultra-links.net` `aywithmehesa.org` `loot-links.com` `onlyshare.info`\n"
    "`mega-guy.com` `speedy-links.com` `megadropz.com` `depravityweb.co`\n"
    "`missleakz.com` `godxnationds.com` `direct-links.net` `of-leaks.xyz`\n"
    "`direct-links.org` `ofhub-leaks.com` `linksloot.net` `worldpacks.co`\n"
    "`links-loot.com` `lootdest.info` `lootlink.org` `pkofs.com`\n"
    "`mdlinkshub.com` `nswfbox.com` `thhaven.net` `onlymega.co`\n"
    "`goldmega.online` `onlyfunlink.com` `rbxdrops.org` `leaksmix.com`\n"
    "`darkmodz-links.com` `megaplugleaks.com`\n\n"
    "**📋 + 136 serviços / + 136 services**\n\n"
    "**📎 PASTE**\n"
    "`pastebin.com` `paste-drop.com` `pastefy.app` `rentry.co`\n"
    "`paster.so` `pastelua.com`\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)

SHORTENERS = (
    # keysystem
    "platorelay.com", "platoboost.app", "platoboost.me", "pandauth.com",
    "pandadevelopment.net", "trigonevo.com", "violated.lol",
    "blox-script.com", "boblox-script.com", "hydrogen.lat", "codex.lol",
    # adlink
    "linkvertise.com", "link-to.net", "link-hub.net", "link-target.org",
    "link-target.net", "link-center.net", "direct-link.net", "loot-link.com",
    "lootlabs.gg", "lootdest.org", "free-content.pro", "lootdest.com",
    "bleleadersto.com", "daughablelea.com", "fast-links.org", "best-links.org",
    "free-leaks.com", "discordlink.cc", "rapid-links.net", "onlylinksmegas.xyz",
    "lootlinks.co", "redeem-nitro.com", "lootdest.net", "tonordersitye.com",
    "mega-redirect.com", "butthedshookh.org", "certainlywhenev.org",
    "ultra-links.net", "aywithmehesa.org", "loot-links.com", "onlyshare.info",
    "mega-guy.com", "speedy-links.com", "megadropz.com", "depravityweb.co",
    "missleakz.com", "godxnationds.com", "direct-links.net", "of-leaks.xyz",
    "direct-links.org", "ofhub-leaks.com", "linksloot.net", "worldpacks.co",
    "links-loot.com", "lootdest.info", "lootlink.org", "pkofs.com",
    "mdlinkshub.com", "nswfbox.com", "thhaven.net", "onlymega.co",
    "goldmega.online", "onlyfunlink.com", "rbxdrops.org", "leaksmix.com",
    "darkmodz-links.com", "megaplugleaks.com",
    # outros comuns
    "adf.ly", "adfoc.us", "shrinkme.io", "shrinkearn.com", "shorte.st",
    "bc.vc", "ouo.io", "ouo.press", "exe.io", "exey.io", "sub2unlock.net",
    "sub2unlock.com", "sub2get.com", "boost.ink", "boostlink.pro",
    "mboost.me", "work.ink", "workink.net", "up-to-down.net",
    "linkunlocker.com", "social-unlock.com", "socialwolvez.com",
    "rekonise.com", "sub1s.com", "sub4unlock.com", "sub4unlock.io",
    "yosh.gg", "spaste.com", "cuty.io", "clk.sh", "clk.wiki", "clickscoin.com"
)

PASTE_DOMAINS = ("pastebin.com", "paste-drop.com", "pastefy.app", "rentry.co", "paster.so", "pastelua.com")

bypass_lock = asyncio.Lock()

def extract_url(text):
    for part in text.split():
        if part.startswith("http://") or part.startswith("https://"):
            return part.strip()
    return None

def is_shortener(url):
    u = url.lower()
    return any(s in u for s in SHORTENERS)

def is_paste(url):
    u = url.lower()
    return any(s in u for s in PASTE_DOMAINS)

async def fetch_paste(url):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=20)) as r:
                if r.status != 200:
                    return None, f"HTTP {r.status}"
                content = await r.text()
                if "pastefy.app" in url:
                    paste_id = url.rstrip("/").split("/")[-1]
                    api = f"https://pastefy.app/api/v2/paste/{paste_id}"
                    async with s.get(api, timeout=aiohttp.ClientTimeout(total=20)) as r2:
                        if r2.status == 200:
                            data = await r2.json(content_type=None)
                            if isinstance(data, dict) and data.get("content"):
                                return data["content"], None
                if "rentry.co" in url:
                    raw_url = url.rstrip("/") + "/raw"
                    async with s.get(raw_url, timeout=aiohttp.ClientTimeout(total=20)) as r3:
                        if r3.status == 200:
                            return await r3.text(), None
                return content, None
    except Exception as e:
        return None, str(e)

async def bypass_url(url):
    headers = {"Content-Type": "application/json"}
    payload = {"url": url}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                BYPASS_API,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=45)
            ) as r:
                text = await r.text()
                try:
                    data = await r.json(content_type=None)
                except Exception:
                    return None, f"HTTP {r.status}"
                if isinstance(data, dict):
                    if data.get("status") == "success" or data.get("success") is True:
                        result = data.get("result") or data.get("destination") or data.get("url")
                        if result:
                            return result, None
                    return None, data.get("message") or data.get("error") or "sem resultado"
                return None, "resposta invalida"
    except Exception as e:
        return None, str(e)

async def send_pinned_messages():
    try:
        channel = bot.get_channel(BYPASS_CHANNEL_ID)
        if channel is None:
            channel = await bot.fetch_channel(BYPASS_CHANNEL_ID)

        has_header = False
        has_services = False
        async for msg in channel.history(limit=200):
            if msg.author == bot.user and msg.pinned:
                if "ESSE CANAL É DE AUTO BYPASS" in msg.content:
                    has_header = True
                if "SERVIÇOS SUPORTADOS" in msg.content:
                    has_services = True

        if not has_header:
            m = await channel.send(HEADER_MSG)
            await m.pin()

        if not has_services:
            m = await channel.send(SERVICES_MSG)
            await m.pin()
    except Exception as e:
        print(f"Erro ao fixar mensagens: {e}")

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="auto-bypass"))
    await send_pinned_messages()

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.channel.id != BYPASS_CHANNEL_ID:
        return

    try:
        await message.delete()
    except Exception:
        pass

    url = extract_url(message.content)

    if not url:
        try:
            w = await message.channel.send(f"⚠️ {message.author.mention} Bypass only.")
            await asyncio.sleep(6)
            await w.delete()
        except Exception:
            pass
        return

    if not is_shortener(url) and not is_paste(url):
        try:
            w = await message.channel.send(f"⚠️ {message.author.mention} Link nao suportado.")
            await asyncio.sleep(6)
            await w.delete()
        except Exception:
            pass
        return

    async with bypass_lock:
        wait_time = random.randint(20, 30)
        try:
            notice = await message.channel.send(
                f"🔒 {message.author.mention} Aguarde **{wait_time}s** para verificacao de seguranca."
            )
        except Exception:
            notice = None

        start = time.time()

        if is_paste(url):
            result, err = await fetch_paste(url)
        else:
            result, err = await bypass_url(url)

        elapsed = time.time() - start
        remaining = wait_time - elapsed
        if remaining > 0:
            await asyncio.sleep(remaining)

        if notice:
            try:
                await notice.delete()
            except Exception:
                pass

    total = time.time() - start

    if result:
        content = result if len(result) < 1500 else result[:1500] + "..."
        embed = discord.Embed(title="🔓 Bypass Concluido", color=0x22c55e)
        embed.add_field(name="Original", value=f"`{url}`", inline=False)
        if is_paste(url):
            embed.add_field(name="Conteudo / Content", value=f"```\n{content}\n```", inline=False)
        else:
            embed.add_field(name="Final", value=result, inline=False)
        embed.add_field(name="Tempo", value=f"{total:.2f}s", inline=False)
    else:
        embed = discord.Embed(title="❌ Falha no Bypass", color=0xef4444)
        embed.add_field(name="Original", value=f"`{url}`", inline=False)
        embed.add_field(name="Motivo", value=f"`{err}`", inline=False)
        embed.add_field(name="Tempo", value=f"{total:.2f}s", inline=False)

    try:
        msg = await message.channel.send(embed=embed)
        await asyncio.sleep(30)
        await msg.delete()
    except Exception:
        pass

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    if not DISCORD_TOKEN:
        print("ERRO: DISCORD_TOKEN nao definida.")
    else:
        bot.run(DISCORD_TOKEN)
