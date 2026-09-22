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

# COLE AQUI O ID DO CANAL QUE VOCE COPIOU
BYPASS_CHANNEL_ID = 1551336576649396274

BYPASS_APIS = [
    {"url": "https://api.bypass.vip/bypass", "method": "post", "key": "url"},
    {"url": "https://api.bypass.city/bypass", "method": "post", "key": "url"},
    {"url": "https://api.bypass.tools/bypass", "method": "post", "key": "url"},
]

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

SHORTENERS = (
    "linkvertise", "lootlabs", "loot-link", "lootlinks", "lootdest",
    "work.ink", "workink", "boost.ink", "boostlink", "mboost",
    "rekonise", "sub2unlock", "sub2get", "sub4unlock", "sub1s",
    "adf.ly", "adfoc.us", "shrinkme", "shrinkearn", "shorte.st",
    "ouo.io", "ouo.press", "exe.io", "exey.io", "bc.vc",
    "up-to-down", "linkunlocker", "social-unlock", "socialwolvez",
    "yosh.gg", "spaste", "cuty.io", "clk.sh", "clk.wiki", "clickscoin"
)

bypass_lock = asyncio.Lock()

HEADER_TEXT = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "**🚫 ESSE CANAL É DE AUTO BYPASS**\n"
    "**🚫 THIS CHANNEL IS AUTO BYPASS**\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "\n"
    "**🇧🇷 PT:**\n"
    "ESSE CANAL É DE AUTO BYPASS. SE EU DEMORAR PARA MANDAR É PORQUE ISSO SE CHAMA 'PARA NÃO ACIONAR ANTI-BOT'!\n"
    "\n"
    "**🇺🇸 EN:**\n"
    "THIS CHANNEL IS AUTO BYPASS. IF I TAKE A LONG TIME TO SEND IT, IT'S BECAUSE IT'S CALLED 'NOT TO TRIGGER ANTI-BOT'!\n"
    "\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "**PT:** Mande um link encurtado (Linkvertise, LootLabs, Work.ink) e o bot vai bypassar automaticamente.\n"
    "**EN:** Send a shortened link (Linkvertise, LootLabs, Work.ink) and the bot will bypass it automatically.\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)

def extract_url(text):
    for part in text.split():
        if part.startswith("http://") or part.startswith("https://"):
            return part.strip()
    return None

def is_shortener(url):
    u = url.lower()
    return any(s in u for s in SHORTENERS)

async def bypass_url(url):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    payload = {"url": url}

    for api in BYPASS_APIS:
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(
                    api["url"],
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as r:
                    if r.status != 200:
                        continue
                    text = await r.text()
                    try:
                        data = await r.json(content_type=None)
                    except Exception:
                        continue

                    if isinstance(data, dict):
                        result = (
                            data.get("result")
                            or data.get("destination")
                            or data.get("url")
                            or data.get("bypassed")
                            or data.get("target")
                        )
                        if result and isinstance(result, str) and result.startswith("http"):
                            return result, None

                        # Alguns formatos retornam em lista
                        if "results" in data and isinstance(data["results"], list):
                            for item in data["results"]:
                                if isinstance(item, dict):
                                    r2 = item.get("result") or item.get("url")
                                    if r2:
                                        return r2, None
        except Exception:
            continue

    return None, "Nenhuma das APIs conseguiu bypassar (link com captcha, expirado ou nao suportado)."

async def send_pinned_header():
    try:
        channel = bot.get_channel(BYPASS_CHANNEL_ID)
        if channel is None:
            channel = await bot.fetch_channel(BYPASS_CHANNEL_ID)
        async for msg in channel.history(limit=100):
            if msg.author == bot.user and msg.pinned:
                return
        m = await channel.send(HEADER_TEXT)
        await m.pin()
    except Exception as e:
        print(f"Erro ao fixar cabecalho: {e}")

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")
    print(f"Canal configurado: {BYPASS_CHANNEL_ID}")
    channel = bot.get_channel(BYPASS_CHANNEL_ID)
    if channel is None:
        print("AVISO: ID do canal invalido ou bot nao tem acesso a ele.")
    await send_pinned_header()

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
    if not url or not is_shortener(url):
        try:
            w = await message.channel.send(f"Aviso: {message.author.mention} Bypass only.")
            await asyncio.sleep(6)
            await w.delete()
        except Exception:
            pass
        return

    async with bypass_lock:
        wait_time = random.randint(20, 30)
        try:
            notice = await message.channel.send(
                f"Bypass em andamento. Aguarde {wait_time}s..."
            )
        except Exception:
            notice = None

        start = time.time()
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
        embed = discord.Embed(title="Bypass Concluido", color=0x22c55e)
        embed.add_field(name="Original", value=f"`{url}`", inline=False)
        embed.add_field(name="Final", value=result, inline=False)
        embed.add_field(name="Tempo", value=f"{total:.2f}s", inline=False)
    else:
        embed = discord.Embed(title="Falha no Bypass", color=0xef4444)
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
