from __future__ import annotations

from pathlib import Path

VERSION_PLACEHOLDER = "${version}"

FONT_REPLACEMENTS = {
    "方正FW筑紫黑 简 E": "Source Han Sans TC",
    "思源黑体": "Source Han Sans TC",
    "思源宋体": "Source Han Serif TC",
    "Source Han Sans SC": "Source Han Sans TC",
    "Source Han Serif SC": "Source Han Serif TC",
}

USER_PRE_REPLACE = (
    "艾米莉=艾蜜莉\n"
    "斯图亚特=司徒亚特\n"
    "试镜=甄选会\n"
    "埃琳娜=艾琳娜\n"
    "百万现场=百万人演唱会"
)

USER_PROTECT_REPLACE = "华康翩翩体\n獅尾圓體"

SKIP_DIR_NAMES = {
    ".git",
    ".ace-tool",
    "__pycache__",
    "aegisub-cli",
    "build",
    "ep.template",
}

SPEAKER_COLORS = {
    "anna": {"outline": "&H00976171&", "shadow": "&H00A86C7E&"},
    "bba": {"outline": "&H009987C8&", "shadow": "&H00CBBEF1&"},
    "elena": {"outline": "&H00577B5C&", "shadow": "&H0092CE9B&"},
    "miki": {"outline": "&H002C866B&", "shadow": "&H004BE0B4&"},
    "yayoi": {"outline": "&H00225B91&", "shadow": "&H003999F3&"},
    "丽花": {"outline": "&H00696D40&", "shadow": "&H00B0B66B&"},
    "亚美真美": {"outline": "&H00258899&", "shadow": "&H003FE4FF&"},
    "可怜": {"outline": "&H003935A3&", "shadow": "&H00403BB6&"},
    "咯吱": {"outline": "&H006C3923&", "shadow": "&H00794027&"},
    "女儿": {"outline": "&H00A781D5&", "shadow": "&H00BA90ED&"},
    "日向": {"outline": "&H00272EBC&", "shadow": "&H002C34D1&"},
    "梓": {"outline": "&H00AB3283&", "shadow": "&H00BE3892&"},
    "环": {"outline": "&H00296AD6&", "shadow": "&H002E76EE&"},
    "美也": {"outline": "&H00406581&", "shadow": "&H006BA9D7&"},
    "翼": {"outline": "&H00378DAA&", "shadow": "&H0052D5FE&"},
    "茜": {"outline": "&H003857D3&", "shadow": "&H003F61EB&"},
    "风花": {"outline": "&H00976B66&", "shadow": "&H00A87872&"},
    "72": {"outline": "&H00BD4324&", "shadow": "&H00D24327&"},
    "julia": {"outline": "&H005532C1&", "shadow": "&H005F38D7&"},
    "roco": {"outline": "&H00248F99&", "shadow": "&H003CF0FF&"},
    "伊织": {"outline": "&H00BD80D5&", "shadow": "&H00D38FED&"},
    "千鹤": {"outline": "&H004E86D8&", "shadow": "&H005795F1&"},
    "律子": {"outline": "&H00396400&", "shadow": "&H0060A801&"},
    "所惠美": {"outline": "&H00262829&", "shadow": "&H00414345&"},
    "昴": {"outline": "&H005D6C68&", "shadow": "&H009CB4AE&"},
    "朋花": {"outline": "&H00888871&", "shadow": "&H00E3E3BE&"},
    "条纹人": {"outline": "&H00566369&", "shadow": "&H0090A6AF&"},
    "桃子": {"outline": "&H003C6E8F&", "shadow": "&H0064B8EF&"},
    "步": {"outline": "&H008B51CB&", "shadow": "&H009B5AE2&"},
    "瑞希": {"outline": "&H00B4967D&", "shadow": "&H00DCB799&"},
    "紬": {"outline": "&H00B9A4AA&", "shadow": "&H00FFE1EB&"},
    "莉绪": {"outline": "&H008286D8&", "shadow": "&H009195F1&"},
    "贵音": {"outline": "&H005F1095&", "shadow": "&H006A12A6&"},
    "静香": {"outline": "&H00BA865A&", "shadow": "&H00CF9564&"},
    "arisa": {"outline": "&H00573DA2&", "shadow": "&H006144B5&"},
    "emily": {"outline": "&H00653A4C&", "shadow": "&H00714155&"},
    "可胖": {"outline": "&H00236793&", "shadow": "&H003BADF5&"},
    "响": {"outline": "&H006E6700&", "shadow": "&H00B9AD01&"},
    "奈绪": {"outline": "&H00B17D6C&", "shadow": "&H00C58B78&"},
    "未来": {"outline": "&H006A51D2&", "shadow": "&H00765BEA&"},
    "法子": {"outline": "&H00438C8D&", "shadow": "&H0070EBEC&"},
    "海美": {"outline": "&H008B67D1&", "shadow": "&H009B73E9&"},
    "琴皇": {"outline": "&H00707C57&", "shadow": "&H00BBCF92&"},
    "百合子": {"outline": "&H00236E77&", "shadow": "&H003CB8C7&"},
    "真哥": {"outline": "&H00343230&", "shadow": "&H00585551&"},
    "纱代子": {"outline": "&H00695A72&", "shadow": "&H0075657F&"},
    "美奈子": {"outline": "&H00846334&", "shadow": "&H00DCA658&"},
    "育": {"outline": "&H00558A94&", "shadow": "&H008EE7F7&"},
    "阁下": {"outline": "&H002B26CB&", "shadow": "&H00302BE2&"},
    "雪步": {"outline": "&H00B99774&", "shadow": "&H00E9DDD3&"},
    "马自立": {"outline": "&H006D7236&", "shadow": "&H00B7BF5A&"},
    "小鸟": {"outline": "&H00629399&", "shadow": "&H00A4F6FF&"},
    "早坂空": {"outline": "&H002E8451&", "shadow": "&H004EDC88&"},
    "社长": {"outline": "&H006C6C6C&", "shadow": "&H03797979&"},
    "美咲": {"outline": "&H0085875A&", "shadow": "&H00DFE296&"},
    "赤P源P": {"outline": "&H007B454D&", "shadow": "&H00894D56&"},
}

TEXT_GENERIC_STYLES = [
    "Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1",
    "Style: Text_Bottom,方正FW筑紫黑 简 E,65,&H00F0F0F0,&H000000FF,&H00505050,&H00000000,0,0,0,0,100,100,1.1,0,1,3.5,0.3,2,10,10,30,1",
    "Style: Text_Top,方正FW筑紫黑 简 E,65,&H00F0F0F0,&H000000FF,&H00505050,&H00000000,0,0,0,0,100,100,1.1,0,1,3.5,0.3,8,10,10,30,1",
    "Style: 注释,思源黑体,45,&H00F0F0F0,&H000000FF,&H002F2F2F,&H00000000,-1,0,0,0,100,100,1.1,0,1,3,0,7,10,10,30,1",
    "Style: Title,思源黑体,30,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,2,10,10,10,1",
    "Style: OnScreen,思源黑体,40,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,2,10,10,10,1",
]

ROOT_DIR = Path(__file__).resolve().parents[1]
