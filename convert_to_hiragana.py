from pykakasi import kakasi


def convertToHiragana(word: str) -> str:
    kks = kakasi()
    result = kks.convert(word)
    converted = "".join([item["hira"] for item in result])
    return converted
