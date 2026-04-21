import requests
import datetime
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def get_google_ads():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=ko-KR')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    ads_report = []

    try:
        print("[CRAWL] 구글 검색 시작")
        driver.get("https://www.google.co.kr/search?q=솔라온케어&hl=ko&gl=kr")
        time.sleep(5)
        driver.save_screenshot("google_search.png")

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # ✅ '광고: 검색 결과' span 찾기
        start_span = soup.find("span", class_="L8u9l")
        # ✅ '광고: 검색 결과 숨기기' span 찾기
        end_span = soup.find("span", class_="iInZTe")

        print(f"[CRAWL] 시작 span: {start_span}")
        print(f"[CRAWL] 끝 span: {end_span}")

        if start_span and end_span:
            # 두 span의 공통 부모 찾기
            # start_span에서 위로 올라가면서 광고 블록 컨테이너 찾기
            ad_container = start_span.find_parent("div", recursive=True)

            # 컨테이너 안에서 heading role 가진 요소들 추출
            headings = []
            if ad_container:
                for el in ad_container.find_all(attrs={"role": "heading"}):
                    text = el.get_text().strip()
                    if text and "광고" not in text:
                        headings.append(text)

            print(f"[CRAWL] 찾은 제목들: {headings}")

            if headings:
                for i, title in enumerate(headings, 1):
                    print(f"[CRAWL] 구글 SA 순번 {i}. {title}")
                    ads_report.append(f"구글 SA 순번 {i}. {title}")
            else:
                ads_report.append("검색 광고 없음")
        else:
            # ✅ span을 못 찾으면 페이지 소스 일부 출력해서 확인
            print("[CRAWL] 광고 span 못 찾음")
            print(f"[CRAWL] 페이지 소스 일부: {driver.page_source[:3000]}")
            ads_report.append("검색 광고 없음")

    except Exception as e:
        print(f"[CRAWL] 오류: {e}")
        ads_report.append(f"크롤링 오류: {str(e)[:100]}")

    finally:
        driver.quit()

    return ads_report


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
    ads = get_google_ads()

    total_ads = [a for a in ads if "없음" not in a and "오류" not in a]
    summary = f"총 {len(total_ads)}개 광고 감지" if total_ads else "광고 없음"
    detail = "\n".join(ads)

    print(f"\n[결과 요약] {summary}")
    print(f"[상세 리포트]\n{detail}")

    send_to_google_form(summary, detail)


if __name__ == "__main__":
    run()
