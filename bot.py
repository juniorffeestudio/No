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

BYPASS_APIS = [
    "https://api.bypass.vip/bypass",
    "https://api.bypass.city/bypass",
    "https://bypass-api.com/api/bypass",
]

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
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    payload = {"url": url}

    for api in BYPASS_APIS:
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(
                    api,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=40)
                ) as r:
                    text = await r.text()
                    try:
                        data = await r.json()
                    except Exception:
                        continue

                    if isinstance(data, dict):
                        ok = (
                            data.get("status") == "success"
                            or data.get("success") is True
                            or data.get("status") is True
                        )
                        if ok:
                            result = (
                                data.get("result")
                                or data.get("destination")
                                or data.get("url")
                                or data.get("bypassed")
                            )
                            if result:
                                return result, None
        except Exception:
            continue

    return None, "Nenhuma API conseguiu bypassar esse link (pode ter captcha ou estar expirado)."

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

    try:
        await message.delete()
    except Exception:
        pass

    url = extract_url(message.content)

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

    async with bypass_lock:
        wait_time = random.randint(20, 30)

        try:
            warning = await message.channel.send(
                f"🔒 {message.author.mention} **Bypass em andamento.**\n"
                f"⏱️ Aguarde **{wait_time}s** para a verificação de segurança.\n"
                f"⏱️ Please wait **{wait_time}s** for security verification."
            )
        except Exception:
            warning = None

        start = time.time()
        result, err = await bypass_url(url)
        elapsed = time.time() - start

        remaining = wait_time - elapsed
        if remaining > 0:
            for _ in range(int(remaining)):
                await asyncio.sleep(1)

        try:
            if warning:
                await warning.delete()
        except Exception:
            pass

    total_time = time.time() - start

    if result:
        embed = discord.Embed(
            title="🔓 Bypass Concluído / Bypass Complete",
            color=0x22c55e
        )
        embed.add_field(name="Link Original", value=f"`{url}`", inline=False)
        embed.add_field(name="Link Final", value=result, inline=False)
        embed.add_field(name="⏱️ Tempo total / Total time", value=f"{total_time:.2f}s", inline=False)
        embed.set_footer(text=f"Pedido por {message.author.name}")
        msg = await message.channel.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Falha no Bypass / Bypass Failed",
            description=f"Motivo / Reason: `{err}`",
            color=0xef4444
        )
        embed.add_field(name="Link Original", value=f"`{url}`", inline=False)
        embed.add_field(name="⏱️ Tempo total / Total time", value=f"{total_time:.2f}s", inline=False)
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
