script_name = ("Pangu - 自动插入空白")
script_description = ("自动在选中行中将所有的中文与半角英文、数字、符号之间插入空白")
script_author = "Scrpr"
script_version = "2"

re = require 'aegisub.re'
unicode = require 'aegisub.unicode'

CUSTOM_SPACE = [[{\\fscx50} {\\fscx100}]]
-- SPACE_SPACED = [[\\{\\\\fscx25\}　\\{\\\\fscx100\\}]]
SPACE = [[ YJSP ㋿ ]]
SPACE_SPACED = [[YJSP ㋿]]

CJK = [[⺀-⻿⼀-⿟぀-ゟ゠-ヺー-ヿ㄀-ㄯ㈀-㋿㐀-䶿一-鿿豈-﫿]]
-- CJK = [[123]]

ANY_CJK = re.compile(string.format('[%s]', CJK))

CONVERT_TO_FULLWIDTH_CJK_SYMBOLS_CJK = re.compile(string.format('([%s])([ ]*[~\\!;,\\?]+[ ]*)([%s])', CJK, CJK))
CONVERT_TO_FULLWIDTH_CJK_SYMBOLS = re.compile(string.format('([%s])([ ]*[~\\!;,\\?]+[ ]*)', CJK))
DOTS_CJK = re.compile(string.format('([\\.]{2,}|…)([%s])', CJK))
FIX_CJK_COLON_ANS = re.compile(string.format('([%s])\\:([A-Z0-9\\(\\)])', CJK))

CJK_QUOTE = re.compile(string.format('([%s])([`"״])', CJK))
QUOTE_CJK = re.compile(string.format('([`"״])([%s])', CJK))
FIX_QUOTE_ANY_QUOTE = re.compile(string.format('([`"״]+)(?:[ ]|'..SPACE_SPACED..')*(.+?)(?:[ ]|'..SPACE_SPACED..')*([`"״]+)'))

