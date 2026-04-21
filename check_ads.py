import requests
import datetime
import os
from serpapi import GoogleSearch
from bs4 import BeautifulSoup


def get_google_ads(serpapi_key):
    print("[SERP] 구글 광고 검색 시작")
    try:
        search = GoogleSearch({
            "q": "솔라온케어",
            "hl": "ko",
            "gl": "kr",
            "location": "Seoul, South Korea",
            "google_domain": "google.co.kr",
            "no_cache": "true",
            "api_key": serpapi_key
        })
        results = search.get_dict()

        print(f"[SERP] 검색 ID: {results.get('search_metadata', {}).get('id', '')}")

        # ✅ HTML 파일 직접 가져와서 파싱
        html_url = results.get("search_metadata", {}).get("raw_html_file", "")
        print(f"[SERP] HTML URL: {html_url}")

        ads_report = []

        if html_url:
            html_res = requests.get(html_url, timeout=10)
            soup = BeautifulSoup(html_res.text, "html.parser")

            # 광고 블록 찾기 — '광고: 검색 결과' 텍스트 기준
            ad_titles = []

            # 방법 1: data-text-ad 속성
            for el in soup.find_all(attrs={"data-text-ad": True}):
                title_el = el.find("div", {"role": "heading"})
                if title_el:
                    ad_titles.append(title_el.get_text().strip())

            # 방법 2: aria-label에 광고 포함
            if not ad_titles:
                for el in soup.select("div[aria-label*='광고']"):
                    h3 = el.find("h3")
                    if h3:
                        ad_titles.append(h3.get_text().strip())

            # 방법 3: 클래스명으로
            if not ad_titles:
                for el in soup.select(".uEierd, .d5oMvf, .Krnil"):
                    text = el.get_text().strip()
                    if text:
                        ad_titles.append(text)

            if ad_titles:
                for i, title in enumerate(ad_titles, 1):
                    print(f"[SERP] 구글 SA 순번 {i}. {title}")
                    ads_report.append(f"구글 SA 순번 {i}. {title}")
            else:
                print("[SERP] HTML에서도 광고 못 찾음")
                ads_report.append("검색 광고 없음")
        else:
            ads_report.append("HTML URL 없음")

        return ads_report

    except Exception as e:
        print(f"[SERP] 오류: {e}")
        return [f"광고 조회 실패: {str(e)}"]


def send_to_google_form(status, detail):
    form_url = (
        "https://docs.google.com/forms/d/e/"
        "1FAIpQLSecpFdDiKYEDpvi4P_w94Xc_nku8cBgLR6wH6KEFTYD7Q7TAQ/formResponse"
    )
    payload = {
        "entry.916170448": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "entry.1911817445": status,
        "entry.64048030": detail,
    }
    requests.post(form_url, data=payload, timeout=10)
    print("[FORM] 구글 폼 전송 완료")


def run():
    serpapi_key = os.environ.get('SERPAPI_KEY')
    ads = get_google_ads(serpapi_key)

    total_ads = [a for a in ads if "없음" not in a and "실패" not in a]
    summary = f"총 {len(total_ads)}개 광고 감지" if total_ads else "광고 없음"
    detail = "\n".join(ads)

    print(f"\n[결과 요약] {summary}")
    print(f"[상세 리포트]\n{detail}")

    send_to_google_form(summary, detail)


if __name__ == "__main__":
    run()
