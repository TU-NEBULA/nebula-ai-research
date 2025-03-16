import re
import json
from bs4 import BeautifulSoup

def extract_json_from_html(html_file):
    """
    Velog 트렌딩 페이지 HTML에서 블로그 데이터를 포함한 JSON 문자열을 추출하고,
    최종적으로 블로그 데이터 딕셔너리를 반환하는 함수입니다.
    """
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 정규표현식을 수정하여 반드시 [1, "a:..."] 형태의 배열을 캡쳐하도록 함.

    pattern = re.search(
        r'self\.__next_f\.push\(\[1,\"a:(\[.*\{.*\}\])\\n\"\]\)',
        html_content, 
        re.DOTALL
    )

    if not pattern:
        print("❌ 원하는 블로그 데이터를 찾을 수 없습니다. HTML 구조를 확인하세요.")
        return None

    push_data_str = pattern.group(1).replace('\\"', '"')
    push_data_str = push_data_str.replace('\\\\', '\\')
    # print("🔹 추출된 push 데이터:", push_data_str)  
    # print("🔹 추출된 push 타입:", type(push_data_str))  

    
    try:
        # push_data_str는 JSON 형식의 배열이어야 함
        push_data = json.loads(push_data_str)
    except Exception as e:
        print(f"❌ push 데이터 JSON 파싱 실패: {e}")
        return None

    if len(push_data) < 2:
        print("❌ push 데이터 구조가 예상과 다릅니다.")
        return None

    blog_data_str = push_data[-1]

    return push_data[-1]

def extract_blog_links(blog_json):
    """
    추출된 블로그 데이터 딕셔너리에서 블로그 URL을 생성하여 리스트로 반환하는 함수입니다.
    """
    if not blog_json or "data" not in blog_json:
        print("❌ 'data' 키를 찾을 수 없습니다. JSON 구조를 확인하세요.")
        return []

    blog_links = []
    for item in blog_json["data"]:
        username = item["user"]["username"]
        url_slug = item["url_slug"]
        blog_url = f"https://velog.io/@{username}/{url_slug}"
        blog_links.append(blog_url)

    return blog_links

# 실행 예제
if __name__ == "__main__":
    velog_html_file = "velog_trending.html"  # 저장된 HTML 파일 경로
    blog_json = extract_json_from_html(velog_html_file)

    if blog_json:
        links = extract_blog_links(blog_json)
        if links:
            print("✅ 추출된 블로그 링크:")
            for link in links:
                print(link)
        else:
            print("❌ 블로그 링크를 찾을 수 없습니다.")
