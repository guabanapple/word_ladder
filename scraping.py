from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time
import re
import convert_to_hiragana


def get_driver():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    return driver


# wordが全てひらがな -> return reオブジェクト
def is_hiragana(word):
    re_hiragana = re.compile(r"^[あ-んー]+$")
    is_hira = re_hiragana.fullmatch(word)
    return is_hira


def get_data(driver):
    ul = driver.find_element(By.XPATH, value='//*[@id="mw-pages"]/div/div/div/ul')
    lis = ul.find_elements(By.TAG_NAME, "li")

    # 各データをひらがなに変換し、再リスト化
    data = []
    for item in lis:
        converted = convert_to_hiragana.convertToHiragana(item.text)
        if is_hiragana(converted) is not None and len(converted) != 1:
            data.append(converted)
    return data


def is_invalid_word(word):
    if word[-1] != "ん":
        return True


def next_page(driver):
    try:
        # ”次のページへ”のhrefを取得
        next_page_url = next = driver.find_element(
            By.XPATH, value='//*[@id="mw-pages"]/a[4]'
        ).get_attribute("href")
    except NoSuchElementException as te:
        print("No next page")
        return

    # 次ページにアクセス
    driver.get(next_page_url)
    time.sleep(1)


def get_vocabulary():
    vocabulary = {}
    words50 = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほみむめもやゆよらりるれろわ"
    driver = get_driver()

    for item in words50:
        url = f"https://ja.wiktionary.org/w/index.php?title=カテゴリ:日本語_名詞&from={item}"

        # サイトにアクセス
        try:
            driver.get(url)
            time.sleep(1)
        except NoSuchElementException as n:
            print("データの取得に失敗しました。", n)
            exit()

        data = get_data(driver)
        words = [d for d in data if d[0] == item and is_invalid_word(d[-1])]

        # 追加1ページ分
        for j in range(1):
            # 次のページにアクセス
            next_page(driver)
            words.append(get_data(driver))

        vocabulary[item] = words

    # Driverの終了
    driver.quit()
    return vocabulary


def main():
    vocabulary = get_vocabulary()
    df = pd.DataFrame(vocabulary.values(), index=vocabulary.keys())
    df.to_excel("vocabulary.xlsx")


if __name__ == "__main__":
    main()
