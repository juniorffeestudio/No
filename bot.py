import os
import time
import asyncio
import threading
import aiohttp
import discord
from discord.ext import commands
from flask import Flask

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

BYPASS_CHANNEL_ID = 1551336576649396274

BYPASS_API = "https://api.bypass.vip/bypass"

HEADER_TEXT = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "**🚫 ESSE CANAL É APENAS DE BYPASS — NÃO MANDE MENSAGENS NORMAIS**\n"
    "**🚫 THIS CHANNEL IS BYPASS ONLY — DO NOT SEND NORMAL MESSAGES**\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "**PT:** Mande um link encurtado (Linkvertise, LootLabs, Work.ink, etc) e o bot vai bypassar automaticamente.\n"
    "**EN:** Send a shortened link (Linkvertise, LootLabs, Work.ink, etc) and the bot will bypass it automatically.\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)

SHORTENERS = (
    "linkvertise.com", "linkvertise.net", "link-to.net", "linkvertise.co",
    "lootlabs.gg", "loot-link.com", "loot-links.com", "links-loot.com",
    "lootlinks.gg", "lootdest.com", "lootdest.org", "lootdest.info",
    "adf.ly", "adfoc.us", "shrinkme.io", "shrinkearn.com", "shorte.st",
    "bc.vc", "ouo.io", "ouo.press", "exe.io", "exey.io", "sub2unlock.net",
    "sub2unlock.com", "sub2get.com", "boost.ink", "boostlink.pro",
    "mboost.me", "work.ink", "workink.net", "up-to-down.net",
    "linkunlocker.com", "social-unlock.com", "socialwolvez.com",
    "rekonise.com", "sub1s.com", "sub4unlock.com", "sub4unlock.io",
    "yosh.gg", "spaste.com", "cuty.io", "clk.sh", "clk.wiki", "clickscoin.com"
)

last_bypass_time = 0
bypass_lock = asyncio.Lock()

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Kamui Bypass Bot online!", 200

def run_server():
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!byp ", intents=intents, help_command=None)

def extract_url(text):
    for part in text.split():
        if part.startswith("http://") or part.startswith("https://"):
            return part.strip()
    return None

def is_shortener(url):
    url_lower = url.lower()
    return any(domain in url_lower for domain in SHORTENERS)

async def bypass_url(url):
    headers = {"Content-Type": "application/json"}
    payload = {"url": url}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(BYPASS_API, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=45)) as r:
                text = await r.text()
                try:
                    data = await r.json()
                except Exception:
                    return None, text
                if isinstance(data, dict):
                    if data.get("status") == "success" or data.get("success") is True:
                        result = data.get("result") or data.get("destination") or data.get("url")
                        return result, None
                    err = data.get("message") or data.get("error") or text
                    return None, err
                return None, text
    except Exception as e:
        return None, str(e)

async def send_pinned_header():
    try:
        channel = bot.get_channel(BYPASS_CHANNEL_ID)
        if channel is None:
            channel = await bot.fetch_channel(BYPASS_CHANNEL_ID)
        async for msg in channel.history(limit=50):
            if msg.author == bot.user and msg.pinned:
                return
        m = await channel.send(HEADER_TEXT)
        await m.pin()
    except Exception as e:
        print(f"Erro ao fixar cabeçalho: {e}")

@bot.event
async def on_ready():
    print(f"✅ Bypass Bot online: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="bypass | só links"))
    await send_pinned_header()

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.channel.id != BYPASS_CHANNEL_ID:
        return

    # Sempre apaga a mensagem original (seja link ou não)
    try:
        await message.delete()
    except Exception:
        pass

    url = extract_url(message.content)

    # Se não for link de encurtador → avisa e apaga
    if not url or not is_shortener(url):
        try:
            warn = await message.channel.send(
                f"⚠️ {message.author.mention} **Este canal é apenas para bypass de links encurtados.**\n"
                f"⚠️ {message.author.mention} **This channel is bypass only.**"
            )
            await asyncio.sleep(6)
            await warn.delete()
        except Exception:
            pass
        return

    # Cooldown de 10s entre bypasses (global)
    global last_bypass_time
    async with bypass_lock:
        now = time.time()
        wait = 10 - (now - last_bypass_time)
        if wait > 0:
            try:
                warn = await message.channel.send(
                    f"⏳ Aguarde **{wait:.1f}s** para o próximo bypass / Wait **{wait:.1f}s** for next bypass"
                )
                await asyncio.sleep(wait)
                await warn.delete()
            except Exception:
                pass
        last_bypass_time = time.time()

    # Executa o bypass e mede o tempo
    start = time.time()
    result, err = await bypass_url(url)
    elapsed = time.time() - start

    if result:
        embed = discord.Embed(
            title="🔓 Bypass Concluído / Bypass Complete",
            color=0x22c55e
        )
        embed.add_field(name="Link Original", value=f"`{url}`", inline=False)
        embed.add_field(name="Link Final", value=result, inline=False)
        embed.add_field(name="⏱️ Tempo / Time", value=f"{elapsed:.2f}s", inline=False)
        embed.set_footer(text=f"Pedido por {message.author.name}")
        msg = await message.channel.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Falha no Bypass / Bypass Failed",
            description=f"Motivo / Reason: `{err}`",
            color=0xef4444
        )
        embed.add_field(name="Link Original", value=f"`{url}`", inline=False)
        embed.add_field(name="⏱️ Tempo / Time", value=f"{elapsed:.2f}s", inline=False)
        embed.set_footer(text=f"Pedido por {message.author.name}")
        msg = await message.channel.send(embed=embed)

    await asyncio.sleep(30)
    try:
        await msg.delete()
    except Exception:
        pass

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    if not DISCORD_TOKEN:
        print("❌ ERRO: variável DISCORD_TOKEN não definida.")
    else:
        bot.run(DISCORD_TOKEN)
