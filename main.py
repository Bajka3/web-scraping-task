import requests
from bs4 import BeautifulSoup
import json

PRODUCT_DETAIL_5_URLS = ["https://www.lapierre-bike.cz/produkt/spicy-cf-69/5943",
                         "https://www.lapierre-bike.cz/produkt/aircode-drs-50/5931",
                         "https://www.lapierre-bike.cz/produkt/esensium-22-m250/5945",
                         "https://www.lapierre-bike.cz/produkt/lapierre-prorace-24-girl/5990",
                         "https://www.lapierre-bike.cz/produkt/treking-30/6011"
                         ]


def check_spec(list, keyword):
    """Control of the bike specification table. If it doesn't contain given keyword, it returns None."""
    if keyword in list:
        try:
            return list[list.index(keyword) + 1]
        except IndexError:
            pass
    return None


def scrape_product_detail_page(product_detail_url):
    """To obtain detailed information about bicycles from https://www.lapierre-bike.cz/"""
    # Web scraping
    response = requests.get(product_detail_url)
    if response.status_code != 200:
        print(f"Some problem with URL:{product_detail_url} ")
    else:
        response.encoding = response.apparent_encoding  # czech characters
        content = response.text
        soup = BeautifulSoup(content, "html.parser")

        # 1) model
        try:
            model = soup.find(name="h1").getText()
        except AttributeError:
            model = None

        # 2) main photo image- best possible image quality
        """Fotka ktera je v modelovem vystupu, nema maximalni dostupne rozliseni. Varianta full je lepsi nez 1100."""
        try:
            # main_photo_path = (soup.find(name="img", id="nahled")).get("src")          # vede k 1100
            main_photo_path_info = (soup.find(name="div", id="zoomed-image-container")).get("style")
            main_photo_path = main_photo_path_info.split("(")[1][:-2]
            if "https" not in main_photo_path:
                main_photo_path = None
        except (AttributeError, IndexError):
            main_photo_path = None

        # 3) additional photo paths - best possible image quality
        """ podobne jako u main photo image, ziskavam odkaz na fotky ve 'full' rozliseni"""
        # additional_photo_paths_all = soup.select(selector='a > img[border="0"]')          # vede k '410'
        # additional_photo_paths = [nahled.get("src") for nahled in additional_photo_paths_all]
        additional_photo_paths_all = soup.find_all(name="a", class_="html5lightbox")
        additional_photo_paths = [nahled.get("href") for nahled in additional_photo_paths_all]
        if not additional_photo_paths or "https" in additional_photo_paths:
            additional_photo_paths = None

        # 4) price - integer
        try:
            price = int(((((soup.find(name="div", class_="cena")).find(name="span")).getText()).split()[0]).replace(".", ""))
        except (NameError, IndexError, ValueError, AttributeError):
            price = None

        # 5-7) specification - model_year (int), weight, frame
        spec = soup.select(selector="table td", class_="spec")
        spec_texts = [one_spec.getText() for one_spec in spec]
        try:
            model_year = int(check_spec(spec_texts, "Ročník"))
        except (ValueError, TypeError):
            model_year = None
        weight = check_spec(spec_texts, "Hmotnost")
        frame = check_spec(spec_texts, "Rám")

        return {
            "model": model,
            "url": product_detail_url,
            "main_photo_path": main_photo_path,
            "additional_photo_paths": additional_photo_paths,
            "price": price,
            "model_year": model_year,
            "parameters": {
                "weight": weight,
                "frame": frame
            }
        }


# Scraping of multiple urls
def main(multiple_urls):
    array = [scrape_product_detail_page(url) for url in multiple_urls]
    code = json.dumps(array, indent=4)

    with open("top-5-bikes.json", "w") as file:
        print(code, file=file)


main(PRODUCT_DETAIL_5_URLS)
