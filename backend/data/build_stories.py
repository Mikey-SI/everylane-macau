# -*- coding: utf-8 -*-
"""Write five-language Ah-Hou stories for every POI, then copy to frontend."""
from __future__ import annotations

import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LANGS = ("zh-HK", "zh", "en", "pt", "ja")


def S(yue: str, hans: str, en: str, pt: str, ja: str) -> dict:
    return {"zh-HK": yue.strip(), "zh": hans.strip(), "en": en.strip(), "pt": pt.strip(), "ja": ja.strip()}


# Existing seven Cantonese tales are kept verbatim.
STORIES = {
    "ruins_st_paul": S(
        "呢座『三巴』其實係聖保祿學院教堂嘅前壁，1835年一場大火燒淨剩塊石牌坊。你抬頭望，最頂係銅鴿代表聖神，再落啲有耶穌、聖母，仲有牡丹同菊花——係當年中國工匠落嘅手影，中西合璧，全世界獨一無二。",
        "这座“三巴”其实是圣保禄学院教堂的前壁，1835年一场大火只留下这块石牌坊。你抬头看：最顶是铜鸽代表圣神，往下有耶稣、圣母，还有牡丹和菊花——是当年中国工匠留下的手笔，中西合璧，世上独一份。",
        "This ‘façade’ is all that remains of the Church of St. Paul’s College after the 1835 fire. Look up: a copper dove, then Jesus and Mary, then peonies and chrysanthemums carved by Chinese craftsmen. East meets West, and nowhere else looks quite like it.",
        "Esta ‘fachada’ é o que restou da igreja do Colégio de São Paulo após o incêndio de 1835. Olha para cima: a pomba, Jesus e Maria, e ainda peónias e crisântemos talhados por artesãos chineses. Oriente e Ocidente, só aqui.",
        "この「三巴」は聖パウロ学院教会の正面だけで、1835年の大火のあと石のファサードが残りました。一番上の鳩、イエスとマリア、そして牡丹や菊は中国の職人が彫ったもので、東西が重なる景色はここだけです。",
    ),
    "a_ma_temple": S(
        "話說當年葡萄牙人喺呢度上岸，問本地人呢度叫咩，街坊以為佢問緊間廟，答『媽閣』(Maa-Gok)，葡人聽落變咗『Macau』——成個城市嘅名就係咁嚟。",
        "当年葡萄牙人在这里上岸，问本地人这地方叫什么。街坊以为在问这座庙，答“妈阁”（Maa-Gok），葡人听成了 Macau——整座城市的名字就是这样来的。",
        "When the Portuguese came ashore here they asked the name of the place. Locals thought they meant this temple and said ‘Maa-Gok’. That became Macau — the whole city’s name started at this door.",
        "Quando os portugueses desembarcaram, perguntaram o nome do sítio. Os vizinhos pensaram que falavam do templo e disseram ‘Maa-Gok’. Assim nasceu o nome Macau, à porta desta casa.",
        "ポルトガル人がここで上陸し、土地の名を尋ねました。街の人は廟のことだと思い「媽閣（マーゴク）」と答え、それが Macau になった。街の名前は、この門から始まったんです。",
    ),
    "lilau_square": S(
        "有句葡文老話：『飲過亞婆井水，忘唔到澳門』。以前呢度係城裡最重要嘅水井，葡萄牙人就喺周圍起屋定居，所以你會見到好濃嘅南歐味。",
        "有句葡文老话：“喝过亚婆井的水，就忘不了澳门。”从前这里是城里最重要的水井，葡萄牙人围着井边盖屋定居，所以南欧味道特别浓。",
        "An old Portuguese saying goes: drink from Lilau’s spring, and you never forget Macau. This was the city’s most important well; people built homes around it, which is why the square still feels so southern European.",
        "Diz o ditado: quem bebe a água do Lilau não esquece Macau. Era o poço mais importante da cidade; à volta nasceram casas, e por isso o largo ainda tem um ar tão mediterrânico.",
        "古いポルトガルの言い伝えに「亜婆井の水を飲めば、マカオを忘れない」とあります。かつての大切な井戸のまわりに家が建ち、今も南欧の空気が残っています。",
    ),
    "mandarin_house": S(
        "呢度係《盛世危言》作者鄭觀應住過嘅大屋，據講孫中山先生都嚟過。成個大宅有六十幾間房，中式天井加上西式百葉窗，行入去好似穿越返清末。",
        "这里是《盛世危言》作者郑观应住过的大宅，听说孙中山先生也来过。整座宅子六十多间房，中式天井配西式百叶窗，走进去像回到清末。",
        "Zheng Guanying, who wrote Words of Warning in a Prosperous Age, lived here — and Sun Yat-sen is said to have visited. Sixty-odd rooms, a Chinese courtyard and Western shutters: step inside and the late Qing still feels close.",
        "Zheng Guanying, autor de Palavras de Alerta numa Era Próspera, viveu aqui; diz-se que Sun Yat-sen também veio. Mais de sessenta salas, pátio chinês e persianas ocidentais: é quase um salto ao fim da dinastia Qing.",
        "『盛世危言』の鄭観応が住んだ屋敷で、孫文も訪れたと言われます。六十余りの部屋、中庭と西洋のブラインド。一歩入ると清末に戻ったようです。",
    ),
    "rua_felicidade": S(
        "福隆新街喺清末民初係澳門最旺嘅『花街』，兩邊全部酒樓茶館。你而家見到嘅紅色木窗花，就係當年青樓嘅痕跡。後尾洗盡鉛華，變咗手信街，但係嗰種舊澳門嘅味道一直都喺度。",
        "福隆新街在清末民初是澳门最旺的“花街”，两边都是酒楼茶馆。你现在看见的红色木窗花，就是当年青楼留下的痕迹。后来洗尽铅华，成了手信街，可那种旧澳门的味道一直还在。",
        "In the late Qing this was Macau’s busiest pleasure street, lined with tea houses. The red wooden shutters are that era’s leftover. It later became a souvenir lane, but the old-town perfume never quite left.",
        "No fim do Império Qing era a rua mais animada de Macau, cheia de casas de chá. As janelas vermelhas são essa memória. Depois tornou-se rua de lembranças, mas o cheiro da Macau antiga ficou.",
        "清末民初、ここは澳門でいちばん賑やかな花街で、両側が茶楼でした。赤い木の窓はその名残。いまは手土産通りですが、古いマカオの匂いは残っています。",
    ),
    "rua_cinco": S(
        "十月初五街個名，係紀念葡萄牙建立共和國嗰日。呢條街以前係內港最旺嘅商業街，𠵇家仲有好多幾十年嘅老舖——梁慶記、成記粥、咸蝦燦……行落去就好似翻返轉頭幾十年前嘅澳門。",
        "十月初五街这个名字，是纪念葡萄牙成立共和国的日子。以前是内港最旺的商业街，现在还有好多几十年的老店——梁庆记、成记粥、咸虾灿……走下去就像翻回几十年前的澳门。",
        "The street is named for the day Portugal became a republic. It was the Inner Harbour’s busiest shopping lane; old names like Leong Heng Kei and Seng Kei congee are still here. Walk it and the Macau of decades ago walks with you.",
        "O nome assinala o dia da República Portuguesa. Foi a rua comercial mais viva do Porto Interior; lojas com décadas — Leong Heng Kei, papas Seng Kei, haam haa chaan — ainda estão. Caminhar aqui é voltar uns decénios atrás.",
        "通りの名はポルトガル共和国の記念日。内港いちばんの商店街で、梁慶記や成記粥、咸蝦燦など何十年ものの店が残っています。歩くと、数十年前の澳門に戻ったようです。",
    ),
    "rua_estalagens": S(
        "草堆街80號，係孫中山先生 1892 年喺澳門開嘅『中西藥局』舊址。佢當年一邊行醫一邊講革命。成條街以前係賣藥材同開客棧嘅，𠵇家仲有古玩舖，好多本地人都未必行勻。",
        "草堆街80号，是孙中山先生1892年在澳门开的“中西药局”旧址。他当年一边行医一边讲革命。整条街从前卖药材、开客栈，现在还有古玩铺，连很多本地人都不一定走遍。",
        "Number 80 is where Sun Yat-sen opened his Chinese-Western pharmacy in 1892, practising medicine by day and talking revolution by night. The street once sold herbs and ran inns; antique shops remain, and even locals have not walked every door.",
        "O 80 é a antiga farmácia sino-ocidental de Sun Yat-sen, 1892: de dia médico, de noite revolucionário. A rua vendia ervas e tinha estalagens; ainda há antiquários, e nem todos os macaenses a conhecem ao pormenor.",
        "80番地は、孫文が1892年に開いた中西薬局の跡。昼は診療、夜は革命の話。かつては薬種と宿の通りで、今も古物商があり、地元の人でも歩き尽くしていないかもしれません。",
    ),
    "camoes_garden": S(
        "白鴿巢公園係澳門人晨運嘅地方，大榕樹底下落棋吹水，旁邊白色嘅東方基金會好似歐洲別墅。你慢慢行，會聽到好地道嘅澳門節奏。",
        "白鸽巢公园是澳门人晨运的地方，大榕树底下下棋闲聊，旁边白色的东方基金会像一座欧洲别墅。你慢慢走，就能听见很地道的澳门节奏。",
        "Camões Garden is where Macau stretches in the morning: chess under the banyans, gossip in the shade, and the white Casa Garden villa next door. Walk slowly and you will hear the city’s real tempo.",
        "O Jardim de Camões é o despertar da cidade: xadrez debaixo dos banianos e a Casa Garden branca ao lado. Anda devagar e ouves o verdadeiro ritmo de Macau.",
        "白鴿巣公園は朝の運動の場。大きなガジュマルの下で将棋、となりの白い東方基金会は欧州の別荘のよう。ゆっくり歩くと、本物のマカオのリズムが聞こえます。",
    ),
    "cathedral_macau": S(
        "主教座堂睇落好樸素，入到去先至發覺好安靜。大堂前地冇大三巴咁逼，本地人結婚、祈禱都鍾意嚟呢度，係澳門天主教嘅家。",
        "主教座堂外表朴素，进去才发觉特别安静。大堂前地没有大三巴那么挤，本地人结婚、祈祷都喜欢来这里，是澳门天主教的家。",
        "The cathedral looks modest until you step inside and the quiet lands. Cathedral Square is never as packed as St. Paul’s; weddings and weekday prayers still treat this as home.",
        "A Sé parece simples, mas lá dentro o silêncio acolhe. O largo não tem a fila das Ruínas; casamentos e orações ainda tratam este sítio como casa.",
        "司教座聖堂は地味に見えますが、中はとても静か。大堂前地は聖ポール跡ほど混まず、結婚式も祈りも、ここが澳門カトリックの家です。",
    ),
    "dom_pedro_theatre": S(
        "崗頂劇院係中國第一座西式劇院，薄荷綠色嗰面牆，好似一盒精緻嘅糖果。以前葡人喺度睇歌劇，而家你行過，都仲聞到舊時澳門嘅文藝味。",
        "岗顶剧院是中国第一座西式剧院，薄荷绿的墙像一盒精致的糖果。从前葡人在这里看歌剧，现在你走过，还能闻到旧时澳门的文艺气味。",
        "Dom Pedro V is China’s first Western-style theatre — mint-green, like a tin of sweets. Portuguese audiences once came for opera; walk past and the old cultural perfume is still there.",
        "O D. Pedro V foi o primeiro teatro ocidental na China, verde-menta como uma caixa de bombons. Havia ópera; hoje, ao passar, ainda sentes essa Macau culta.",
        "崗頂劇院は中国初の西洋劇場。ミント色の壁はお菓子の箱のよう。かつては歌劇、いま通り過ぎても、あの文芸の香りが残っています。",
    ),
    "guan_qian": S(
        "關前正街以前冷清，近年年輕主理人搬入嚟開古著、咖啡同本地設計舖。舊磚牆配新品，好似澳門自己喺度同自己傾偈。",
        "关前正街从前冷清，近年年轻主理人搬进来开古着、咖啡和本地设计店。旧砖墙配新品，像澳门在和自己聊天。",
        "Guan Qian was sleepy until young shopkeepers arrived with vintage clothes, coffee and local design. Old brick, new goods: Macau having a quiet conversation with itself.",
        "A Rua dos Mercadores esteve quieta até chegarem lojas de vintage, café e design local. Tijolo velho, peças novas: Macau a falar consigo própria.",
        "関前正街は静かでしたが、いまは古着、コーヒー、地元デザインの店。古い煉瓦に新しい品物、澳門が自分とおしゃべりしているようです。",
    ),
    "hang_yau_fishball": S(
        "大堂巷嗰架咖喱魚蛋車，本地人排隊排到出巷口。自選餸料、咖喱好濃，食完嘴唇都係香味。阿濠同你講，呢啲先係澳門日常。",
        "大堂巷那辆咖喱鱼蛋车，本地人会排到巷口。自己拣配料、咖喱很浓，吃完嘴唇都是香味。阿濠跟你说，这才是澳门日常。",
        "The curry fish-ball cart in Travessa da Sé draws a local queue out of the alley. You pick the extras, the sauce is thick, and your lips keep the smell. This, Ah-Hou says, is everyday Macau.",
        "O carrinho de peixe em caril na Travessa da Sé faz fila até à rua. Escolhes os extras, o molho é grosso, e o cheiro fica nos lábios. Isto é o Macau do dia-a-dia.",
        "大堂巷のカレー魚団子は、地元の行列が巷の外まで。具を選んで濃いカレー。食後も唇が香る。これが澳門の日常です。",
    ),
    "ho_tung_library": S(
        "何東圖書館以前係私人花園洋房，而家變咗公共閱讀嘅綠洲。後院啲樹好涼，鬧市行到呢度，心會突然靜低。",
        "何东图书馆从前是私人花园洋房，现在成了公共阅读的绿洲。后院的树很凉，从闹市走进来，心会突然静下来。",
        "Sir Robert Ho Tung’s garden villa is now a public library oasis. The backyard trees are cool; the city’s noise drops the moment you arrive.",
        "A villa-jardim de Ho Tung é agora biblioteca. As árvores do pátio refrescam; o barulho da cidade cai assim que entras.",
        "何東図書館はかつての花園洋館で、いまは読書のオアシス。裏庭の木陰は涼しく、繁華街から入ると心がすっと静まります。",
    ),
    "holy_house_mercy": S(
        "仁慈堂喺議事亭前地隔離，白色新古典，好似一位文靜嘅長者。澳門最早嘅慈善同醫院制度，好多都由呢度開始，觀光以外仲有一份心。",
        "仁慈堂在議事亭前地旁边，白色新古典，像一位文静的长者。澳门最早的慈善和医院制度，很多都从这里开始，观光之外还有一份心。",
        "Santa Casa da Misericórdia sits beside Senado Square in quiet white neoclassical dress. Macau’s first charity and hospital traditions started here — sightseeing with a conscience.",
        "A Santa Casa, branca e serena junto ao Leal Senado, viu nascer a caridade e o hospital em Macau. Há coração para além do postal.",
        "仁慈堂は議事亭前地の隣、白い新古典。澳門の慈善と病院の始まりで、観光の向こうに心があります。",
    ),
    "leal_senado": S(
        "民政總署大樓正正對住議事亭前地，入面有個好靜嘅葡式花園同圖書館。廣場好熱鬧，推門入去就好似匿入澳門自己嘅客廳。",
        "民政总署大楼正对着議事亭前地，里面有安静的葡式花园和图书馆。广场很热闹，推门进去就像躲进澳门自己的客厅。",
        "The Leal Senado faces the square; inside are a hush of Portuguese garden and a library. The plaza is loud; push the door and you have slipped into Macau’s own sitting room.",
        "O Leal Senado olha o largo; lá dentro há jardim português e biblioteca. Lá fora é festa; ao empurrar a porta entras na sala de Macau.",
        "民政総署は広場の真正面。中は静かな葡式庭園と図書館。外は賑やか、扉を開けると澳門の居間に入ったようです。",
    ),
    "lin_fong_temple": S(
        "蓮峰廟有古樹同石刻，相傳林則徐曾喺度接見葡官。你企喺廟前，會覺得歷史唔係博物館裡，而係風裡面。",
        "莲峰庙有古树和石刻，相传林则徐曾在此接见葡官。你站在庙前，会觉得历史不在博物馆里，而在风里面。",
        "Lin Fong Temple keeps old trees and stone inscriptions; Lin Zexu is said to have received Portuguese officials here. Stand at the gate and history is in the wind, not behind glass.",
        "O Templo de Lin Fong tem árvores antigas e inscrições; diz-se que Lin Zexu recebeu oficiais portugueses aqui. À porta, a história está no vento, não na vitrina.",
        "蓮峰廟には古木と石刻。林則徐がここで葡官と会ったと伝えられます。門前に立つと、歴史は展示ではなく風の中にあります。",
    ),
    "lou_kau_mansion": S(
        "盧家大屋匿喺鬧市裡，青磚牆、嶺南天井，仲有西式裝飾。遊客少，正正適合你慢慢睇澳門有錢人家從前點樣住。",
        "卢家大屋藏在闹市里，青砖墙、岭南天井，还有西式装饰。游客少，正好让你慢慢看澳门有钱人家从前怎么住。",
        "Lou Kau Mansion hides in the busy grid: grey-green brick, a Lingnan courtyard, Western trim. Few visitors — perfect for lingering over how a wealthy Macau family once lived.",
        "A Casa de Lou Kau esconde-se na malha urbana: tijolo, pátio lingnan, detalhes ocidentais. Pouca gente: dá para ver, com calma, como vivia uma família abastada.",
        "盧家大屋は繁華街に隠れた青煉瓦の邸。嶺南の中庭に西洋装飾。観光客は少なく、かつての富裕な家の暮らしをゆっくり見られます。",
    ),
    "lou_lim_ioc_garden": S(
        "盧廉若公園係澳門少見嘅中式園林，曲橋、池塘、亭台，本地人散步歇腳都嚟。你行過石橋，水光會同你一齊慢低。",
        "卢廉若公园是澳门少见的中式园林，曲桥、池塘、亭台，本地人散步歇脚都来。你走过石桥，水光会和你一起放慢。",
        "Lou Lim Ioc is Macau’s rare Chinese garden: zigzag bridges, a pond, pavilions. Locals come to rest. Cross the stone bridge and the water teaches you to slow down.",
        "O Jardim Lou Lim Ioc é o raro jardim chinês de Macau: pontes em ziguezague, lago, pavilhões. Os vizinhos vêm descansar. A água pede-te calma.",
        "盧廉若公園は珍しい中式庭園。曲橋、池、亭。地元の散歩先です。石橋を渡ると、水面といっしょに歩みがゆるみます。",
    ),
    "macau_museum": S(
        "澳門博物館喺大炮台裡面，漁村、商港、到而家嘅旅遊城市，一層層講清楚。行完出到天台，個城就喺腳下，故事同風景一齊嚟。",
        "澳门博物馆在大炮台里面，渔村、商港、到现在的旅游城市，一层层讲清楚。走完到天台，城市就在脚下，故事和风景一起来。",
        "Inside Monte Fort, the museum layers fishing village, trading port and today’s tourist city. Finish on the terrace: the town is under your shoes, story and view at once.",
        "No Forte do Monte, o museu empilha a aldeia de pescadores, o porto e a cidade turística. No terraço, Macau fica-te aos pés.",
        "澳門博物館は大砲台の中。漁村、商港、いまの観光都市を層ごとに。屋上に出ると街が足元で、物語と景色が同時に来ます。",
    ),
    "monte_fort": S(
        "大炮台係十七世紀軍事要塞，同大三巴隔條路。上到去吹一陣風，半島啲屋頂紅紅地攤開，先至明白點解叫『炮台』都要睇風景。",
        "大炮台是十七世纪军事要塞，和大三巴隔一条路。上去吹一阵风，半岛的屋顶红红地摊开，才明白为什么炮台也要看风景。",
        "Monte Fort is a seventeenth-century stronghold, a street away from St. Paul’s. The wind hits, red roofs fan out, and you understand why a gun battery is also a viewpoint.",
        "O Monte é uma fortaleza do século XVII, a uma rua das Ruínas. O vento chega, os telhados vermelhos abrem-se, e percebes porque uma bateria também é miradouro.",
        "大砲台は17世紀の要塞で、聖ポール跡のすぐそば。風に当たると赤い屋根が広がり、砲台が展望台でもある理由がわかります。",
    ),
    "na_tcha_temple": S(
        "哪吒廟細到差啲行過都睇唔到，貼住大三巴同舊城牆。一邊教堂一邊細廟，澳門多元信仰就係咁並排，唔使爭，大家一齊香火。",
        "哪吒庙小到差点走过都看不见，贴着大三巴和旧城墙。一边教堂一边小庙，澳门多元信仰就是这样并排，不必争，大家一起香火。",
        "Na Tcha Temple is so small you could miss it, glued to St. Paul’s and the old wall. Church and shrine side by side: Macau’s faiths do not shout over each other; they share the incense.",
        "O templo de Na Tcha é minúsculo, colado às Ruínas e à muralha. Igreja e templo lado a lado: as fés de Macau não gritam; partilham o incenso.",
        "哪吒廟は小さすぎて見逃しそう。聖ポール跡と旧城壁のすぐ横。教会と小さな廟が並び、信仰は奪い合わず、線香を分け合います。",
    ),
    "old_city_walls": S(
        "舊城牆用夯土、砂石同蠔殼灰砌成，貼住大三巴但好少人停低。你伸手摸一下，會摸到澳門保衛過自己嘅痕跡。",
        "旧城墙用夯土、砂石和蚝壳灰砌成，贴着大三巴但很少人停下。你伸手摸一下，会摸到澳门保卫过自己的痕迹。",
        "The old wall is rammed earth, sand and oyster-shell lime, right beside St. Paul’s, yet few stop. Touch it and you feel how Macau once defended itself.",
        "A muralha é terra batida, areia e cal de ostra, ao lado das Ruínas, e quase ninguém pára. Ao tocá-la, sentes como Macau se defendeu.",
        "旧城壁は版築、砂、カキ殻の灰。聖ポール跡の隣なのに、立ち止まる人は少ない。触れると、街が身を守った跡がわかります。",
    ),
    "red_market": S(
        "紅街市係一九三〇年代紅磚建築，而家仲係街坊買餸嘅地方。遊客行博物館，本地人喺度揀菜，兩種澳門同時存在。",
        "红街市是一九三〇年代红砖建筑，现在仍是街坊买菜的地方。游客走博物馆，本地人在这里拣菜，两种澳门同时存在。",
        "The Red Market is 1930s brick and still a neighbourhood wet market. Tourists do museums; locals choose greens. Two Macaus, same morning.",
        "O Mercado Vermelho é tijolo dos anos 30 e continua a ser o mercado do bairro. Turistas vão a museus; vizinhos escolhem hortaliças. Duas Macaus, a mesma manhã.",
        "紅街市は1930年代の赤煉瓦で、いまも買い物の場。観光客は博物館、地元は野菜を選ぶ。二つの澳門が同時にあります。",
    ),
    "sam_kai_vui_kun": S(
        "三街會館匿喺營地大街，以前華商議事，而家仲係關帝廟。香火同帳冊一齊留低，澳門華人點樣自己管自己，呢度最清楚。",
        "三街会馆藏在营地大街，从前华商议事，现在仍是关帝庙。香火和账册一起留下，澳门华人怎样自己管自己，这里最清楚。",
        "Sam Kai Vui Kun hides on Rua dos Mercadores: once a Chinese merchants’ hall, still a temple to Guan Di. Incense and ledgers together — this is how Chinese Macau governed itself.",
        "O Sam Kai Vui Kun esconde-se na Rua dos Mercadores: foi assembleia dos comerciantes chineses e continua templo de Guan Di. Incenso e livros de contas: a Macau chinesa a governar-se.",
        "三街会館は营地大街に隠れ、華商の議事堂であり関帝廟。線香と帳簿が残り、華人の自治が一番よくわかります。",
    ),
    "senado_square": S(
        "議事亭前地舖滿波浪紋碎石，四周粉彩色歐式建築，係澳門嘅客廳。人多唔係壞事，你睇地下嗰條波，就好似海一路跟住你。",
        "議事亭前地铺满波浪纹碎石，四周粉彩色欧式建筑，是澳门的客厅。人多不是坏事，你看地上那条波，就像海一直跟着你。",
        "Senado Square is Macau’s sitting room: wave-pattern cobbles and pastel façades. Crowds are part of the furniture; the pavement still looks like the sea walking with you.",
        "O Largo do Senado é a sala de Macau: calçada em ondas e fachadas a pastel. A multidão faz parte; o chão parece o mar a ir contigo.",
        "議事亭前地は波模様の石畳とパステルの建物、澳門の居間。混むのもご愛敬で、地面の波が海のようについてきます。",
    ),
    "st_anthony_church": S(
        "花王堂係澳門最古老教堂之一，婚禮特別多，所以街坊叫佢花王堂。白牆細巧，附近樟樹同石仔路，好適合靜靜行一段。",
        "花王堂是澳门最古老教堂之一，婚礼特别多，所以街坊叫它花王堂。白墙小巧，附近樟树和石子路，很适合静静走一段。",
        "St. Anthony’s is among Macau’s oldest churches and so popular for weddings that locals call it the ‘Flower King’ church. White, small, camphor trees and cobbles: a gentle stretch of walking.",
        "Santo António é das igrejas mais antigas; há tantos casamentos que o povo lhe chama Igreja das Flores. Branca, pequena, com cânforas e calçada: um troço calmo.",
        "聖アンタントニオ聖堂は最古級で、結婚式が多く「花王堂」と呼ばれます。白い小さな堂、クスノキと石畳。静かな散歩に向きます。",
    ),
    "st_augustine": S(
        "聖奧斯定教堂企喺崗頂前地，每年苦難善耶穌聖像出遊由呢度起步。劇院、圖書館、教堂圍住一個細廣場，澳門最有歐洲小鎮味嘅一角。",
        "圣奥斯定教堂立在岗顶前地，每年苦难善耶稣圣像出游从这里起步。剧院、图书馆、教堂围住一个小广场，是澳门最有欧洲小镇味的一角。",
        "St. Augustine’s stands on the little square where the Procession of the Passion begins each year. Theatre, library and church around one plaza: Macau’s most European-village corner.",
        "Santo Agostinho marca o largo de onde sai a Procissão da Paixão. Teatro, biblioteca e igreja num só terreiro: o canto mais de vila europeia em Macau.",
        "聖アウグスチノ聖堂は崗頂前地にあり、受難像の行列はここから。劇場、図書館、教会が小さな広場を囲み、いちばん欧州の村らしい角です。",
    ),
    "st_dominic": S(
        "玫瑰堂鵝黃色巴洛克，議事亭前地一抬頭就見到。入面聖物寶庫好靜，出面廣場好旺，一扇門隔開兩種澳門時間。",
        "玫瑰堂鹅黄色巴洛克，議事亭前地一抬头就看见。里面圣物宝库很静，外面广场很旺，一扇门隔开两种澳门时间。",
        "St. Dominic’s is butter-yellow baroque, the square’s visual full stop. The relic treasury inside is hushed; outside the plaza bustles. One door, two clocks for Macau.",
        "São Domingos é barroco amarelo-manteiga, o ponto final do largo. O tesouro de relíquias cala; lá fora o largo ferve. Uma porta, dois relógios.",
        "玫瑰堂はバター色のバロックで、広場の目印。中の聖遺物は静か、外は賑やか。一枚の扉が二つの時間を分けます。",
    ),
    "tap_seac_gallery": S(
        "塔石藝文館由歷史建築改成展覽空間，老城散步中途入去睇一場，腳同眼都休息到。藝術唔一定要專程，可以夾喺巷仔之間。",
        "塔石艺文馆由历史建筑改成展览空间，老城散步中途进去看一场，脚和眼都休息到。艺术不一定要专程，可以夹在巷子之间。",
        "Tap Seac Gallery turned a historic house into exhibition rooms. Duck in mid-walk: feet and eyes both rest. Art here is not a pilgrimage; it lives between lanes.",
        "A Galeria do Tap Seac fez de uma casa histórica um espaço de mostras. Entra a meio do passeio: pés e olhos descansam. A arte vive entre ruelas.",
        "塔石芸文館は歴史建築の展示空間。散歩の途中で入ると足も目も休まる。芸術は遠出しなくても、路地のあいだにあります。",
    ),
    "tap_seac_square": S(
        "塔石廣場紅磚地面，四周葡式建築齊齊整整，書展、文創市集常常喺度擺。澳門唔止賭場同世遺，呢度見到社區自己玩。",
        "塔石广场红砖地面，四周葡式建筑整整齐齐，书展、文创市集常常在这里摆。澳门不止赌场和世遗，这里看见社区自己玩。",
        "Tap Seac Square is red brick and neat Portuguese fronts, often hosting book fairs and design markets. Macau is not only casinos and UNESCO; here the neighbourhood plays.",
        "O Tap Seac é tijolo vermelho e frentes portuguesas, com feiras do livro e mercados criativos. Macau não é só casinos e património; aqui o bairro brinca.",
        "塔石広場は赤煉瓦と整った葡式建築。ブックフェアや市がよく出ます。カジノと世界遺産だけではない、地域の遊び場です。",
    ),
    "three_lamps": S(
        "三盞燈一帶緬甸、泰國、印尼小店好密，咖喱同香料味出到街。澳門唔止中葡兩味，呢度先至見到真正多元嘅街坊。",
        "三盏灯一带缅甸、泰国、印尼小店很密，咖喱和香料味飘到街上。澳门不止中葡两味，这里才见到真正多元的街坊。",
        "Around the Three Lamps, Burmese, Thai and Indonesian kitchens sit tight, curry in the air. Macau is more than Chinese and Portuguese; this is the neighbourhood’s real mix.",
        "Nas Três Lâmpadas há cozinhas birmanesas, tailandesas e indonésias, o cheiro de caril na rua. Macau não é só china e portugalidade; aqui está a mistura verdadeira.",
        "三盞燈はミャンマー、タイ、インドネシアの店が密集し、カレーの香り。中葡だけではない、本当に多様な街です。",
    ),
    "travessa_paixao": S(
        "戀愛巷粉紅同鵝黃色牆，碎石斜路，大三巴隔離但人少啲。情侶影相一流，阿濠提醒你：唔好淨係對住鏡頭，抬頭睇下窗花。",
        "恋爱巷粉红和鹅黄色墙，碎石斜路，大三巴隔壁但人少一点。情侣拍照一流，阿濠提醒你：不要只对着镜头，抬头看看窗花。",
        "Love Lane is pink and cream cobbles, beside St. Paul’s but a shade quieter. Perfect for couple photos — and Ah-Hou would add: look up from the camera at the window carvings.",
        "A Travessa da Paixão é rosa e creme, ao lado das Ruínas mas um pouco mais calma. Óptima para fotos de casal — e olha as janelas, não só o ecrã.",
        "恋愛巷はピンクとクリーム色の石畳。聖ポール跡の隣でも少し空いています。カップル写真に最適。レンズから顔を上げて、窓の装飾も見て。",
    ),
    "wong_chi_kei": S(
        "黃枝記打竹昇麵打咗八十幾年，蝦子撈麵同鮮蝦雲吞係 ban 位。米芝蓮推介過，但阿濠覺得最緊要係：本地人今朝都仲會入嚟食一碗。",
        "黄枝记打竹升面打了八十几年，虾子捞面和鲜虾云吞是镇店。米其林推介过，但阿濠觉得最要紧的是：本地人今天早上还会进来吃一碗。",
        "Wong Chi Kei has bamboo-pressed noodles for eighty-plus years; shrimp-roe lo mein and prawn wontons are the signatures. Michelin noticed, but Ah-Hou cares more that locals still come in for a morning bowl.",
        "A Wong Chi Kei amassa noodles há mais de oitenta anos; o lo mein de ovas e os wonton de camarão são a casa. A Michelin viu; Ah-Hou prefere que os vizinhos ainda entrem de manhã.",
        "黄枝記は八十余年の竹升麺。エビ子拌麺と海老雲呑が看板。ミシュランも推したが、今朝も地元が碗を運ぶのがいちばん大事。",
    ),
    "yee_shun_milk": S(
        "義順鮮奶源自順德，雙皮燉奶同薑汁撞奶滑到好似講悄悄話。食甜品唔使急，呢碗奶會教你澳門都識得慢。",
        "义顺鲜奶源自顺德，双皮炖奶和姜汁撞奶滑得像在讲悄悄话。吃甜品不用急，这碗奶会教你澳门也懂得慢。",
        "Yee Shun comes from Shunde: double-skin milk pudding and ginger milk curd so silky they almost whisper. Dessert is not a rush; this bowl teaches Macau’s slower gear.",
        "A Yee Shun vem de Shunde: o leite de duas peles e o leite de gengibre são tão sedosos que quase sussurram. A sobremesa não corre; ensina a Macau lenta.",
        "義順は順徳発。ダブルスキンプリンと生姜ミルクはささやきのように滑らか。急がなくていい。この一碗が、遅い澳門を教えます。",
    ),
    "cheoc_van_beach": S(
        "竹灣比黑沙更靜，海水泳池同斜坡小路好適合慢慢行。聽海、睇山，路環會同你講：唔使全程都好熱鬧。",
        "竹湾比黑沙更静，海水泳池和斜坡小路很适合慢慢走。听海、看山，路环会跟你说：不必全程都热闹。",
        "Cheoc Van is quieter than Hac Sa, with a tidal pool and a sloping path. Sea, hill, and Coloane reminding you the day does not have to be loud.",
        "Cheoc Van é mais calma que Hac Sá, com piscina de mar e caminho em rampa. Mar e monte: Coloane diz-te que o dia não precisa de barulho.",
        "竹湾は黒沙より静か。海水プールと坂道。海と山が、一日中にぎやかでなくていいと路環が言います。",
    ),
    "coloane_village": S(
        "路環市區仲係彩色平房、碼頭同小店，節奏慢過半島兩個档。你行到廣場，會見到街坊坐低吹海風，好似時間自己放假。",
        "路环市区还是彩色平房、码头和小店，节奏比半岛慢两档。你走到广场，会见到街坊坐着吹海风，像时间自己放假。",
        "Coloane village still has pastel houses, a pier and small shops, two gears slower than the peninsula. On the square, neighbours sit in the sea breeze as if time had taken the afternoon off.",
        "A vila de Coloane ainda tem casas a pastel, cais e lojas, dois andamentos abaixo da península. No largo, os vizinhos sentam-se à brisa como se o tempo tivesse folga.",
        "路環の町は色家、埠頭、小さな店。半島より二段遅い。広場で海風に当たる人を見ると、時間まで休んでいるようです。",
    ),
    "fernando_restaurant": S(
        "法蘭度喺黑沙旁邊，蒜蓉包、葡式烤雞同海鮮，係路環經典分享餐。沙都未抖走，已經聞到烤爐味，離島午餐就應該咁。",
        "法兰度在黑沙旁边，蒜蓉包、葡式烤鸡和海鲜，是路环经典分享餐。沙还没抖走，已经闻到烤炉味，离岛午餐就应该这样。",
        "Fernando’s sits by Hac Sa: garlic bread, Portuguese chicken and seafood meant for sharing. Sand still on your shoes, oven already in the air. That is an island lunch.",
        "O Fernando fica junto a Hac Sá: pão de alho, frango à portuguesa e marisco para partilhar. Ainda com areia nos sapatos, já cheira a forno. Almoço de ilha.",
        "フェルナンドは黒沙のそば。ニンニクパン、葡式鶏、海鮮のシェア。砂を払う前にオーブンの匂い。離島の昼はこれでいい。",
    ),
    "hac_sa_beach": S(
        "黑沙係澳門最大天然海灘，沙係深色細粒，踩落去軟軟地。唔使游水都值得行一圈，海風會幫你把半島嘅逼人味吹走。",
        "黑沙是澳门最大天然海滩，沙是深色细粒，踩下去软软的。不必游泳也值得走一圈，海风会帮你把半岛的拥挤吹走。",
        "Hac Sa is Macau’s biggest natural beach, dark fine sand that gives underfoot. You need not swim; a loop in the wind rinses the peninsula’s crush out of you.",
        "Hac Sá é a maior praia natural, areia escura e fina. Não é preciso nadar; uma volta ao vento lava a azáfama da península.",
        "黒沙は最大の天然ビーチ。細かい黒い砂は柔らかい。泳がなくても一周する価値があり、海風が半島の混雑を流します。",
    ),
    "hac_sa_park": S(
        "黑沙公園挨住海灘，草地同樹蔭適合親子野餐。小朋友跑、大人坐，路環教你點樣『無事發生』都係行程一部分。",
        "黑沙公园挨着海滩，草地和树荫适合亲子野餐。小朋友跑、大人坐，路环教你怎样“没事发生”也是行程的一部分。",
        "Hac Sa Park leans against the beach: lawn and shade for a family picnic. Children run, adults sit. Coloane teaches that nothing happening is still part of the day.",
        "O parque encosta à praia: relvado e sombra para piquenique. Crianças correm, adultos sentam. Coloane ensina que nada acontecer também é roteiro.",
        "黒沙公園はビーチ隣の芝生と木陰。子どもは走り、大人は座る。「何もない」も旅程だと路環が教えます。",
    ),
    "lai_chi_vun": S(
        "荔枝碗舊船廠而家活化成海邊文化片區，木構船棚仲喺。澳門曾經識得造船，呢度將工業記憶輕輕放低俾你睇。",
        "荔枝碗旧船厂如今活化成海边文化片区，木构船棚还在。澳门曾经懂得造船，这里把工业记忆轻轻放低给你看。",
        "Lai Chi Vun’s old shipyards are now a waterfront cultural strip; the timber sheds remain. Macau once built boats. Here that industrial memory is set down gently for you.",
        "Os estaleiros de Lai Chi Vun são agora um eixo cultural à beira-mar; os galpões de madeira ficaram. Macau soube construir barcos. A memória industrial está aqui, com jeito.",
        "荔枝碗の船廠は海辺の文化区になり、木造の船小屋が残ります。澳門は船を造っていた。その記憶が、やさしく置いてあります。",
    ),
    "lord_stow": S(
        "安德魯餅店一九八九年由英國人 Andrew 喺路環創立，焦香酥脆嗰隻葡撻，好多人口中嘅『正宗』由呢度開始。排隊都值得，因為第一啖係故事。",
        "安德鲁饼店一九八九年由英国人 Andrew 在路环创立，焦香酥脆的葡挞，很多人口中的“正宗”从这里开始。排队也值得，因为第一口就是故事。",
        "Lord Stow’s opened in Coloane in 1989; that dark, shatter-crisp tart is what many people mean by ‘the real one’. The queue is part of the tale, and the first bite is the plot.",
        "A Lord Stow nasceu em Coloane em 1989; o pastel escuro e estaladiço é o ‘autêntico’ para muita gente. A fila faz parte; a primeira dentada é o enredo.",
        "ロード・ストウは1989年、英国人アンドリューが路環に開業。焦げ香のサクサク蛋撻が「本家」。列も物語で、一口目が本題です。",
    ),
    "nga_tim_cafe": S(
        "雅憩花園餐廳就喺聖堂旁邊，露天座位同葡國菜好有小村氣氛。鐘聲、椰影、一碟馬介休，路環嘅中午應該咁過。",
        "雅憩花园餐厅就在教堂旁边，露天座位和葡国菜很有小村气氛。钟声、椰影、一碟马介休，路环的中午应该这样过。",
        "Nga Tim sits beside the chapel, open-air tables and Portuguese plates, village-slow. Bells, palms, a dish of bacalhau: that is noon in Coloane.",
        "O Nga Tim fica ao lado da capela, esplanada e pratos portugueses, ritmo de vila. Sinos, palmeiras, um bacalhau: o meio-dia em Coloane.",
        "雅憩は聖堂の隣。テラスと葡国料理で村の空気。鐘、椰子、バカリャウ。路環の昼はこれでいい。",
    ),
    "panda_pavilion": S(
        "熊貓館喺石排灣，大熊貓同小熊貓都有，親子多日遊好穩陣。阿濠唔會同你講好『罕見』，淨係講：睇住佢哋食竹，心情會意外地好。",
        "熊猫馆在石排湾，大熊猫和小熊猫都有，亲子多日游很稳妥。阿濠不会说有多“罕见”，只说：看着它们吃竹子，心情会意外地好。",
        "The Panda Pavilion in Seac Pai Van has giant and red pandas, a solid family stop. Ah-Hou will not call it rare; he will say watching them eat bamboo quietly improves the day.",
        "O Pavilhão dos Pandas tem pandas-gigantes e vermelhos, bom para famílias. Ah-Hou não fala em raridade; diz só que vê-los comer bambu melhora o dia.",
        "パンダ館は石排湾。ジャイアントもレッサーもいて、家族向き。珍しいとは言わず、竹を食べる姿を見ると、気分が意外とよくなります。",
    ),
    "seac_pai_van_park": S(
        "石排灣郊野公園有步道同自然教育，路環大肺葉。行一陣樹蔭，再決定去海邊定睇熊貓，離島行程就唔會成日食同影相。",
        "石排湾郊野公园有步道和自然教育，是路环的大肺叶。走一阵树荫，再决定去海边还是看熊猫，离岛行程才不会整天吃和拍照。",
        "Seac Pai Van Country Park is Coloane’s big green lung: trails and nature notes. Shade first, then beach or pandas — so the island day is not only eating and photos.",
        "O Parque de Seac Pai Van é o pulmão de Coloane: trilhos e educação na natureza. Primeiro a sombra, depois praia ou pandas — o dia não é só comer e fotografar.",
        "石排湾郊野公園は路環の大きな肺。遊歩道と自然学習。木陰を歩いてから海かパンダか。離島の一日が食べて撮るだけにならない。",
    ),
    "st_francis_coloane": S(
        "路環聖方濟各聖堂鵝黃色，廣場有椰影，慢活代名詞。你企喺門前，海味同鐘聲一齊嚟，心會自動調校慢兩格。",
        "路环圣方济各聖堂鹅黄色，广场有椰影，慢活代名词。你站在门前，海味和钟声一起来，心会自动调慢两格。",
        "The cream-yellow Chapel of St. Francis Xavier, palms on the square, is Coloane’s emblem of slow. At the door, sea air and bells arrive together, and your pulse drops two notches.",
        "A capela amarelo-creme de São Francisco Xavier, palmeiras no largo, é o símbolo da vida lenta. À porta, mar e sinos chegam juntos, e o pulso desce dois pontos.",
        "聖フランシスコ・ザビエル聖堂はクリーム色。広場の椰子がスローライフの象徴。門前で潮風と鐘が同時に来て、心が二段遅くなります。",
    ),
    "tam_kung_temple": S(
        "譚公廟係路環漁村信仰，廟前海風同老榕樹。你唔使識得譚公生平，都感受得到呢度曾經為出海嘅人祈過好多風。",
        "谭公庙是路环渔村信仰，庙前海风和老榕树。你不必懂得谭公生平，也能感到这里曾经为出海的人祈过很多风。",
        "Tam Kung Temple is Coloane’s fishing faith: sea wind and an old banyan at the door. You need not know the saint’s life to feel how many winds were asked for the boats.",
        "O templo de Tam Kong é a fé da vila: vento e um velho baniano. Não precisas da biografia para sentir quantos ventos se pediram para os barcos.",
        "譚公廟は漁村の信仰。海風と大きなガジュマル。生涯を知らなくても、船出の風を何回も祈った場所だとわかります。",
    ),
    "fishermans_wharf": S(
        "漁人碼頭外港旁，羅馬競技場外觀同海景，影相好易出片。阿濠會老實講：呢度偏主題樂園，行完記得返舊區食一餐，先至平衡。",
        "渔人码头在外港旁，罗马竞技场外观和海景，拍照很容易出片。阿濠会老实讲：这里偏主题乐园，走完记得回旧区吃一餐，才平衡。",
        "Fisherman’s Wharf by the outer harbour has a Roman-arena silhouette and easy sea photos. Ah-Hou will be honest: it is theme-park-ish. Afterward, eat in the old town to balance the day.",
        "O Fisherman’s Wharf tem arena à romana e mar fácil de fotografar. Ah-Hou é franco: sabe a parque temático. Depois, come no bairro antigo para equilibrar.",
        "漁人碼頭は外港そばのローマ風と海。写真は撮りやすい。テーマパーク寄り、と正直に言います。あとで旧区で一食すると釣り合います。",
    ),
    "grand_prix_museum": S(
        "大賽車博物館講格蘭披治，賽車、頭盔同互動都有。澳門除咗世遺，仲有一條每年响一次嘅引擎聲，呢度將佢收埋俾你聽。",
        "大赛车博物馆讲格兰披治，赛车、头盔和互动都有。澳门除了世遗，还有一条每年响一次的引擎声，这里把它收起来给你听。",
        "The Grand Prix Museum keeps helmets, cars and hands-on bits of the Guia circuit. Besides UNESCO stone, Macau has an engine note that sounds once a year; here you can hear it on a quiet day.",
        "O Museu do Grande Prémio guarda carros, capacetes e o circuito da Guia. Além da pedra UNESCO, Macau tem um motor que canta uma vez por ano; aqui ouves-no em silêncio.",
        "グランプリ博物館は車、ヘルメット、体験。世界遺産の石に加えて、年に一度鳴るエンジン。ここで静かな日にも聴けます。",
    ),
    "guia_fortress": S(
        "東望洋燈塔係中國海岸最古老嘅一座，上到松山可以睇成個半島。炮台、小堂、壁畫一齊，行山同睇歷史可以同一條路。",
        "东望洋灯塔是中国海岸最古老的一座，上到松山可以看整个半岛。炮台、小堂、壁画一起，行山和看历史可以同一条路。",
        "Guia Lighthouse is the oldest on the China coast; from the hill the whole peninsula opens. Fortress, chapel and frescoes share one path, so the hike is also the history lesson.",
        "O Farol da Guia é o mais antigo da costa da China; do monte vê-se a península. Fortaleza, capela e frescos no mesmo caminho: o passeio é aula.",
        "東望洋灯台は中国沿岸最古。松山から半島全体が見えます。砲台、聖堂、壁画が一つの道で、散歩が歴史になります。",
    ),
    "kun_iam_temple": S(
        "普濟禪院庭院深幽，同《望廈條約》簽訂地相關，澳門三大古廟之一。香、樹、石，行入去會覺得城市突然退後幾步。",
        "普济禅院庭院深幽，与《望厦条约》签订地相关，是澳门三大古庙之一。香、树、石，走进去会觉得城市突然退后几步。",
        "Kun Iam Tong’s courtyards run deep; it is tied to the Treaty of Wangxia and is one of Macau’s three great temples. Incense, trees, stone: the city takes a few steps back.",
        "O Kun Iam Tong tem pátios fundos, liga-se ao Tratado de Wangxia e é um dos três grandes templos. Incenso, árvores, pedra: a cidade recua uns passos.",
        "普済禅院は庭が深く、『望廈条約』にも縁。三大古廟の一つ。香、木、石。入ると街が数歩うしろに下がります。",
    ),
    "science_center": S(
        "科學館銀色圓錐係貝聿銘團隊作品，展覽互動高，親子同落雨天一流。澳門唔止舊磚，仲有一棟會發光嘅未來。",
        "科学馆银色圆锥是贝聿铭团队作品，展览互动高，亲子和下雨天一流。澳门不止旧砖，还有一栋会发光的未来。",
        "The Science Centre’s silver cone is an I. M. Pei-team building, hands-on and perfect for families or rain. Macau is not only old brick; it also has a piece of glowing future.",
        "O cone prateado do Centro de Ciência é da equipa de I. M. Pei, interactivo, ideal com crianças ou chuva. Macau não é só tijolo velho; também tem futuro a brilhar.",
        "科学館の銀の円錐は貝聿銘チーム。展示は触れて学べ、雨の日や親子に最適。古い煉瓦だけではない、光る未来もあります。",
    ),
    "kun_iam_statue": S(
        "觀音蓮花苑企喺海面，現代雕塑同佛教語言一齊。海風好開揚，你唔使拜都值得行近睇下澳門點樣用新形態講舊信仰。",
        "观音莲花苑立在海面，现代雕塑和佛教语言在一起。海风很开扬，你不必拜也值得走近，看看澳门怎样用新形态讲旧信仰。",
        "Kun Iam on the water is modern sculpture speaking a Buddhist sentence. The wind is wide; you need not pray to see how Macau tells an old faith in a new shape.",
        "A Kun Iam sobre a água é escultura contemporânea a falar budismo. O vento é largo; não é preciso rezar para ver a fé antiga em forma nova.",
        "観音像は海の上。現代彫刻が仏教を話します。風が広く、拝まなくても、古い信仰の新しい姿を見に行く価値があります。",
    ),
    "macau_tower": S(
        "旅遊塔三百三十八米，笨豬跳同三百六十度珠江口。刺激歸刺激，阿濠更想你喺觀景層認一認：邊邊係舊城，邊邊係填海。",
        "旅游塔三百三十八米，蹦极和三百六十度珠江口。刺激归刺激，阿濠更想你在观景层认一认：哪边是旧城，哪边是填海。",
        "Macau Tower is 338 metres of skyjump and a full Pearl River mouth. The thrill is real; Ah-Hou would rather you pick out old town versus reclaimed land from the deck.",
        "A Torre tem 338 metros, bungee e a foz do Rio das Pérolas. O arrepio existe; Ah-Hou pede-te que distingas cidade antiga e aterro lá do alto.",
        "観光塔は338メートル。バンジーと珠江口の全景。刺激は刺激、展望台で旧市街と埋立を見分けてほしい。",
    ),
    "moorish_barracks": S(
        "港務局大樓黃色拱廊，原嚟係印度兵營，摩爾風格臨海。澳門故事裡唔止中同葡，仲有南亞士兵守過呢段岸。",
        "港务局大楼黄色拱廊，原来是印度兵营，摩尔风格临海。澳门故事里不止中和葡，还有南亚士兵守过这段岸。",
        "The yellow-arched Moorish Barracks faced the sea as housing for Indian troops. Macau’s story is not only Chinese and Portuguese; South Asian soldiers kept this shore.",
        "Os arcos amarelos dos Quartéis Mouros olhavam o mar, casa de tropas indianas. A história não é só china e portuguesa; soldados do sul da Ásia guardaram esta costa.",
        "港務局の黄色いアーチは、もとインド兵の営舎。中と葡だけではない、南アジアの兵がこの岸を守っていました。",
    ),
    "penha_church": S(
        "主教山小堂白色，俯瞰西灣大橋同南灣。黃昏最靚，阿濠叫你早啲上，佔個位睇燈，唔好淨係喺下面影塔。",
        "主教山小堂白色，俯瞰西湾大桥和南湾。黄昏最美，阿濠叫你早点上，占个位看灯，不要只在下面拍塔。",
        "Penha Chapel is white above the Sai Van Bridge and the bay. Dusk is the hour; Ah-Hou says go up early, take a rail, and watch the lights — not only shoot the tower from below.",
        "A Capela da Penha é branca sobre a ponte de Sai Van e a baía. O entardecer é a hora; sobe cedo, ocupa um lugar, vê as luzes — não fiques só a fotografar a torre lá de baixo.",
        "西望洋聖堂は白く、西湾大橋と南湾を見下ろします。黄昏がいちばん。早めに上がって欄干で灯を見て。下から塔を撮るだけにしないで。",
    ),
    "st_lawrence": S(
        "風順堂俗稱就係為出海家人祈求順風。三大古教堂之一，企喺西望洋山腳。你聽到名，就明白澳門曾經成日等船返嚟。",
        "风顺堂俗称就是为出海家人祈求顺风。三大古教堂之一，立在西望洋山脚。你听到这名字，就明白澳门曾经整天等船回来。",
        "St. Lawrence’s is nicknamed the Wind-Favour church, prayers for families at sea. One of the three old churches, at the foot of Penha. The name itself is Macau waiting for boats to come home.",
        "São Lourenço chama-se Igreja do Vento Favorável: reza por quem está no mar. Uma das três igrejas antigas, ao pé da Penha. O nome é Macau à espera dos barcos.",
        "風順堂は、海に出た家族の順風を祈る名。三大古教会の一つで西望洋の麓。その名を聞くと、船を待っていた澳門がわかります。",
    ),
    "broadway_food_street": S(
        "百老匯美食街集合好多澳門同亞洲口味，人多時最方便各取所需。阿濠會講：呢度解決肚子；想食『有故事』嘅，返官也街同舊區。",
        "百老汇美食街集合好多澳门和亚洲口味，人多时最方便各取所需。阿濠会讲：这里解决肚子；想吃“有故事”的，回官也街和旧区。",
        "Broadway Food Street gathers Macau and Asian counters, handy when a group cannot agree. Ah-Hou: this fills the stomach; for food with a story, go back to Rua do Cunha and the old lanes.",
        "A Broadway junta sabores de Macau e da Ásia, prático quando o grupo não se entende. Ah-Hou: aqui enche-se a barriga; a comida com história está na Rua do Cunha e nas ruelas.",
        "ブロードウェイ美食街は澳門とアジアの店が集まり、人数が多いと便利。お腹はここで。物語のある味は官也街と旧区へ。",
    ),
    "carmel_church": S(
        "嘉模聖母堂米黃色，氹仔小山上面，可以望龍環葡韻同濕地。行完官也街上嚟吹風，視線會突然打開。",
        "嘉模圣母堂米黄色，氹仔小山上面，可以望龙环葡韵和湿地。走完官也街上来吹风，视线会突然打开。",
        "Our Lady of Carmel is cream on Taipa’s little hill, looking over the Houses and the wetland. After Rua do Cunha the wind hits and the view suddenly opens.",
        "Nossa Senhora do Carmo é cor de creme no outeiro da Taipa, sobre as Casas-Museu e o sapal. Depois da Rua do Cunha o vento chega e a vista abre.",
        "嘉模聖母堂はクリーム色の小さな丘。龍環葡韻と湿地が見えます。官也街のあと風に当たると、視界がぱっと開けます。",
    ),
    "mok_yi_kei": S(
        "莫義記大菜糕係官也街百年甜品，大菜糕同榴槤雪糕消暑。阿濠細個已經食，而家帶你嚟，唔係打卡，係續一碗涼。",
        "莫义记大菜糕是官也街百年甜品，大菜糕和榴莲雪糕消暑。阿濠小时候已经吃，现在带你来，不是打卡，是续一碗凉。",
        "Mok Yi Kei’s agar jelly and durian ice cream have cooled Rua do Cunha for a century. Ah-Hou ate this as a child; he is not taking you for a photo, he is handing you a cold bowl.",
        "O gelado de durião e a gelatina da Mok Yi Kei refrescam a Rua do Cunha há um século. Ah-Hou comia isto pequeno; não é para foto, é para uma tigela fria.",
        "莫義記の大菜糕は百年の甘味。寒天とドリアンアイス。子どもの頃から食べていて、写真ではなく、冷たい一碗を継ぐために連れてきます。",
    ),
    "old_taipa_market": S(
        "氹仔街市係街坊買餸嘅地方，同行兩步嘅官也街好唔同。一邊旅遊手信，一邊青菜鮮魚，你兩條街一齊行，先睇到完整氹仔。",
        "氹仔街市是街坊买菜的地方，和隔两步的官也街很不同。一边旅游手信，一边青菜鲜鱼，两条街一起走，才看到完整氹仔。",
        "Old Taipa Market is where neighbours shop, two steps from souvenir-heavy Rua do Cunha. Postcards one lane, greens and fish the next; walk both and Taipa is complete.",
        "O mercado da Taipa é dos vizinhos, a dois passos da Rua do Cunha turística. Lembranças numa rua, hortaliça e peixe na outra; as duas juntas fazem a Taipa inteira.",
        "氹仔市場は近所の買い出し。数歩先の官也街とは別世界。みやげと青菜。両方歩いて、はじめて氹仔が揃います。",
    ),
    "pak_tai_temple_taipa": S(
        "氹仔北帝廟留住漁村時代嘅民間信仰。官也街好旺，轉入廟就靜，好似氹仔仲記得自己以前靠海食飯。",
        "氹仔北帝庙留住渔村时代的民间信仰。官也街很旺，转入庙就静，像氹仔还记得自己以前靠海吃饭。",
        "Pak Tai Temple keeps Taipa’s fishing-village faith. Rua do Cunha is busy; inside the temple it is still, as if Taipa still remembers living off the sea.",
        "O templo de Pak Tai guarda a fé da vila de pescadores. A Rua do Cunha ferve; no templo há silêncio, como se a Taipa ainda se lembrasse do mar.",
        "北帝廟は漁村の信仰を残します。官也街は賑やか、廟の中は静か。海で食べていた自分を、氹仔が覚えているようです。",
    ),
    "parisian_macau": S(
        "巴黎人鐵塔夜景亮燈好易影，路氹另一種澳門。阿濠唔反對你嚟打卡，但會輕輕講：聽日記得返舊區，先至唔好以為澳門淨係燈光。",
        "巴黎人铁塔夜景亮灯很好拍，路氹另一种澳门。阿濠不反对你来打卡，但会轻轻说：明天记得回旧区，才不要以为澳门只是灯光。",
        "The Parisian’s tower photographs easily after dark: Cotai’s other Macau. Ah-Hou will not stop your picture; he will murmur that tomorrow you should return to the old streets, so the city is not only lights.",
        "A torre parisiense fotografa-se bem à noite: a outra Macau de Cotai. Ah-Hou não te impede o postal; pede só que amanhã voltes às ruelas, para a cidade não ser só luzes.",
        "パリジャンの塔は夜景が撮りやすい。コタイの別の澳門。写真は止めない。明日は旧区へ。街が光だけにならないように。",
    ),
    "pou_tai_temple": S(
        "菩提禪院喺氹仔山邊，園林清幽，官也街行完最啱過嚟歇。木魚同樹影，嘈完美食之後，俾耳仔放假。",
        "菩提禅院在氹仔山边，园林清幽，官也街走完最适合过来歇。木鱼和树影，热闹完美食之后，给耳朵放假。",
        "Pou Tai Un sits on Taipa’s hillside, gardens quiet after Rua do Cunha. Wooden fish-drum and tree shade: let your ears rest after the food noise.",
        "O Pou Tai Un fica na encosta da Taipa, jardins quietos depois da Rua do Cunha. Tambor de madeira e sombra: os ouvidos também merecem folga.",
        "菩提禅院は氹仔の山際。官也街のあと休むのに最適。木魚と木陰。美食の喧騒のあと、耳を休ませて。",
    ),
    "rua_cunha": S(
        "官也街短短一條臥虎藏龍，豬扒包、大菜糕、蛋卷排成行。人多係真，但你慢慢揀、錯開正午，仲係氹仔最順路嘅美食起點。",
        "官也街短短一条卧虎藏龙，猪扒包、大菜糕、蛋卷排成行。人多是真，但你慢慢拣、错开正午，仍是氹仔最顺路的美食起点。",
        "Rua do Cunha is short and crowded with pork-chop buns, agar jelly and egg rolls. Yes, it is busy; pick slowly, skip high noon, and it remains Taipa’s natural food start.",
        "A Rua do Cunha é curta e cheia de pães de porco, gelatinas e rolos de ovo. Há gente; escolhe devagar, evita o meio-dia, e continua o arranque certo da Taipa.",
        "官也街は短いのに猪扒包、大菜糕、蛋巻が並ぶ。混むのは本当。ゆっくり選んで正午をずらせば、いちばん順路の美食スタート。",
    ),
    "seng_cheong": S(
        "誠昌水蟹粥喺官也街附近，一煲鮮甜，適合作為氹仔舊城正餐。阿濠建議兩至三人分享，食完再行，唔好撐住去影龍環葡韻。",
        "诚昌水蟹粥在官也街附近，一煲鲜甜，适合作为氹仔旧城正餐。阿濠建议两至三人分享，吃完再走，不要撑着去拍龙环葡韵。",
        "Seng Cheong’s swimming-crab congee near Rua do Cunha is a proper Taipa meal. Share it between two or three, then walk; do not waddle to the Houses overfull.",
        "As papas de caranguejo da Seng Cheong, junto à Rua do Cunha, são refeição a sério. Partilhem dois ou três, e só depois andem; não vão às Casas demasiado cheios.",
        "誠昌の水蟹粥は官也街近くの正餐。二、三人で分けて、おなかいっぱいのまま龍環葡韻へ行かないで。",
    ),
    "tai_lei_loi": S(
        "大利來記豬扒包係氹仔代名詞，現炸厚切夾脆菠蘿包，每日限量。阿濠叫你早啲去，遲咗就只餘香味，故事講完都未食到。",
        "大利来记猪扒包是氹仔代名词，现炸厚切夹脆菠萝包，每日限量。阿濠叫你早点去，迟了就只剩香味，故事讲完都还没吃到。",
        "Tai Lei Loi’s pork-chop bun is Taipa’s nickname in bread: thick, fried to order, limited each day. Go early. Late, you get only the smell, and the story ends before the bite.",
        "O pão de porco da Tai Lei Loi é a Taipa em forma de pão: grosso, frito na hora, limitado. Vai cedo. Tarde, fica o cheiro, e a história acaba sem dentada.",
        "大利来記の猪扒包は氹仔の代名詞。厚切りをその場で揚げ、毎日限り。早めに。遅いと香りだけ、物語が先に終わります。",
    ),
    "taipa_houses": S(
        "龍環葡韻五幢薄荷綠葡式別墅臨湖，前身係葡人官邸。行完官也街過嚟，眼睛由舖面轉去水同百葉窗，氹仔就立體咗。",
        "龙环葡韵五幢薄荷绿葡式别墅临湖，前身是葡人官邸。走完官也街过来，眼睛从铺面转到水和百叶窗，氹仔就立体了。",
        "Five mint Portuguese villas by the water, once officials’ homes, now museums. After the shops, your eyes meet lake and shutters, and Taipa gains a third dimension.",
        "Cinco villas verde-menta à beira do lago, antigas residências, hoje museus. Depois das lojas, os olhos encontram água e persianas, e a Taipa ganha volume.",
        "龍環葡韻はミント色の五棟。もと官邸、いま博物館。店のあと、湖とブラインドで氹仔が立体になります。",
    ),
    "taipa_museum": S(
        "氹仔市政博物館由舊市政廳改成，細但補足氹仔同路環歷史。官也街食完行入嚟十分鐘，故事就唔會淨係停留喺豬扒包。",
        "氹仔市政博物馆由旧市政厅改成，小但补足氹仔和路环历史。官也街吃完走进来十分钟，故事就不会只停在猪扒包。",
        "The Municipal Museum is the old hall, small, filling in Taipa and Coloane history. Ten minutes after the food street, the tale is no longer only a pork-chop bun.",
        "O museu municipal, antigo paços, é pequeno e completa a Taipa e Coloane. Dez minutos depois da rua da comida, a história já não é só pão de porco.",
        "市政博物館は旧庁舎の小さな館。氹仔と路環の歴史を補う。食べたあと十分、物語が猪扒包で終わらない。",
    ),
    "taipa_village": S(
        "氹仔舊城區喺官也街外圍，葡式小屋、窄巷同街坊食店交錯。遊客地圖常常淨畫一條街，阿濠帶你入兩條橫巷，先至係村。",
        "氹仔旧城区在官也街外围，葡式小屋、窄巷和街坊食店交错。游客地图常常只画一条街，阿濠带你进两条横巷，才算是村。",
        "Old Taipa village wraps Rua do Cunha: Portuguese cottages, alleys, neighbourhood kitchens. Maps often draw one street; Ah-Hou takes two side lanes, and then it is a village.",
        "A vila velha envolve a Rua do Cunha: casinhas, ruelas, tascas. Os mapas desenham uma rua; Ah-Hou mete-te em duas travessas, e aí sim é vila.",
        "旧城区は官也街の外側。葡式の小屋、路地、近所の店。地図は一本の通りだけ。横巷を二つ入って、はじめて村です。",
    ),
    "venetian_macau": S(
        "威尼斯人室內運河同拱廊極具辨識度，人流都集中。阿濠唔反對你入去睇一眼，但會講：出到去吸一口舊城空氣，先至記得澳門唔係商場。",
        "威尼斯人室内运河和拱廊极具辨识度，人流都集中。阿濠不反对你进去看一眼，但会说：出去吸一口旧城空气，才记得澳门不是商场。",
        "The Venetian’s indoor canals are unmistakable and crowded. Ah-Hou will not forbid a look; he will say step outside for old-town air, so you remember Macau is not a mall.",
        "Os canais interiores do Venetian são inconfundíveis e cheios. Ah-Hou não te impede de espreitar; pede que saias a respirar o bairro antigo, para Macau não ser um centro comercial.",
        "ベネチアンの室内運河はわかりやすく混む。一目は止めない。外で旧市街の空気を吸って、澳門がモールではないと思い出して。",
    ),
}


def main() -> None:
    pois = json.loads(open(os.path.join(HERE, "pois.json"), encoding="utf-8").read())
    ids = [p["id"] for p in pois]
    missing = [i for i in ids if i not in STORIES]
    extra = [i for i in STORIES if i not in ids]
    if missing or extra:
        raise SystemExit(f"id mismatch missing={missing} extra={extra}")
    for pid, rec in STORIES.items():
        for lang in LANGS:
            text = rec[lang].strip()
            if len(text) < 24:
                raise SystemExit(f"{pid} {lang} too short")
    out = os.path.join(HERE, "stories.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(STORIES, f, ensure_ascii=False, indent=2)
        f.write("\n")
    dest = os.path.join(ROOT, "frontend", "stories.json")
    shutil.copyfile(out, dest)
    print(f"wrote {len(STORIES)} stories -> {out}")
    print(f"copied -> {dest}")


if __name__ == "__main__":
    main()
