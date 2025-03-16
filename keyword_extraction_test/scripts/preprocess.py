import requests
from bs4 import BeautifulSoup
import os
import re
from velog_scraper import VelogScraper 


def fetch_html(url):
    """
    주어진 URL에서 HTML 내용을 가져오는 함수.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        print(f"❌ 요청 실패! 상태 코드: {response.status_code}")
        return None


def extract_main_text(html: str) -> str:
    """
    BeautifulSoup을 사용하여 HTML 본문 텍스트를 추출하는 함수.
    """
    soup = BeautifulSoup(html, "lxml")

    # <script>, <style> 태그 제거
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Velog 본문이 있는 태그 탐색
    content_tag = soup.find("div", class_="markdown-body")
    
    if content_tag:
        main_text = content_tag.get_text(separator=" ", strip=True)
    else:
        main_text = ""

    # 불필요한 공백 및 특수 문자 정리
    main_text = re.sub(r"[^\w\s]", "", main_text)  # 특수 문자 제거
    main_text = re.sub(r"\s+", " ", main_text).strip()  # 중복 공백 제거

    return main_text


def process_velog_articles():
    """
    Velog 트렌딩 페이지에서 모든 블로그를 가져와 본문을 추출하고 저장하는 함수.
    """
    # VelogScraper를 이용해 트렌딩 블로그 링크 가져오기
    scraper = VelogScraper()
    article_links = scraper.get_trending_links()

    if not article_links:
        print("❌ 블로그 링크를 찾을 수 없습니다.")
        return

    print(f"✅ 총 {len(article_links)}개의 블로그를 가져왔습니다.")

    # 폴더 생성
    raw_html_dir = "data/raw_html"
    processed_text_dir = "data/processed_text"
    os.makedirs(raw_html_dir, exist_ok=True)
    os.makedirs(processed_text_dir, exist_ok=True)

    for i, link in enumerate(article_links, start=1):
        print(f"📌 {i}/{len(article_links)} 블로그 크롤링 중: {link}")
        
        html_content = fetch_html(link)
        if not html_content:
            continue

        # HTML 저장 (원본 데이터 보관)
        raw_html_path = os.path.join(raw_html_dir, f"blog_{i}.html")
        with open(raw_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 본문 추출 & 전처리
        processed_text = extract_main_text(html_content)

        # 텍스트 저장
        processed_text_path = os.path.join(processed_text_dir, f"blog_{i}.txt")
        with open(processed_text_path, "w", encoding="utf-8") as f:
            f.write(processed_text)

        print(f"✅ 본문 저장 완료: {processed_text_path}")


# 실행 예제
if __name__ == "__main__":
    process_velog_articles()
