import os
import re
import requests
import concurrent.futures

def extract_font_urls(css_content):
    pattern = r"@import url\('(https://fonts\.googleapis\.com/css2\?[^']+)'\);"
    return re.findall(pattern, css_content)

def download_font(url, save_dir):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            css_content = response.text
            font_faces = re.findall(r'@font-face\s*{([^}]+)}', css_content)
            for font_face in font_faces:
                font_family = re.search(r"font-family:\s*'([^']+)'", font_face)
                font_style = re.search(r"font-style:\s*(\w+)", font_face)
                font_weight = re.search(r"font-weight:\s*(\w+)", font_face)
                font_display = re.search(r"font-display:\s*(\w+)", font_face)
                src_url = re.search(r"src:\s*url\(([^)]+)\)", font_face)
                
                if font_family and font_style and font_weight and src_url:
                    font_url = src_url.group(1)
                    font_response = requests.get(font_url)
                    if font_response.status_code == 200:
                        filename = f"{font_family.group(1)}_{font_style.group(1)}_{font_weight.group(1)}.ttf"
                        filename = filename.replace(' ', '_')
                        save_path = os.path.join(save_dir, filename)
                        with open(save_path, 'wb') as f:
                            f.write(font_response.content)
                        print(f"Downloaded Successfully: {filename}")
                    else:
                        print(f"Download Failed: {font_url}")
                else:
                    print(f"Failed to Parse Font Information")
        else:
            print(f"Failed to Get CSS: {url}")
    except Exception as e:
        print(f"Error Processing {url}: {str(e)}")

def main():
    css_file_path = 'fonts.css'
    save_dir = 'fonts/'
    os.makedirs(save_dir, exist_ok=True)

    with open(css_file_path, 'r', encoding='utf-8') as file:
        css_content = file.read()

    font_urls = extract_font_urls(css_content)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_font, url, save_dir) for url in font_urls]
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()