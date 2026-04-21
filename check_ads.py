import requests
import datetime
import os


def get_google_ads(api_key):
    print("[SERP] 구글 광고 검색 시작")
    try:
        response = requests.get(
            "https://api.valueserp.com/search",
            params={
                "api_key": api_key,
                "q": "솔라온케어",
                "location": "Seoul,South Korea",
                "google_domain": "google.co.kr",
                "gl": "kr",
                "hl": "ko",
                "ads_optimized": "true",
            },
            timeout=30
        )
        results = response.json()

        # ✅ 모든 키와 값 출력
        print(f"[SERP] 전체 키: {list(results.keys())}")
        for key in results.keys():
            if key not in ["organic_results", "search_parameters", "search_metadata", "request_info", "pagination", "serpapi_pagination"]:
                print(f"[SERP] '{key}' 데이터: {results.get(key)}")

        return ["디버깅 중"]

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
        "entry.1911817445": "디버깅",
        "entry.64048030": "디버깅 중",
    }
    requests.post(form_url, data=payload, timeout=10)


def run():
    api_key = os.environ.get('VALUESERP_KEY')
    ads = get_google_ads(api_key)
    print(f"\n[결과]\n{ads}")


if __name__ == "__main__":
    run()
