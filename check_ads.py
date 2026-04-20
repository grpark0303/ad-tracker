import requests
import datetime
import os
from serpapi import GoogleSearch


def get_google_ads(serpapi_key):
    """구글 '솔라온케어' 검색 광고 순서 및 제목 추출"""
    print("[SERP] 구글 광고 검색 시작")
    try:
        search = GoogleSearch({
            "q": "솔라온케어",
            "hl": "ko",
            "gl": "kr",
            "location": "Seoul, South Korea",
            "google_domain": "google.co.kr",
            "api_key": serpapi_key
        })
        results = search.get_dict()

        print(f"[SERP] 전체 결과 키: {list(results.keys())}")

        ads_report = []
        top_ads = results.get("ads", [])

        if top_ads:
            for i, ad in enumerate(top_ads, 1):
                title = ad.get("title", "제목없음")
                display_url = ad.get("displayed_link", "")
                print(f"[SERP] {i}위: {title} | {display_url}")
                ads_report.append(f"{i}위: {title} ({display_url})")
        else:
            print("[SERP] 광고 없음")
            print(f"[SERP] 받은 데이터: {results}")
            ads_report.append("검색 광고 없음")

        return ads_report

    except Exception as e:
        print(f"[SERP] 오류: {e}")
        return [f"광고 조회 실패: {str(e)}"]


def send_to_google_form(status, detail):
    form_url = (
        "https://docs.google.com/forms/d/e/"
        "1FAIpQLSe10Qm1wxcGVpREkKD0aDPSVr7CEQN1TVp_HsMkm6zLmcQ/formResponse"
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

    total = len(ads)
    summary = f"총 {total}개 광고 감지"
    detail = "\n".join(ads)

    print(f"\n[결과 요약] {summary}")
    print(f"[상세 리포트]\n{detail}")

    send_to_google_form(summary, detail)


if __name__ == "__main__":
    run()
