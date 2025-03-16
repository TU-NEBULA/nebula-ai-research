import re
import json
import requests

class VelogScraper:
    """
    Velog 트렌딩 페이지에서 블로그 데이터를 추출하는 클래스.
    """

    BASE_URL = "https://velog.io/trending/week"

    def __init__(self, user_agent="Mozilla/5.0"):
        self.headers = {"User-Agent": user_agent}

    def fetch_html(self):
        """
        Velog 트렌딩 페이지의 HTML을 가져오는 함수.
        """
        response = requests.get(self.BASE_URL, headers=self.headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f"❌ 요청 실패! 상태 코드: {response.status_code}")
            return None

    def extract_json_from_html(self, html_content):
        """
        Velog HTML에서 블로그 데이터를 포함한 JSON을 추출하는 함수.
        """
        pattern = re.search(
            r'self\.__next_f\.push\(\[1,\"a:(\[.*\{.*\}\])\\n\"\]\)',
            html_content,
            re.DOTALL
        )

        if not pattern:
            print("❌ 블로그 데이터를 찾을 수 없습니다. HTML 구조를 확인하세요.")
            return None

        push_data_str = pattern.group(1).replace('\\"', '"').replace('\\\\', '\\')

        try:
            push_data = json.loads(push_data_str)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 실패: {e}")
            return None

        if len(push_data) < 2:
            print("❌ JSON 데이터 구조가 예상과 다릅니다.")
            return None

        return push_data[-1]

    def extract_blog_links(self, blog_json):
        """
        JSON 데이터에서 블로그 URL 리스트를 생성하는 함수.
        """
        if not blog_json or "data" not in blog_json:
            print("❌ 'data' 키를 찾을 수 없습니다.")
            return []

        return [
            f"https://velog.io/@{item['user']['username']}/{item['url_slug']}"
            for item in blog_json["data"]
        ]

    def get_trending_links(self):
        """
        Velog 트렌딩 페이지에서 블로그 링크를 가져오는 메인 함수.
        """
        html_content = self.fetch_html()
        if not html_content:
            return []

        blog_json = self.extract_json_from_html(html_content)
        if not blog_json:
            return []

        return self.extract_blog_links(blog_json)


# 실행 예제 (직접 실행할 때만 동작)
if __name__ == "__main__":
    scraper = VelogScraper()
    links = scraper.get_trending_links()

    if links:
        print("\n✅ 추출된 블로그 링크:")
        for link in links:
            print(link)
    else:
        print("❌ 블로그 링크를 찾을 수 없습니다.")