CJK_SINGLE_QUOTE_BUT_POSSESSIVE = re.compile(string.format([[([%s])('[^s])]], CJK))
SINGLE_QUOTE_CJK = re.compile(string.format([[(')([%s])]], CJK))
FIX_POSSESSIVE_SINGLE_QUOTE = re.compile(string.format([[([A-Za-z0-9%s])(?: |]]..SPACE_SPACED..[[)('s)]], CJK))

HASH_ANS_CJK_HASH = re.compile(string.format('([%s])(#)([%s]+)(#)([%s])', CJK, CJK, CJK))
CJK_HASH = re.compile(string.format('([%s])(#([^ ]))', CJK))
HASH_CJK = re.compile(string.format('(([^ ])#)([%s])', CJK))

CJK_OPERATOR_ANS = re.compile(string.format('([%s])([\\+\\-\\*\\/=&\\|<>])([A-Za-z0-9])', CJK))
ANS_OPERATOR_CJK = re.compile(string.format('([A-Za-z0-9])([\\+\\-\\*\\/=&\\|<>])([%s])', CJK))

FIX_SLASH_AS = re.compile(string.format([[([/]) ([a-z\-_\./]+)]]))
FIX_SLASH_AS_SLASH = re.compile(string.format([[([/\.])([A-Za-z\-_\./]+) ([/])]]))

CJK_LEFT_BRACKET = re.compile(string.format('([%s])([\\(\\[\\{<>“])', CJK))
RIGHT_BRACKET_CJK = re.compile(string.format('([\\)\\]\\}<>”])([%s])', CJK))
FIX_LEFT_BRACKET_ANY_RIGHT_BRACKET = re.compile(string.format([[([\(\[\{<“]+)(?:[ ]|]]..SPACE_SPACED..[[)*(.+?)(?:[ ]|]]..SPACE_SPACED..[[)*([\)\]\}>”]+)]]))
ANS_CJK_LEFT_BRACKET_ANY_RIGHT_BRACKET = re.compile(string.format('([A-Za-z0-9%s])(?:[ ]|'..SPACE_SPACED..')*([“])([A-Za-z0-9%s\\-_ ]+)([”])', CJK, CJK))
LEFT_BRACKET_ANY_RIGHT_BRACKET_ANS_CJK = re.compile(string.format('([“])([A-Za-z0-9%s\\-_ ]+)([”])(?:[ ]|'..SPACE_SPACED..')*([A-Za-z0-9%s])', CJK, CJK))

AN_LEFT_BRACKET = re.compile(string.format([[([A-Za-z0-9])([\(\[\{])]]))
RIGHT_BRACKET_AN = re.compile(string.format([[([\)\]\}])([A-Za-z0-9])]]))

ANS = [[([A-Za-zͰ-Ͽ0-9@\\$%\\^&\\*\\-\\+\\\\=\\|/¡-ÿ⅐-↏✀—➿])]]
CJK_ANS = re.compile(string.format('([%s])', CJK)..ANS)
ANS_CJK = re.compile(ANS..string.format('([%s])', CJK))

S_A = re.compile([[(%)([A-Za-z])]])

MIDDLE_DOT = re.compile([[((?:[ ]|]]..SPACE_SPACED..[[)*)([·•‧])((?:[ ]|]]..SPACE_SPACED..[[)*)]])

INLINE_TAGS = re.compile('(\\\\[Nnh])(?:[ ]|'..SPACE_SPACED..')*')

function convertToFullWidth_CJK(symbols)
    --- aegisub.debug.out("Processing symbol"..symbols.."\n")

    new_symbols = re.sub(symbols, "~", "～")
    --- aegisub.debug.out(new_symbols.."\n")
    new_symbols = re.sub(new_symbols, "!", "！")
    --- aegisub.debug.out(new_symbols.."\n")
    new_symbols = re.sub(new_symbols,";", "；")
    --- aegisub.debug.out(new_symbols.."\n")
    new_symbols = re.sub(new_symbols, ":", "：")
    --- aegisub.debug.out(new_symbols.."\n")
    new_symbols = re.sub(new_symbols, ",", "，")
    --- aegisub.debug.out(new_symbols.."\n")
    new_symbols = re.sub(new_symbols, "\\.", "。")
    --- aegisub.debug.out(new_symbols.."\n")
    new_symbols = re.sub(new_symbols, "\\?", "？")
    --- aegisub.debug.out(new_symbols.."\n")
    new_symbols = re.sub(new_symbols, " ", "")
    --- aegisub.debug.out(new_symbols.."\n")

    return new_symbols
end

function convertToFullWidth(symbols)
    --- aegisub.debug.out("Processing symbol"..symbols.."\n")

    new_symbols = re.sub(symbols, "~", "～")
    --- aegisub.debug.out(new_symbols.."\n")
    new_symbols = re.sub(new_symbols, "!", "！")
    --- aegisub.debug.out(new_symbols.."\n")
    new_symbols = re.sub(new_symbols,";", "；")
    --- aegisub.debug.out(new_symbols.."\n")
    new_symbols = re.sub(new_symbols, ":", "：")
    --- aegisub.debug.out(new_symbols.."\n")
    new_symbols = re.sub(new_symbols, ",", "，")
    --- aegisub.debug.out(new_symbols.."\n")
    new_symbols = re.sub(new_symbols, "\\.", "。")
    --- aegisub.debug.out(new_symbols.."\n")
    new_symbols = re.sub(new_symbols, "\\?", "？")
    --- aegisub.debug.out(new_symbols.."\n")
    new_symbols = re.sub(new_symbols, "^ ", "")
    --- aegisub.debug.out(new_symbols.."\n")

    return new_symbols
end

function spacing(text)
    if (type(text) ~= "string") then
        aegisub.debug.out(2, string.format("spacing(text) only accepts string but got %s", type(text)).."\n")
        return text
    end

    if (string.len(text) <= 1 or ANY_CJK:find(text) == nil) then
        return text
    end

    new_text = text

    new_text = CONVERT_TO_FULLWIDTH_CJK_SYMBOLS_CJK:sub(new_text, convertToFullWidth_CJK)
    new_text = CONVERT_TO_FULLWIDTH_CJK_SYMBOLS:sub(new_text, convertToFullWidth)
    -- aegisub.debug.out("CONVERT_TO_FULLWIDTH_CJK_SYMBOLS"..new_text.."\n")
    new_text = DOTS_CJK:sub(new_text, "\\1"..SPACE.."\\2")
    --- aegisub.debug.out("DOTS_CJK"..new_text.."\n")
    new_text = FIX_CJK_COLON_ANS:sub(new_text, "\\1：\\2")
    --- aegisub.debug.out("FIX_CJK_COLON_ANS"..new_text.."\n")

    new_text = CJK_QUOTE:sub(new_text, "\\1"..SPACE.."\\2")
    --- aegisub.debug.out("CJK_QUOTE"..new_text.."\n")
    new_text = QUOTE_CJK:sub(new_text, "\\1"..SPACE.."\\2")
    --- aegisub.debug.out("QUOTE_CJK"..new_text.."\n")
    new_text = FIX_QUOTE_ANY_QUOTE:sub(new_text, "\\1\\2\\3")
    --- aegisub.debug.out("FIX_QUOTE_ANY_QUOTE"..new_text.."\n")

    new_text = CJK_SINGLE_QUOTE_BUT_POSSESSIVE:sub(new_text, "\\1"..SPACE.."\\2")
    --- aegisub.debug.out("CJK_SINGLE_QUOTE_BUT_POSSESSIVE"..new_text.."\n")
    new_text = SINGLE_QUOTE_CJK:sub(new_text, "\\1"..SPACE.."\\2")
    --- aegisub.debug.out("SINGLE_QUOTE_CJK"..new_text.."\n")
    new_text = FIX_POSSESSIVE_SINGLE_QUOTE:sub(new_text, "\\1's")
    --- aegisub.debug.out("FIX_POSSESSIVE_SINGLE_QUOTE"..new_text.."\n")

    new_text = HASH_ANS_CJK_HASH:sub(new_text, "\\1"..SPACE.."\\2\\3\\4"..SPACE.."\\5")
    --- aegisub.debug.out("HASH_ANS_CJK_HASH"..new_text.."\n")
    new_text = CJK_HASH:sub(new_text, "\\1"..SPACE.."\\2")
    --- aegisub.debug.out("CJK_HASH"..new_text.."\n")
    new_text = HASH_CJK:sub(new_text, "\\1"..SPACE.."\\3")
    --- aegisub.debug.out("HASH_CJK"..new_text.."\n")

    new_text = CJK_OPERATOR_ANS:sub(new_text, "\\1"..SPACE.."\\2"..SPACE.."\\3")
    --- aegisub.debug.out("CJK_OPERATOR_ANS"..new_text.."\n")
    new_text = ANS_OPERATOR_CJK:sub(new_text, "\\1"..SPACE.."\\2"..SPACE.."\\3")
    --- aegisub.debug.out("ANS_OPERATOR_CJK"..new_text.."\n")

    new_text = FIX_SLASH_AS:sub(new_text, "\\1\\2")
    --- aegisub.debug.out("FIX_SLASH_AS"..new_text.."\n")
    new_text = FIX_SLASH_AS_SLASH:sub(new_text, "\\1\\2\\3")
    --- aegisub.debug.out("FIX_SLASH_AS_SLASH"..new_text.."\n")

    new_text = CJK_LEFT_BRACKET:sub(new_text, "\\1"..SPACE.."\\2")
    --- aegisub.debug.out("CJK_LEFT_BRACKET"..new_text.."\n")
    new_text = RIGHT_BRACKET_CJK:sub(new_text, "\\1"..SPACE.."\\2")
    --- aegisub.debug.out("RIGHT_BRACKET_CJK"..new_text.."\n")
    new_text = FIX_LEFT_BRACKET_ANY_RIGHT_BRACKET:sub(new_text, "\\1\\2\\3")
    --- aegisub.debug.out("FIX_LEFT_BRACKET_ANY_RIGHT_BRACKET"..new_text.."\n")
    new_text = ANS_CJK_LEFT_BRACKET_ANY_RIGHT_BRACKET:sub(new_text, "\\1"..SPACE.."\\2\\3\\4")
    --- aegisub.debug.out("ANS_CJK_LEFT_BRACKET_ANY_RIGHT_BRACKET"..new_text.."\n")
    new_text = LEFT_BRACKET_ANY_RIGHT_BRACKET_ANS_CJK:sub(new_text, "\\1\\2\\3"..SPACE.."\\4")
    --- aegisub.debug.out("LEFT_BRACKET_ANY_RIGHT_BRACKET_ANS_CJK"..new_text.."\n")

    new_text = AN_LEFT_BRACKET:sub(new_text, "\\1"..SPACE.."\\2")
    --- aegisub.debug.out("AN_LEFT_BRACKET"..new_text.."\n")
    new_text = RIGHT_BRACKET_AN:sub(new_text, "\\1"..SPACE.."\\2")
    --- aegisub.debug.out("RIGHT_BRACKET_AN"..new_text.."\n")

    new_text = CJK_ANS:sub(new_text, "\\1"..SPACE.."\\2")
    --- aegisub.debug.out("CJK_ANS"..new_text.."\n")
    new_text = ANS_CJK:sub(new_text, "\\1"..SPACE.."\\2")
    --- aegisub.debug.out("ANS_CJK"..new_text.."\n")

    new_text = S_A:sub(new_text, "\\1"..SPACE.."\\2")
    --- aegisub.debug.out("S_A"..new_text.."\n")

    new_text = MIDDLE_DOT:sub(new_text, "・")
    --- aegisub.debug.out("MIDDLE_DOT"..new_text.."\n")
    new_text = INLINE_TAGS:sub(new_text, "\\1")

    return new_text
end



function processing(subtitles, selected_lines, active_line)
    ASS_TAGS = re.compile([[[^\{\}]*(?=(?:[^\}]*\{[^\{]*\})*[^\{\}]*$)]])
    LAST_PROCESSED = re.compile(CUSTOM_SPACE)
    ADD_CUSTOM = re.compile(SPACE.."?")
    for z, i in ipairs(selected_lines) do
        local l = subtitles[i]
        line_new_text = LAST_PROCESSED:sub(l.text, "")
        line_new_text = ASS_TAGS:sub(line_new_text, spacing)
        -- aegisub.debug.out("New text is "..line_new_text)
        line_new_text = ADD_CUSTOM:sub(line_new_text, CUSTOM_SPACE)
        l.text = line_new_text
        subtitles[i] = l
    end
    aegisub.set_undo_point("Pangu")
end

aegisub.register_macro(script_name, "Automatic CJK text spacing", processing)