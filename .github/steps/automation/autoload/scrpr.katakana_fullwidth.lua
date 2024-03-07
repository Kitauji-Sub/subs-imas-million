script_name = ("Make Katakana Fullwidth - 转换为全角片假")
script_description = ("将选中行内半角片假名转换为全角片假名")
script_author = "Scrpr"
script_version = "3"

include("unicode.lua")


lookup = {
    ['ｦ'] = 'ヲ',
    ['ｧ'] = 'ァ',
    ['ｨ'] = 'ィ',
    ['ｩ'] = 'ゥ',
    ['ｪ'] = 'ェ',
    ['ｫ'] = 'ォ',
    ['ｬ'] = 'ャ',
    ['ｭ'] = 'ュ',
    ['ｮ'] = 'ョ',
    ['ｯ'] = 'ッ',
    ['ｰ'] = 'ー',
    ['ｱ'] = 'ア',
    ['ｲ'] = 'イ',
    ['ｳ'] = 'ウ',
    ['ｴ'] = 'エ',
    ['ｵ'] = 'オ',
    ['ｶ'] = 'カ',
    ['ｷ'] = 'キ',
    ['ｸ'] = 'ク',
    ['ｹ'] = 'ケ',
    ['ｺ'] = 'コ',
    ['ｻ'] = 'サ',
    ['ｼ'] = 'シ',
    ['ｽ'] = 'ス',
    ['ｾ'] = 'セ',
    ['ｿ'] = 'ソ',
    ['ﾀ'] = 'タ',
    ['ﾁ'] = 'チ',
    ['ﾂ'] = 'ツ',
    ['ﾃ'] = 'テ',
    ['ﾄ'] = 'ト',
    ['ﾅ'] = 'ナ',
    ['ﾆ'] = 'ニ',
    ['ﾇ'] = 'ヌ',
    ['ﾈ'] = 'ネ',
    ['ﾉ'] = 'ノ',
    ['ﾊ'] = 'ハ',
    ['ﾋ'] = 'ヒ',
    ['ﾌ'] = 'フ',
    ['ﾍ'] = 'ヘ',
    ['ﾎ'] = 'ホ',
    ['ﾏ'] = 'マ',
    ['ﾐ'] = 'ミ',
    ['ﾑ'] = 'ム',
    ['ﾒ'] = 'メ',
    ['ﾓ'] = 'モ',
    ['ﾔ'] = 'ヤ',
    ['ﾕ'] = 'ユ',
    ['ﾖ'] = 'ヨ',
    ['ﾗ'] = 'ラ',
    ['ﾘ'] = 'リ',
    ['ﾙ'] = 'ル',
    ['ﾚ'] = 'レ',
    ['ﾛ'] = 'ロ',
    ['ﾜ'] = 'ワ',
    ['ﾝ'] = 'ン',
}

special = {
    ['ｶﾞ'] = 'ガ',
    ['ｷﾞ'] = 'ギ',
    ['ｸﾞ'] = 'グ',
    ['ｹﾞ'] = 'ゲ',
    ['ｺﾞ'] = 'ゴ',
    ['ｻﾞ'] = 'ザ',
    ['ｼﾞ'] = 'ジ',
    ['ｽﾞ'] = 'ズ',
    ['ｾﾞ'] = 'ゼ',
    ['ｿﾞ'] = 'ゾ',
    ['ﾀﾞ'] = 'ダ',
    ['ﾁﾞ'] = 'ヂ',
    ['ﾂﾞ'] = 'ヅ',
    ['ﾃﾞ'] = 'デ',
    ['ﾄﾞ'] = 'ド',
    ['ﾊﾞ'] = 'バ',
    ['ﾋﾞ'] = 'ビ',
    ['ﾌﾞ'] = 'ブ',
    ['ﾍﾞ'] = 'ベ',
    ['ﾎﾞ'] = 'ボ',
    ['ﾊﾟ'] = 'パ',
    ['ﾋﾟ'] = 'ピ',
    ['ﾌﾟ'] = 'プ',
    ['ﾍﾟ'] = 'ペ',
    ['ﾎﾟ'] = 'ポ',
}

bad = {
    ['カﾞ'] = 'ガ',
    ['キﾞ'] = 'ギ',
    ['クﾞ'] = 'グ',
    ['ケﾞ'] = 'ゲ',
    ['コﾞ'] = 'ゴ',
    ['サﾞ'] = 'ザ',
    ['シﾞ'] = 'ジ',
    ['スﾞ'] = 'ズ',
    ['セﾞ'] = 'ゼ',
    ['ソﾞ'] = 'ゾ',
    ['タﾞ'] = 'ダ',
    ['チﾞ'] = 'ヂ',
    ['ツﾞ'] = 'ヅ',
    ['テﾞ'] = 'デ',
    ['トﾞ'] = 'ド',
    ['ハﾞ'] = 'バ',
    ['ヒﾞ'] = 'ビ',
    ['フﾞ'] = 'ブ',
    ['ヘﾞ'] = 'ベ',
    ['ホﾞ'] = 'ボ',
    ['ハﾟ'] = 'パ',
    ['ヒﾟ'] = 'ピ',
    ['フﾟ'] = 'プ',
    ['ヘﾟ'] = 'ペ',
    ['ホﾟ'] = 'ポ',
}

function make_fullwidth(subtitles, selected_lines, active_line)
	for z, i in ipairs(selected_lines) do
		local l = subtitles[i]

        for k, v in pairs(special) do
            l.text = string.gsub(l.text, k, v)
        end

        for k, v in pairs(bad) do
            l.text = string.gsub(l.text, k, v)
        end
		
		-- aegisub.debug.out(string.format('Processing line %d: "%s"\n', i, l.text))
		-- aegisub.debug.out("Chars: \n")
		
		local in_tags = false
		local newtext = ""
		for c in unicode.chars(l.text) do
			-- aegisub.debug.out(c .. ' -> ')
			if c == "{" then
				in_tags = true
			end
			if in_tags then
				-- aegisub.debug.out(c .. " (ignored, in tags)\n")
				newtext = newtext .. c
			else
				if lookup[c] then
					-- aegisub.debug.out(lookup[c] .. " (converted)\n")
					newtext = newtext .. lookup[c]
				else
					-- aegisub.debug.out(c .. " (not found in lookup)\n")
					newtext = newtext .. c
				end
			end
			if c == "}" then
				in_tags = false
			end
		end
		
		l.text = newtext
		subtitles[i] = l
	end
	aegisub.set_undo_point("Make fullwidth")
end

aegisub.register_macro(script_name, "将选中行内半角片假名转换为全角片假名", make_fullwidth)
