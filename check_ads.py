import requests
import datetime
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


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

        # '광고: 검색 결과' 텍스트 기준으로 광고 블록 찾기
        page_source = driver.page_source

        # 광고 영역의 제목 추출
        # 구글 광고는 span[aria-label] 또는 특정 클래스로 구분
        ad_blocks = driver.find_elements(
            By.XPATH,
            "//span[contains(text(),'광고') and contains(text(),'검색 결과')]"
            "/ancestor::div[3]//div[@role='heading'] | "
            "//div[contains(@aria-label,'광고')]//div[@role='heading']"
        )

        if not ad_blocks:
            # 방법 2: 광고 레이블 찾고 그 근처 제목 추출
            ad_labels = driver.find_elements(
                By.XPATH, "//span[contains(text(),'광고: 검색 결과')]"
            )
            print(f"[CRAWL] 광고 레이블 수: {len(ad_labels)}")

            for label in ad_labels:
                try:
                    # 부모 컨테이너에서 heading 찾기
                    container = label.find_element(By.XPATH, "./ancestor::div[5]")
                    headings = container.find_elements(
                        By.XPATH, ".//div[@role='heading']"
                    )
                    for h in headings:
                        text = h.text.strip()
                        if text and "광고" not in text:
                            ad_blocks.append(h)
                except Exception as e:
                    print(f"[CRAWL] 레이블 처리 오류: {e}")

        if ad_blocks:
            seen = []
            for el in ad_blocks:
                text = el.text.strip()
                if text and text not in seen:
                    seen.append(text)

            for i, title in enumerate(seen, 1):
                print(f"[CRAWL] 구글 SA 순번 {i}. {title}")
                ads_report.append(f"구글 SA 순번 {i}. {title}")
        else:
            print("[CRAWL] 광고 없음")
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
