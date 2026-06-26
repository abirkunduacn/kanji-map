def n(char, label, *children):
    return {"char": char, "label": label, "children": list(children)}

def root(id, root_char, label, *children):
    return {"id": id, "root": root_char, "label": label, "children": list(children)}

# Transcribed from 9 source screenshots of JLPT N4 Kanji Mind Map (kanji80s.com).
# Accuracy policy: omit any node whose kanji or label could not be read confidently.
ROOTS = [
    # Page 1 – 十/一 cluster (One / Ten)
    root("ichi-juu", "十", "One / Ten",
        n("生", "life",
            n("売", "to sell"),
            n("産", "give birth")),
        n("士", "scholar",
            n("売", "to sell"),
            n("仕", "attend, serve")),
        n("声", "voice"),
        n("王", "king",
            n("主", "master",
                n("住", "reside"),
                n("注", "concentrate"))),
        n("土", "soil"),
        n("赤", "red",
            n("教", "teach")),
        n("老", "old",
            n("者", "someone",
                n("都", "metropolis"),
                n("暑", "hot"),
                n("考", "to think")))),

    # Page 2 – 代 cluster (Replace / period / lend)
    root("dai", "代", "Replace, period",
        n("射", "shoot"),
        n("式", "ceremony"),
        n("貸", "lend",
            n("試", "test, try, experiment")),
        n("世", "twenty, world, generation",
            n("引", "pull"))),

    # Page 3 – 人 cluster (Person)
    root("hito", "人", "Person",
        n("集", "gather",
            n("進", "advance, proceed")),
        n("会", "to assemble",
            n("合", "fit",
                n("答", "solution, answer"))),
        n("介", "between",
            n("界", "world, boundary")),
        n("験", "verification, effect, testing"),
        n("以", "by means of"),
        n("金", "gold",
            n("銀", "silver")),
        n("今", "now"),
        n("短", "short-tailed bird")),

    # Page 4 – 口 cluster (Mouth)
    root("kuchi", "口", "Mouth",
        n("日", "sun, day",
            n("車", "car"),
            n("軍", "army",
                n("運", "carry")),
            n("音", "sound",
                n("暗", "darkness"),
                n("意", "idea")),
            n("早", "early",
                n("草", "grass")),
            n("朝", "morning"),
            n("昼", "daytime")),
        n("目", "eye",
            n("見", "see"),
            n("顔", "face, expression"),
            n("夏", "summer"),
            n("真", "true, reality"))),

    # Page 5 – 女 cluster (Woman)
    root("onna", "女", "Woman",
        n("安", "cheap"),
        n("好", "fond, pleasing"),
        n("毎", "every",
            n("海", "sea, ocean")),
        n("妹", "younger sister"),
        n("母", "mother",
            n("每", "every")),
        n("姉", "elder sister")),

    # Page 6 – 力 cluster (Power)
    root("chikara", "力", "Power",
        n("地", "ground"),
        n("池", "pond"),
        n("業", "occupation, business"),
        n("勉", "diligence"),
        n("動", "move"),
        n("働", "work")),

    # Page 6 – 乙/也 cluster (private, table, wind etc.)
    root("otsu", "乙", "Second",
        n("机", "table"),
        n("風", "wind"),
        n("服", "clothing"),
        n("飛", "fly"),
        n("広", "wide, broad, spacious",
            n("台", "pedestal",
                n("始", "commence, begin"))),
        n("去", "gone, past",
            n("屋", "roof, house, shop, seller",
                n("室", "room, chamber"))),
        n("雲", "cloud",
            n("転", "revolve, turn around"))),

    # Page 7 – 門 cluster (Gate)
    root("mon", "門", "Gate",
        n("問", "question, ask, problem"),
        n("間", "between",
            n("聞", "hear, listen"),
            n("簡", "simple"))),

    # Page 7 – 月 cluster (Moon / month)
    root("tsuki", "月", "Month, moon",
        n("明", "bright, light"),
        n("有", "possess, have, exist"),
        n("字", "character"),
        n("完", "complete"),
        n("野", "plains, field"),
        n("町", "town"),
        n("歌", "song, sing"),
        n("持", "hold, have")),

    # Page 8 – 宀 cluster (Roof)
    root("ukanmuri", "宀", "Roof",
        n("家", "house, family, expert"),
        n("室", "room"),
        n("寒", "cold"),
        n("安", "cheap"),
        n("宿", "inn, lodging")),

    # Page 8 – 尸 cluster (Corpse / door)
    root("shikabane", "尸", "Corpse",
        n("所", "place"),
        n("区", "district"),
        n("図", "map, drawing, plan"),
        n("文", "sentence, literature, art"),
        n("冬", "winter"),
        n("終", "end, finish")),

    # Page 9 – 厂 / 一 extended (One extended, above/below)
    root("one-ext", "一", "One",
        n("上", "above, up"),
        n("下", "below"),
        n("近", "near"),
        n("元", "origin"),
        n("正", "correct, justice, righteous",
            n("夫", "husband, man"),
            n("乾", "dry"),
            n("中", "China")),
        n("廿", "twenty"),
        n("工", "construction")),

    # Page 9 – 厂 cluster (Cliff)
    root("gake", "厂", "Cliff",
        n("厚", "plump, thick"),
        n("原", "plain, original"),
        n("質", "substance"),
        n("考", "to think"),
        n("与", "give, award")),

    # Page 10 – 大 cluster (Large / person)
    root("dai-hito", "大", "Large",
        n("天", "heavens, sky, imperial"),
        n("央", "center, middle"),
        n("英", "outstanding"),
        n("映", "reflect"),
        n("矢", "arrow",
            n("短", "short"),
            n("族", "family"),
            n("医", "medical"),
            n("知", "to know")),
        n("犬", "dog")),

    # Page 10 – 羽 cluster (Feather)
    root("hane", "羽", "Feather",
        n("習", "learn"),
        n("雉", "pheasant"),
        n("曜", "weekday")),

    # Page 10 – 良 cluster (Good)
    root("yoi", "良", "Good",
        n("食", "eat, meal, rice"),
        n("飲", "drink")),

    # Page 11 – 元 cluster (Origin / Departure)
    root("moto", "元", "Origin",
        n("完", "complete"),
        n("院", "institution"),
        n("光", "light"),
        n("丘", "mound"),
        n("洗", "wash"),
        n("原", "plain"),
        n("兄", "elder brother"),
        n("換", "exchange"),
        n("説", "explanation"),
        n("易", "easy"),
        n("明", "bright"),
        n("場", "location, place"),
        n("題", "thing"),
        n("聞", "hear"),
        n("開", "open"),
        n("勉", "polish, study")),

    # Page 11 – 女 cluster extended (Woman – long kimono / fur)
    root("onna-ext", "女", "Woman (extended)",
        n("着", "wear, arrive"),
        n("長", "long kimono"),
        n("妹", "younger sister"),
        n("好", "fond, pleasing, like something"),
        n("母", "mother"),
        n("毎", "do not",
            n("海", "sea, ocean")),
        n("民", "people, nation, subjects")),

    # Page 12 – 三/春 cluster (Three / Spring)
    root("san-haru", "三", "Three",
        n("春", "spring"),
        n("青", "blue, young",
            n("清", "clear"),
            n("静", "quiet")),
        n("白", "white"),
        n("作", "make"),
        n("斤", "axe"),
        n("不", "negative, non-"),
        n("与", "give, award",
            n("写", "copy, describe"))),

    # Page 12 – 又 cluster (Again)
    root("mata", "又", "Again",
        n("取", "take"),
        n("最", "most"),
        n("受", "receive"),
        n("授", "grant"),
        n("弱", "weak"),
        n("弓", "bow (archery)")),

    # Page 13 – 止 cluster (Stop / foot steps)
    root("tomeru", "止", "Stop",
        n("歩", "walk",
            n("渉", "ford")),
        n("正", "correct, justice",
            n("政", "government, politics")),
        n("走", "run"),
        n("起", "wake up, get up"),
        n("題", "topic")),

    # Page 13 – 長 cluster (Length / Na)
    root("naga", "長", "Length",
        n("帳", "notebook"),
        n("張", "stretch"),
        n("使", "to use"),
        n("便", "convenience"),
        n("官", "official"),
        n("史", "history")),

    # Page 14 – 日 cluster extended (Sun / day – full)
    root("hi-full", "日", "Sun, day (full)",
        n("早", "early, fast",
            n("草", "grass")),
        n("朝", "morning"),
        n("昼", "daytime"),
        n("曜", "weekday"),
        n("昨", "yesterday"),
        n("明", "bright")),

    # Page 14 – 口 cluster (Mouth – full)
    root("kuchi-full", "口", "Mouth (full)",
        n("目", "eye",
            n("見", "see"),
            n("顔", "face, expression"),
            n("夏", "summer"),
            n("真", "true, reality")),
        n("首", "neck, head"),
        n("員", "employee, member"),
        n("貝", "shellfish")),

    # Page 15 – 力 cluster (Power – full)
    root("chikara-full", "力", "Power (full)",
        n("功", "achievement"),
        n("加", "add"),
        n("助", "help"),
        n("勤", "diligent, work"),
        n("勝", "win"),
        n("働", "work")),

    # Page 15 – 厶 cluster (Private / triangle)
    root("mu", "厶", "Private",
        n("公", "public"),
        n("私", "private, I/me"),
        n("去", "go away, past"),
        n("台", "pedestal",
            n("始", "commence, begin")),
        n("雲", "cloud",
            n("転", "revolve")),
        n("屋", "roof, house, seller"),
        n("室", "room")),

    # Page 16 – 門 cluster (Gate – full)
    root("mon-full", "門", "Gate (full)",
        n("間", "between, among",
            n("聞", "hear"),
            n("簡", "simple")),
        n("問", "question"),
        n("閉", "close"),
        n("関", "barrier, connection")),

    # Page 16 – 月 cluster (Moon – full)
    root("tsuki-full", "月", "Month, moon (full)",
        n("朝", "morning"),
        n("服", "clothing"),
        n("肉", "meat"),
        n("有", "exist"),
        n("明", "bright"),
        n("用", "use")),

    # Page 17 – 宀 cluster (Roof – house related)
    root("ukanmuri-full", "宀", "Roof (full)",
        n("写", "copy"),
        n("完", "complete"),
        n("実", "reality, truth"),
        n("安", "cheap"),
        n("家", "house, family"),
        n("室", "room"),
        n("寒", "cold"),
        n("宿", "inn, lodging"),
        n("守", "guard, protect")),

    # Page 17 – 八 cluster (Eight)
    root("hachi", "八", "Eight",
        n("冷", "cold"),
        n("分", "divide, minute")),

    # Page 18 – 尚 cluster (Still / road with walls)
    root("sho", "尚", "Still",
        n("通", "road, pass through"),
        n("週", "week")),

    # Page 18 – 子 cluster (Child / character)
    root("ko", "子", "Child",
        n("字", "character"),
        n("学", "study"),
        n("野", "plains, field"),
        n("完", "complete"),
        n("町", "town")),

    # Page 19 – 口 cluster (Mouth – capital related)
    root("kuchi-capital", "口", "Mouth (capital)",
        n("品", "goods"),
        n("回", "times, round, counter"),
        n("国", "country"),
        n("図", "map, plan")),

    # Page 19 – YO cluster
    root("yo", "与", "Give",
        n("急", "hurry"),
        n("筆", "brush"),
        n("書", "write"),
        n("昔", "former times")),

    # Page 20 – 分 cluster (Separate / diverge)
    root("waka", "分", "Separate",
        n("悪", "bad, evil, wrong"),
        n("品", "goods"),
        n("首", "neck"),
        n("言", "say",
            n("計", "plan, scheme, measure",
                n("政", "government"),
                n("建", "building"))),
        n("使", "to use")),
]

def _walk(nodes):
    for node in nodes:
        yield node["char"]
        yield from _walk(node["children"])

def placed_kanji() -> set[str]:
    out = set()
    for r in ROOTS:
        out.update(_walk(r["children"]))
    return out
