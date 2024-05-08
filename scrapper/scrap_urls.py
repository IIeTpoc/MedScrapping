import os
import requests
from bs4 import BeautifulSoup
import argparse


def scrape_page(url):
    try:
        response = requests.get(url, timeout=10)  # Set timeout to avoid hanging on a request
        response.raise_for_status()  # Raises HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Error fetching {url}: {str(e)}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    for element in soup(["script", "style", "form"]):
        element.decompose()  # Clean the page from scripts, styles, and forms

    extracted_texts = []
    main_content = soup.find('div', class_='show')
    if main_content:
        content_elements = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
        for element in content_elements:
            text = element.get_text(separator="\n", strip=True)
            if text:
                extracted_texts.append(text)

    return '\n'.join(extracted_texts)


def write_files(first_page, last_page, base_url="https://pro.uptodatefree.ir/Show/", output_dir="text_files"):
    os.makedirs(output_dir, exist_ok=True)
    progress_file_path = os.path.join(output_dir, 'last_processed_page.txt')

    # Check if there's a record of the last processed page and resume from there
    if os.path.exists(progress_file_path):
        with open(progress_file_path, 'r') as file:
            last_processed_page = int(file.read().strip())
            first_page = last_processed_page + 1

    for page_number in range(first_page, last_page + 1):
        url = f"{base_url}{page_number}"
        page_text = scrape_page(url)
        if page_text:
            file_path = os.path.join(output_dir, f'extracted_text_page_{page_number}.txt')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(page_text)
                print(f"Text extracted and saved to {file_path}")

            # Update the last processed page
            with open(progress_file_path, 'w') as file:
                file.write(str(page_number))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape text from a website")
    parser.add_argument("first_page", type=int, help="First page to scrape")
    parser.add_argument("last_page", type=int, help="Last page to scrape")
    args = parser.parse_args()

    write_files(args.first_page, args.last_page)
    
