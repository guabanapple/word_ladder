from pykakasi import kakasi


# ひらがなにしてreturn
# 引数：変換したい単語
def convertToHiragana(word):
    kks = kakasi()
    result = kks.convert(word)
    converted = "".join([item["hira"] for item in result])
    return converted
