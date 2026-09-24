import asyncio
from auto_captcha_solver import smart_page

async def main():
    # Você precisa criar uma conta no NopeCHA e pegar sua API Key
    # O plano gratuito oferece 100 soluções por dia
    NOPECHA_KEY = "SUA_CHAVE_NOPECHA_AQUI" 
    
    async with smart_page(api_key=NOPECHA_KEY) as page:
        print("Navegando para a página de teste do Steam...")
        # Esta é uma página oficial do Steam usada para testar captchas
        await page.goto("https://store.steampowered.com/join/")
        
        print("Preenchendo o formulário...")
        await page.fill('input[name="email"]', 'teste@exemplo.com')
        await page.fill('input[name="reenter_email"]', 'teste@exemplo.com')
        
        print("Clicando no botão de criar conta (o captcha deve aparecer)...")
        await page.click('button[type="submit"]')
        
        # A biblioteca `auto_captcha_solver` deve detectar e resolver o captcha automaticamente.
        # Esperamos um tempo para ver o resultado.
        print("Aguardando resolução automática do captcha...")
        await page.wait_for_timeout(30000) 
        
        print("Log de captchas:", page.captcha_log)
        await page.screenshot(path="resultado.png")

if __name__ == "__main__":
    asyncio.run(main())
