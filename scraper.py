import asyncio
import json
from playwright.async_api import async_playwright

async def scrape_zoomer(limit=100):
    async with async_playwright() as p:
        print("🚀 ბრაუზერი იხსნება...")
        
        # headless=False - დაინახავ პროცესს. თუ გინდა ფონზე იმუშაოს, შეცვალე True-თი.
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        target_url = "https://www.zoomer.ge/mobilurebi-2"
        print(f"🔗 გადავდივართ მისამართზე: {target_url}")
        
        try:
            await page.goto(target_url, wait_until="networkidle", timeout=60000)
            
            products = []
            seen_names = set()

            while len(products) < limit:
                # 1. მონაცემების ამოღება არსებული გვერდიდან
                # ვიყენებთ შენს მიერ ნანახ სტრუქტურას [id^="product-"]
                items = await page.query_selector_all('div[id^="product-"]')
                
                for item in items:
                    if len(products) >= limit:
                        break
                    
                    try:
                        name_el = await item.query_selector('a[title]')
                        name = await name_el.get_attribute("title") if name_el else None
                        
                        if name and name not in seen_names:
                            # ფასის ამოღება h4 თეგიდან
                            price_el = await item.query_selector('h4')
                            price_raw = await price_el.inner_text() if price_el else "0"
                            # ვტოვებთ მხოლოდ ციფრებს
                            price = "".join(filter(str.isdigit, price_raw))
                            
                            products.append({
                                "name": name,
                                "price": price
                            })
                            seen_names.add(name)
                    except:
                        continue

                print(f"✅ შეგროვდა {len(products)} ნივთი...")

                if len(products) >= limit:
                    break

                # 2. "მეტის ნახვა" ღილაკზე დაჭერა
                try:
                    # ვიყენებთ .last-ს, რათა გვერდის ბოლოში არსებული მთავარი ღილაკი ვიპოვოთ
                    load_more_btn = page.get_by_text("მეტის ნახვა").last
                    
                    if await load_more_btn.is_visible():
                        # მივდივართ ღილაკთან, რომ ეკრანზე გამოჩნდეს
                        await load_more_btn.scroll_into_view_if_needed()
                        await asyncio.sleep(1)
                        
                        print("⏳ ვაკლიკებ 'მეტის ნახვა' ღილაკს...")
                        await load_more_btn.click()
                        
                        # ველოდებით ახალი ნივთების ჩატვირთვას (დაახლოებით 4 წამი)
                        await asyncio.sleep(4)
                    else:
                        print("🏁 მეტი ნივთი აღარ არის ჩასატვირთი.")
                        break
                except Exception as e:
                    print(f"⚠️ ღილაკზე დაჭერა ვერ მოხერხდა: {e}")
                    break

            # 3. მონაცემების შენახვა JSON ფაილში
            with open("zoomer_products.json", "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=4)
            
            print(f"\n🎉 დასრულდა! მონაცემები შენახულია 'zoomer_products.json'-ში.")

        except Exception as e:
            print(f"❌ მოხდა კრიტიკული შეცდომა: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    # აქ შეგიძლია შეცვალო ლიმიტი (მაგალითად 200 ან 500)
    asyncio.run(scrape_zoomer(limit=100))