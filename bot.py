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

def extract_url(text):
    for part in text.split():
        if part.startswith("http://") or part.startswith("https://"):
            return part.strip()
    return None

def is_shortener(url):
    u = url.lower()
    return any(s in u for s in SHORTENERS)

async def bypass_url(url):
    headers = {"Content-Type": "application/json"}
    payload = {"url": url}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                BYPASS_API,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as r:
                if r.status != 200:
                    return None, f"HTTP {r.status}"
                data = await r.json(content_type=None)
                if isinstance(data, dict):
                    result = data.get("result") or data.get("destination") or data.get("url")
                    if result:
                        return result, None
                    return None, data.get("message", "sem resultado")
                return None, "resposta inválida"
    except Exception as e:
        return None, str(e)

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

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
            w = await message.channel.send(f"⚠️ {message.author.mention} Bypass only.")
            await asyncio.sleep(6)
            await w.delete()
        except Exception:
            pass
        return

    async with bypass_lock:
        wait_time = random.randint(20, 30)
        try:
            notice = await message.channel.send(
                f"🔒 {message.author.mention} Aguarde **{wait_time}s** para verificação de segurança."
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
        embed = discord.Embed(title="🔓 Bypass Concluído", color=0x22c55e)
        embed.add_field(name="Original", value=f"`{url}`", inline=False)
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
