import json
import google.generativeai as genai
from google.api_core import exceptions

# 1. კონფიგურაცია
GOOGLE_API_KEY = "AIzaSyBiKThWYzFz9ojLSEZdD-ydKGf1oUenxk4"
genai.configure(api_key=GOOGLE_API_KEY)

def get_best_model():
    """ავტომატურად პოულობს ხელმისაწვდომ მოდელს (Flash ან Pro)"""
    try:
        available_models = [m.name for m in genai.list_models() 
                           if 'generateContent' in m.supported_generation_methods]
        
        # პრიორიტეტი: 1.5-flash (სწრაფი), შემდეგ 1.5-pro, ბოლოს 1.0-pro
        for preferred in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if preferred in available_models:
                return preferred
        return available_models[0] if available_models else 'gemini-pro'
    except Exception:
        return 'gemini-pro'

# მოდელის ინიციალიზაცია
selected_model = get_best_model()
print(f"🔄 სისტემა ჩაირთო. გამოყენებული მოდელი: {selected_model}")
model = genai.GenerativeModel(selected_model)

def load_products():
    """JSON ფაილიდან მონაცემების წაკითხვა"""
    try:
        with open("zoomer_products.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ შეცდომა: 'zoomer_products.json' ვერ მოიძებნა. ჯერ გაუშვი scraper.py!")
        return None

def start_chat():
    products = load_products()
    if not products:
        return

    # მონაცემების მომზადება კონტექსტისთვის
    product_list = ""
    for p in products:
        product_list += f"ნამუშევარი: {p['name']}, ფასი: {p['price']} ლარი\n"

    print("\n🤖 ჩატბოტი მზად არის! დასვი კითხვა Zoomer-ის ფასებზე.")
    print("(გასასვლელად დაწერე: exit)\n")

    while True:
        query = input("კითხვა: ")
        
        if query.lower() in ['exit', 'quit', 'გასვლა', 'stop']:
            print("ნახვამდის!")
            break

        # სისტემური ინსტრუქცია AI-სთვის
        prompt = f"""
        შენ ხარ Zoomer-ის მაღაზიის ციფრული ასისტენტი.
        უპასუხე მხოლოდ ქართულ ენაზე.
        
        დაეყრდენი მხოლოდ ამ მონაცემებს:
        {product_list}
        
        თუ მომხმარებელი გკითხავს პროდუქტზე, რომელიც სიაში არ არის, უთხარი რომ ამჟამად ეს მოდელი ბაზაში არ გაქვს.
        თუ გკითხავს ფასებს, შეადარე ერთმანეთს სიაში არსებული მონაცემების მიხედვით.
        
        კითხვა: {query}
        """

        try:
            response = model.generate_content(prompt)
            print(f"\nAI: {response.text}\n" + "-"*30)
        except Exception as e:
            print(f"❌ მოხდა შეცდომა პასუხის გენერირებისას: {e}")

if __name__ == "__main__":
    start_chat()