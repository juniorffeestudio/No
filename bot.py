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
