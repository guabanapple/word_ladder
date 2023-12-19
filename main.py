import random
import pandas as pd
import scraping

user_inputs = {"start": "", "end": "", "times": 0}
questions = {
    "start": "最初の単語を【ひらがな】で入力してください。なお最後が「ん」で終わらないものとする。",
    "end": "最後の単語を【ひらがな】で入力してください。",
    "times": "しりとり回数を入力してください。（1 <= n <= 10)",
}


def is_valid_input(user_input: str, key: str) -> bool:
    if key in ["start", "end"]:
        # if only space or empty
        if user_input.isspace() or len(user_input) == 0:
            return True
        # is hiragana
        if not scraping.is_hiragana(user_input):
            return True
    elif key == "times":
        # if only space or empty
        if user_input.isspace() or len(user_input) == 0:
            return True
        # is 1 <= n <= 10
        if user_input.isdigit():
            if not 1 <= int(user_input) <= 10:
                return True
        else:
            return True
    if key == "start" and user_input[-1] == "ん":
        return True


def get_user_input() -> None:
    """入力を要求し,有効な値であればuser_inputsに格納"""
    for key in user_inputs.keys():
        while True:
            user_input = input(questions[key])
            if is_valid_input(user_input, key):
                print(f"{key}: 入力値が無効です。再度入力してください。")
            else:
                user_inputs[key] = user_input
                break
    user_inputs["times"] = int(user_inputs["times"])


def get_suitable_word(vocabulary, head: str, tail: str) -> str:
    """headから始まりtailで終わる単語を出力する

    Args:
        vocabulary(DataFrame): スクレイピングで得た単語リスト
        head(str): 単語の頭文字
        tail(str): 単語の末尾
    Returns:
        words.iloc[r] (str): 単語
        raise(Error): 該当する単語が見つからない場合
    """
    regex = f"^.*{tail}$"
    char_series = vocabulary.loc[head, :]
    try:
        words = char_series[char_series.str.match(regex, na=False)]
        r = random.randrange(len(words))
        return words.iloc[r]
    except (IndexError, KeyError, ValueError):
        raise


def to_upper_and_normalize_case(char: str):
    """小文字を大文字に、濁音・半濁音を対応する50音に変換する

    Args:
        char(str): 1文字
    Returns:
        char.translate(filter) (str): 変換後の1文字
    """
    from_translate = "ぁぃぅぇぉっゃゅょがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ"
    to_translate = "あいうえおつやゆよかきくけこさしすせそたちつてとはひふへほはひふへほ"
    filter = char.maketrans(from_translate, to_translate)
    return char.translate(filter)


def get_last_char(word: str) -> str:
    """wordの最後1文字を出力
    最後1文字が伸ばし棒（ー）の場合、その1つ手前の音を出力する

    Returns:
        to_upper_and_normalize_case(word[-n]) (str): ひらがな1文字
    """
    if word[-1] == "ー":
        return to_upper_and_normalize_case(word[-2])
    else:
        return to_upper_and_normalize_case(word[-1])


def make_ladder(vocabulary):
    """get_sutable_word()から得た単語を繋いでいく

    ユーザー入力で指定された回数(times)が1でない場合、該当する単語がなくエラーとなる可能性がある。
    """
    char_s = get_last_char(user_inputs["start"])
    start_last_char = to_upper_and_normalize_case(char_s)
    end_first_char = to_upper_and_normalize_case(user_inputs["end"][0])
    result = []
    times = user_inputs["times"]

    if times == 1:
        try:
            result.insert(
                -1, get_suitable_word(vocabulary, start_last_char, end_first_char)
            )
        except (IndexError, KeyError):
            print("再度別の単語で試してください。")
            exit()
        else:
            return result

    while True:
        tail = ""
        if len(result) == 0:
            # 1回目
            head = start_last_char
        elif len(result) == times - 1:
            # ラスト1回
            tail = end_first_char
            char = get_last_char(word)
            head = to_upper_and_normalize_case(char)
        else:
            char = get_last_char(word)
            head = to_upper_and_normalize_case(char)

        try:
            word = get_suitable_word(vocabulary, head, tail)
        except (IndexError, KeyError, ValueError) as e:
            print("申し訳ありません。私の語彙では厳しいようです...")
            exit()
        else:
            result.append(word)
            print(head, word)
            if len(result) == times:
                break


def main():
    try:
        vocabulary = scraping.get_vocabulary()
    except:
        vocabulary = pd.read_excel("vocabulary.xlsx", index_col=0, header=0)

    get_user_input()
    print(f"スタート： {user_inputs['start']}")
    make_ladder(vocabulary)
    print(f"ゴール： {user_inputs['end']}")


if __name__ == "__main__":
    main()
