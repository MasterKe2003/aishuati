import os
import json
import time
import requests


# 读取题目函数
def read_questions_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        # 以空行分隔题目，假设题目之间有空行
        questions = f.read().strip().split("\n\n")
    return questions


# 向ChatGPT发送请求并获取JSON格式的响应
def get_question_json_from_chatgpt(question):
    api_url = "https://oneapi.masterke.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "",  # 请使用自己的API Key
    }
    prompt = f"""
    请根据{question}提取出一个标准的题目格式输出，格式如下，如果是判断题就是A正确，B错误，如果是简答题就是空列表，请确保生成的内容仅包含要求的文本，且不要返回其他内容例如markdown中的```以及空格换行等等。
    {{"id": "当前时间戳","title": "题目","option": ["A选项", "B选项", "C选项", "D选项"],"answer": "正确答案","analysis": "解析"}}
    
    """
    payload = {
        "model": "glm-4-plus",
        "messages": [
            {
                "role": "system",
                "content": "你是一个助理，负责生成标准格式的选择题题目和答案，请确保生成的内容仅包含要求的文本，且不要返回其他内容例如markdown中的```以及空格换行等等。",
            },
            {
                "role": "user",
                "content": prompt,
            }
        ]
    }

    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            json_response = response.json()
            content = json_response["choices"][0]["message"]["content"]
            print(f"响应内容: {content}")
            # 这里假设返回的是标准的JSON格式，如果返回不正确，可能需要再做一些清洗工作
            return json.loads(content)
        except Exception as e:
            print(f"解析JSON失败: {e}")
            return get_question_json_from_chatgpt(question)
    else:
        print(f"API请求失败，状态码: {response.status_code}")
        print(f"响应内容: {response.json()['choices'][0]['message']['content']}")
        return None


# 保存JSON文件的函数
def save_questions_to_json(questions_json, file_name):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(questions_json, f, ensure_ascii=False, indent=4)
    print(f"JSON文件已保存到: {file_name}")


# 主逻辑
def main():
    # 读取题目
    questions = read_questions_from_file("D://aishuati/py-timuToJson/timu.txt")

    all_questions_json = []
    timestamp = str(int(time.time()))  # 获取当前时间戳
    file_name = f"json/{timestamp}.json"

    # 确保json文件夹存在
    if not os.path.exists("json"):
        os.makedirs("json")

    for idx, question in enumerate(questions, start=1):
        print(f"正在处理第 {idx} 道题目：{question}")
        question_json = get_question_json_from_chatgpt(question)
        if question_json:
            all_questions_json.append(question_json)
            # 每次处理完一个题目后就保存文件，防止中断
            save_questions_to_json(all_questions_json, file_name)

    # 最后保存所有题目
    if all_questions_json:
        print(f"所有题目处理完成，总共{len(all_questions_json)}道题目。")
        save_questions_to_json(all_questions_json, file_name)


if __name__ == "__main__":
    main()
