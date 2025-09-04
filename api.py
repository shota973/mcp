import requests
import re
import sys

API_SERVER_URL = "http://localhost:11434/api/generate"

def format_result(x):
    return x[12:-1]

def pretty_print(string):
    lines = string.split(r"\n")
    for line in lines:
        print(line)

def main():
    pattern = r'"response":"[^"]*"'
    args = sys.argv
    headers = {"Content-Type": "application/json"}
    json = {
        "model": "deepseek-r1:70b",
        "prompt": """
            # 設定
            あなたは以下に与えられた問題を解く手法を提案するaiエージェントです。
            問題の答えを考えてはいけません。
            ステップバイステップで問題を解く手順のみを出力してください。
            また、手順の中では以下に記載された関数を手順の中で使用、新たな関数の作成ができます。
            既存の関数が問題解決に有効である場合は関数を使用する手順を設け、使用する関数と入力に使用すべきパラメータを記載してください。
            そして、新たな関数が必要であると判断した場合には関数を作成する手順を設け、作成する関数のコードをpythonで記してください。
            # 問題
            以下のメールの内容から予定をタスクに追加して

            ## 内容
            **件名：予定の確認のお願い**

                Dear たなかさん、

                お世話になっております。
                山田です。

                現在、ollamaの講習会を10/10の午後5時から行おうと思っていますが、お時間は取れますでしょうか
                ご都合にあわない場合は、ご自身のご都合の良い日時を教えていただければ幸いです。

                ご確認のほど、どうぞよろしくお願い申し上げます。
                後ほど直接折り返しさせていただきます。

                この度はお手数をおかけしますが、よろしくお願いいたします。

            # 関数
            "functions"{
                "function": {
                    "name": "save_task",
                    "description": "タスクをカレンダーに追加する。deadline_dateはyyyy-mm-dd-hh-mmの形",
                    "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {
                        "type": "string",
                        "description": "タスクの名前"
                        },
                        "deadline_date": {
                        "type": "string",
                        "description": "タスクの期限を示す文字列"
                        }
                    },
                    "required": ["task_name", "deadline_date"]
                    }
                },
                "function": {
                    "name": "letter_counter",
                    "description": "単語の中に文字が何回現れるかを数える。大文字と小文字を区別しない",
                    "parameters": {
                    "type": "object",
                    "properties": {
                        "word": {
                        "type": "string",
                        "description": "分析する単語またはフレーズ"
                        },
                        "letter": {
                        "type": "string",
                        "description": "出現回数を数える文字"
                        }
                    },
                    "required": ["word", "letter"]
                    }
                }
            }
            # 出力例
            ## 問題
            1 + 2 * (3 - 4)の答えはなに？
            ## 使用可能関数
            - sum(x, y): x + yを計算
            - sub(x, y): x - yを計算
            - mult(x, y): x * yを計算
            ## 手順
            1. 3 - 4をsub(3, 4)で計算。この出力結果をr1と呼ぶ
            2. 2と1の出力の積をmult(2, r1)で計算。この出力結果をr2と呼ぶ
            3. 1と2の出力の和をsum(1, r2)で計算""",
    }

    response = requests.post(API_SERVER_URL, headers=headers, json=json)
    repatter = re.compile(pattern)
    result = repatter.findall(response.text)
    result_formated = list(map(format_result, result))
    if len(args) >= 2 and (args[1] == "show_think" or args[1] == "think"):
        pretty_print("".join(result_formated))
    else:
        joined_result = "".join(result_formated)
        pattern_without_think = r'think\\u003e\\n\\n## .*'
        repatter = re.compile(pattern_without_think)
        result = repatter.search(joined_result).group()
        pretty_print(result[15:])

main()  