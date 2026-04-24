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
                "q": "운동화",
                "location": "Seoul,South Korea",
                "google_domain": "google.co.kr",
                "gl": "kr",
                "hl": "ko",
                "ads_optimized": "true",
            },
            timeout=30
        )
        results = response.json()

        all_ads = results.get("ads", []) + results.get("bottom_ads", [])
        ads_report = []

        if all_ads:
            # 상단 광고 우선, 없으면 하단
            top_ads = [a for a in all_ads if a.get("relative_block_position") == "top"]
            bottom_ads = [a for a in all_ads if a.get("relative_block_position") == "bottom"]
            final_ads = top_ads if top_ads else bottom_ads

            for i, ad in enumerate(final_ads, 1):
                title = ad.get("title", "제목없음")
                display_url = ad.get("displayed_link", "")
                print(f"[SERP] 구글 SA 순번 {i}. {title}")
                ads_report.append(f"구글 SA 순번 {i}. {title} ({display_url})")
        else:
            print("[SERP] 광고 없음")
            ads_report.append("검색 광고 없음")

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
    api_key = os.environ.get('VALUESERP_KEY')
    ads = get_google_ads(api_key)

    total_ads = [a for a in ads if "없음" not in a and "오류" not in a and "실패" not in a]
    summary = f"총 {len(total_ads)}개 광고 감지" if total_ads else "광고 없음"
    detail = "\n".join(ads)

    print(f"\n[결과 요약] {summary}")
    print(f"[상세 리포트]\n{detail}")

    send_to_google_form(summary, detail)


if __name__ == "__main__":
    run()
