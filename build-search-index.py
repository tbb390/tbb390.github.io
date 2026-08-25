import os
import re
import json
from html.parser import HTMLParser


# =========================
# 配置
# =========================

NOTE_DIR = "daily-study"

OUTPUT_FILE = "search-index.json"



# =========================
# HTML解析器
# =========================

class TextParser(HTMLParser):

    def __init__(self):

        super().__init__()

        self.text = []


    def handle_data(self, data):

        data = data.strip()

        if data:

            self.text.append(data)



def extract_text(html):

    """
    提取HTML中的纯文本
    """

    parser = TextParser()

    parser.feed(html)

    return " ".join(parser.text)





# =========================
# 获取标题
# =========================

def extract_title(html, day):


    # 优先读取title标签

    result = re.search(
        r"<title>(.*?)</title>",
        html,
        re.I | re.S
    )


    if result:


        title = result.group(1)


        title = re.sub(
            r"\s+",
            " ",
            title
        )


        title = title.strip()


        if title:

            return title




    # 没有title

    # 默认名称

    return f"第 {day} 天学习记录"






# =========================
# 生成索引
# =========================

def build_index():


    index = []



    if not os.path.exists(NOTE_DIR):


        print(
            f"错误：不存在目录 {NOTE_DIR}"
        )

        return





    files = os.listdir(NOTE_DIR)



    for filename in files:



        # 匹配 day数字note.html

        match = re.match(
            r"day(\d+)note\.html",
            filename,
            re.I
        )


        if not match:


            continue





        day = int(
            match.group(1)
        )



        filepath = os.path.join(
            NOTE_DIR,
            filename
        )



        try:


            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as f:


                html = f.read()



        except Exception as e:


            print(
                f"读取失败: {filename}",
                e
            )


            continue





        title = extract_title(
            html,
            day
        )



        content = extract_text(
            html
        )



        item = {


            "day": day,


            "title": title,


            "content": content,


            "file":
            f"{NOTE_DIR}/{filename}"

        }



        index.append(item)



        print(
            f"完成: Day {day}"
        )






    # 按Day排序

    index.sort(
        key=lambda x:x["day"]
    )





    # 输出JSON

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(

            index,

            f,

            ensure_ascii=False,

            indent=2

        )





    print("\n===================")

    print("搜索索引生成完成")

    print(
        f"共收录 {len(index)} 篇笔记"
    )

    print(
        f"生成文件: {OUTPUT_FILE}"
    )

    print("===================")






# =========================
# 程序入口
# =========================

if __name__ == "__main__":

    build_index()