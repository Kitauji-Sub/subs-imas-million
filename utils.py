import ass
import subdigest
import requests
import json
import os
import shutil
import requests
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter, Retry

def cleanup_ass_file(input_file, output_file):
    with open(input_file, encoding='utf-8-sig', mode='r') as f:
        subs = subdigest.Subtitles(ass.parse(f),"s")
        subs.selection_set("effect", "fx").remove_selected()

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, encoding='utf-8-sig', mode='w+') as f_out:
            subs.dump_file(f_out)

def traditionalize_text(input_text, user_pre_replace="", user_protect_replace="", timeout=10, max_tries=8):
    url = "https://api.zhconvert.org/convert"
    data = {
        "text": input_text,
        "converter": "Taiwan",
        "userPreReplace": user_pre_replace,
        "userProtectReplace": user_protect_replace
    }
    
    retry_strategy = Retry(
        total=max_tries,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    try:
        response = session.post(url, data=data, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        if "data" in result and "text" in result["data"]:
            return result["data"]["text"]
        else:
            raise Exception("Error: Unexpected response format")
    except RequestException as e:
        print(f"Request failed: {e}")
    
    raise Exception("Error: Maximum number of tries exceeded")

def traditionalize_ass(input_file, output_file, user_pre_replace="", user_protect_replace=""):
    with open(input_file, encoding='utf-8-sig', mode='r') as f:
        doc = ass.parse(f)
        new_texts = []
        temp_texts = []
        for i in range(len(doc.events)):
            temp_texts.append(doc.events[i].text)
        print(f"Traditionalizing {input_file}")
        for i in range(0, len(temp_texts), 50):
            print(f"Traditionalizing line {i} to {i+50}...")
            slice_texts = temp_texts[i:i+50]
            slice_texts = json.dumps(slice_texts, ensure_ascii=False)
            traditionalized_slice = traditionalize_text(slice_texts, user_pre_replace, user_protect_replace)
            new_texts += json.loads(traditionalized_slice)
        for i in range(len(new_texts)):
            doc.events[i].text = new_texts[i].replace("思源黑体", "Source Han Sans TC").replace("思源宋体", "Source Han Serif TC").replace("Source Han Sans SC", "Source Han Sans TC").replace("Source Han Serif SC", "Source Han Serif TC").replace("{\\fn思源黑体\\b1\\fs70\\fscx105}䌷","䌷")
            # replace import commands
            if doc.events[i].effect.startswith("import"):
                doc.events[i].text = doc.events[i].text.replace(".ass", "_tc.ass").replace("_sc_tc.ass", "_tc.ass")

        # replace styles if needed
        for i in range(len(doc.styles)):
            if doc.styles[i].fontname == "方正FW筑紫黑 简 E":
                doc.styles[i].fontsize = "75"
                doc.styles[i].bold = "-1"
            doc.styles[i].fontname = doc.styles[i].fontname.replace("方正FW筑紫黑 简 E", "Source Han Sans TC").replace("思源黑体", "Source Han Sans TC").replace("思源宋体", "Source Han Serif TC").replace("Source Han Sans SC", "Source Han Sans TC").replace("Source Han Serif SC", "Source Han Serif TC")

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, encoding='utf-8-sig', mode='w+') as f_out:
            doc.dump_file(f_out)

def traverse_files(folder_path):
    build_dir = os.path.join(folder_path, 'build')
    if os.path.exists(build_dir):
        print("Clean old build dirs...")
        shutil.rmtree(build_dir)
    
    for root, dirs, files in os.walk(folder_path):
        # Skip movies folder
        if "Movies" in root:
            continue
        for file in files:
            if file.endswith(".ass") and not file.endswith("_tc.ass"):
                input_file = os.path.join(root, file)
                output_file = os.path.join(build_dir, os.path.relpath(input_file, folder_path))
                if file.endswith("_sc.ass"):
                    output_tc_file = os.path.join(build_dir, os.path.splitext(os.path.relpath(input_file, folder_path))[0].replace("_sc", "_tc") + ".ass")
                else:
                    output_tc_file = os.path.join(build_dir, os.path.splitext(os.path.relpath(input_file, folder_path))[0] + "_tc.ass")

                print(f'Preprocessing {input_file}...')

                # should directly copy op files
                if file.startswith("op"):
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    shutil.copy(input_file, output_file)
                    shutil.copy(input_file.replace("_sc", "_tc"), output_file.replace("_sc", "_tc"))
                    continue

                cleanup_ass_file(input_file, output_file)
                traditionalize_ass(output_file, output_tc_file, user_pre_replace='艾米莉=艾蜜莉\n斯图亚特=司徒亚特\n试镜=甄选会\n埃琳娜=艾琳娜\n百万现场=百万人演唱会', user_protect_replace='华康翩翩体\n獅尾圓體')

def merge_files(input_file, output_file):
    with open(input_file, encoding='utf-8-sig', mode='r') as f:
        subs = subdigest.Subtitles(ass.parse(f),"s")
        subs.ms_import_rc()

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, encoding='utf-8-sig', mode='w+') as f_out:
            subs.dump_file(f_out)
