import requests, os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote

headers = {'User-Agent': 'Mozilla/5.0'}
download_folder = 'C:\\Users\\sihow\\OneDrive\\Datasheet'
os.makedirs(download_folder, exist_ok=True)

def clean_filename(url):
    path = urlparse(url).path
    return os.path.basename(unquote(path))

def download_pdfs(base_url, vendor_name, subfolder_name=None):
    try:
        response = requests.get(base_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f'Failed to fetch {base_url}: {e}')
        return

    folder_name = os.path.join(download_folder, vendor_name)
    if subfolder_name:
        folder_name = os.path.join(folder_name, subfolder_name)
    os.makedirs(folder_name, exist_ok=True)

    for link in soup.find_all('a', href=True):
        if link['href'].endswith('.pdf'):
            file_url = urljoin(base_url, link['href'])
            filename = clean_filename(file_url)
            file_path = os.path.join(folder_name, filename)

            if os.path.exists(file_path):
                print(f'Skipped: {vendor_name}/{subfolder_name}/{filename}')
                continue

            try:
                file_response = requests.get(file_url, headers=headers)
                with open(file_path, 'wb') as f:
                    f.write(file_response.content)
                print(f'Downloaded: {vendor_name}/{subfolder_name}/{filename}')
            except Exception as e:
                print(f'Error downloading {filename}: {e}')

def get_raritan_products():
    support_url = 'https://www.raritan.com/support'
    response = requests.get(support_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    product_names = []

    for option in soup.find_all('option'):
        val = option.get('value')
        if val and val.startswith('/support/product/'):
            product_slug = val.split('/')[-1]
            product_names.append(product_slug)
    return product_names

# 🔗 Static sources
static_sources = {
    'Raritan': 'https://www.raritan.com/resources/data-sheets',
    'Adder': 'https://support.adder.com/tiki/tiki-index.php?page=Product+Manuals',
    'G&D': 'https://www.gdsys.com/en/service/manuals',
    'ZPE': 'https://zpesystems.com/'
}

# 🚀 Run static sources
for vendor, url in static_sources.items():
    download_pdfs(url, vendor)

# 🌀 Raritan dynamic product user guides
product_list = get_raritan_products()
for product in product_list:
    product_url = f'https://www.raritan.com/support/product/{product}'
    download_pdfs(product_url, 'RaritanManualGuide')
