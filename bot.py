from tkinter import Button

### BOT CONFIG (explained in documentation)
skins_start, skins_count = 0, 50
skin_name = "M4A1-S | Fade"
rarity = "Factory New"
statrak = False
max_float = 0.01

from bot_config import *
import asyncio
import time
from playwright.async_api import async_playwright, Playwright


def print_red(text): print("\033[91m{}\033[0m".format(text))


def print_green(text): print("\033[92m{}\033[0m".format(text))


def print_blue(text): print("\033[94m{}\33[0m".format(text))


def get_d_number(ch, id):
    ch = str(ch)
    i = 0
    while i < 4:
        ch = ch[ch.find(id) + 1:]
        i += 1
    return ch[52:170].replace('\\', '')


async def run(playwright: Playwright):
    skin_full_name = f"StatTrak™ {skin_name} ({rarity})" if statrak else f"{skin_name} ({rarity})"
    skin_page = f"https://steamcommunity.com/market/listings/730/{skin_full_name}?query=&start={skins_start}&count={skins_count}"

    chromium = playwright.chromium  # or "firefox" or "webkit"
    browser = await chromium.launch()
    context = await browser.new_context()

    if steam_login_secure == "":
        print_red("No steam_login_secure found in bot_config.py.\nMarket's currency will be random")
        time.sleep(3)
    else:
        await context.add_cookies([login_hash])

    page = await context.new_page()
    page2 = await browser.new_page()

    await page.goto(skin_page)
    await page2.goto("https://csfloat.com/checker")

    weapon_index = skins_start + 1
    skins = await page.query_selector_all('.market_recent_listing_row')

    if len(skins) == 0:
        await page.screenshot(path="error_skins.png")
        print_red("Error: 0 skins loaded!\nScreenshot saved at error_skins.png")
        exit()

    for skin in skins:
        price_el = await skin.query_selector(
            'div.market_listing_price_listings_block > div.market_listing_right_cell.market_listing_their_price > span > span.market_listing_price.market_listing_price_with_fee')
        price = (await price_el.text_content()).strip()

        btn = await skin.query_selector('.market_listing_item_img_container a')
        await btn.evaluate_handle('button => button.click()', arg=btn)
        inspect_link = await page.locator('#market_action_popup_itemactions > a').get_attribute('href')

        inpt = page2.locator('#mat-input-0')

        try:
            await page2.wait_for_selector('#mat-input-0', timeout=80000)
            await inpt.fill(inspect_link)
        except Exception as e:
            print_red(f"Failed to fill the input selector: {str(e)}")
            continue

        try:
            float_selector = '.mat-mdc-tooltip-trigger.wear'
            await page2.wait_for_selector(float_selector, timeout=80000)
            wp_float_elements = await page2.query_selector_all(float_selector)
            if not wp_float_elements:
                raise TimeoutError("Failed to find any valid float value element")

            wp_float = float(await wp_float_elements[0].text_content())
        except Exception as e:
            print_red(f"Failed to retrieve the float value: {str(e)}")
            continue

        if wp_float < max_float:
            print(f"({weapon_index}) >>> FLOAT: {wp_float} | {price} {skin_page}")
        weapon_index += 1

    await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
