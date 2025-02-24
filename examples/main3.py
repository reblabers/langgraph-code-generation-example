# Agentを使ってツールを呼び出す (不完全)

from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from typing import Annotated
from langchain.agents import OpenAIFunctionsAgent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import AgentExecutor, create_openai_functions_agent

from langchain.tools import BaseTool, StructuredTool, Tool, tool

CLAUDE_3_HAIKU = "us.anthropic.claude-3-haiku-20240307-v1:0"
CLAUDE_3_5_SONNET = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

from credentials import get_credentials

import os
from dotenv import load_dotenv

# .envファイルのパスを指定して読み込む
load_dotenv('.env')

AWS_ACCOUNT_ID = os.environ['AWS_ACCOUNT_ID']
SYSTEM_ADMIN_ROLE = os.environ['SYSTEM_ADMIN_ROLE']
credentials = get_credentials(AWS_ACCOUNT_ID, SYSTEM_ADMIN_ROLE)


# toolの定義
@tool
def add(
    a: Annotated[int, '一つ目の値'],
    b: Annotated[int, '二つ目の値'],
) -> int:
    """2つの値を足し算して返す"""
    return a + b

# プロンプトの定義
prompt = ChatPromptTemplate.from_messages(
    [
        ('system', '与えられたinputに従って計算処理を呼び出してください'),
        # ('placeholder', '{messages}'),
        # ("system", "You are a helpful assistant"),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
    
)

tools = [StructuredTool.from_function(add)]




# llm = ChatBedrock(
#     model_id=CLAUDE_3_HAIKU,
#     # model_id=CLAUDE_3_5_SONNET,
#     aws_access_key_id=credentials.access_key_id,
#     aws_secret_access_key=credentials.secret_access_key,
#     aws_session_token=credentials.session_token,
#     region_name="us-east-1",
#     # model_kwargs={"maxTokenCount": 512, "temperature": 0.7},
# )



# from langchain.agents import Tool

# # tools = load_tools([add], llm=llm)
# tools = load_tools([])

# tools.append(
#     Tool(
#         name="add",
#         func=add,
#         description="useful for when you need to answer questions about add"
#     ),
# )

# agent = create_openai_functions_agent(llm, tools, prompt)
# agent_executor = AgentExecutor(agent=agent, tools=tools)

# response = agent_executor.invoke({"input": "3 + 4の計算結果は？"})
# print(response)

# agent_executor = AgentExecutor(agent=agent, tools=[add], verbose=True)
# # エージェントの作成
# agent = create_react_agent(
#     model=llm,
#     tools=[add],
#     state_modifier=prompt,
# )

# # エージェントの実行
# result = agent.invoke({'messages': ['3 + 4の計算結果は？']})
# print(result['messages'][-1].content)
# # => 3 + 4の計算結果は7です。

# print(result)

# AWS_ACCOUNT_ID = os.environ['AWS_ACCOUNT_ID']
# SYSTEM_ADMIN_ROLE = os.environ['SYSTEM_ADMIN_ROLE']

# # Get temporary credentials
# session = boto3.Session(profile_name=SYSTEM_ADMIN_ROLE)
# sts_client = session.client("sts")
# assumed_role_object = sts_client.assume_role(
#     RoleArn=f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/power_role",
#     RoleSessionName="LANGCHAIN-POWER-ROLE"
# )
# credentials = assumed_role_object['Credentials']

# # Initialize the Bedrock LLM
# llm = ChatBedrock(
#     model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
#     aws_access_key_id=credentials['AccessKeyId'],
#     aws_secret_access_key=credentials['SecretAccessKey'],
#     aws_session_token=credentials['SessionToken'],
#     region_name="us-east-1",  # ご利用のリージョンに変更してください
#     # model_kwargs={"maxTokenCount": 512, "temperature": 0.7},
# )

# # Load Finder.kt from file
# with open("Finder.kt", "r") as file:
#     finder_code = file.read()

# # Load FinderTest.kt from file
# with open("FinderTest.kt", "r") as file:
#     finder_test_code = file.read()

# print(finder_code)
# print(finder_test_code)

# example_diff = """
# // DIFF <START>
# --- before.kt
# +++ after.kt
# @@ -2,9 +2,9 @@
#  quick
#  brown
#  fox
# -
# -jumps
# +jumped
#  over
#  the
# +
#  lazy
# -dog
# +dogs
# // DIFF <END>
# """.strip()

# # Create the prompt
# prompt_template = ChatPromptTemplate.from_messages([
#     ("system", "テスト対象のクラス '''Finder.kt'' のKotlinクラスといくつかのユニットテストを含むテストクラス '''FinderTest.kt'' があります。"
#     + "各メソッドが、動作不良を引き起こす典型的なバグを含む、そのメソッドの新しいバージョンで置き換えられたテスト対象のクラスの新しいバージョンを書きます。"
#     # + "コメントペアの '// MUTANT <START>' と '// MUTANT <END>' を使って、変異した部分を区切ります。"),
#     + "コメントペアの '// DIFF <START>' と '// DIFF <END>' を使って、変異させたUnified形式のDIFFファイルを出力してください。"),
#     ("user", "<class_under_test>{class_under_test}</class_under_test>"),
#     ("user", "<existing_test_class>{finder_test_code}</existing_test_class>"),
#     ("user", "<example_diff>{example_diff}</example_diff>"),
#     ("user", "// DIFF <START>"),
# ])

# # Execute the LLM
# # output_parser = StrOutputParser()
# # chain = prompt_template | llm | output_parser
# # response = chain.invoke({"class_under_test": finder_code, "finder_test_code": finder_test_code, "example_diff": example_diff})

# # # Add the DIFF <START> comment to the response if it is not present
# # if not response.startswith("// DIFF <START>"):
# #     response = "// DIFF <START>\n" + response

# # # Extract the DIFF from the response
# # diff = response.split("// DIFF <START>")[1].split("// DIFF <END>")[0]
# # print(diff)


# # print("########################")
# # print(response.split("// DIFF <START>")[0])

# # print("########################")
# # print(response.split("// DIFF <END>")[1])

# diff = """
# --- Finder.kt	Wed Feb 21 22:37:22 2024
# +++ MUTATED_Finder.kt	Wed Feb 21 22:37:22 2024
# @@ -174,11 +174,11 @@
#       * @return 見つかったプロパティを [KtProperty] として返します。見つからない場合は null を返します。
#       */
#      fun findKtProperty(qualifiedPropertyName: String): KtProperty? {
# -        val targetFqName = FqName(qualifiedPropertyName)
# -        return findKtClass(targetFqName.parent().asString())?.let { ktClass ->
# +        val propertyName = qualifiedPropertyName.substringAfterLast(".")
# +        return findKtClass(qualifiedPropertyName.substringBeforeLast("."))?.let { ktClass ->
#              val properties = ktClass.getProperties()
# -            return properties.firstOrNull { it.fqName == targetFqName }
# +            return properties.firstOrNull { it.name == propertyName }
#          }
#      }
# """.strip()

# # print(diff)

# diff = diff.split("\n")

# # 1. diffを1行ずつ読み込む
# # 2. 行が@@で始まる場合、その行をスキップする
# # 3. 行が---で始まる場合、その行をスキップする
# # 4. 行が+++で始まる場合、その行をスキップする
# # 5. 行が+ or - で始まらない場合、ソースのコードの同じ行まで移動する
# # 6. 行が+ or - で始まる場合、ソースのコードの該当行を変更する
# # 7. diffの最後まで繰り返す

# with open("Finder.kt", "r") as file:
#     with open("Finder_mutated.kt", "w") as mutated_file:
#         for line in diff:
#             if line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
#                 continue

#             mark = line[0]
#             line = line[1:].rstrip()

#             if mark == "+":
#                 mutated_file.write(line)
#                 print(f"ADDED: {line}")
#             elif mark == "-":
#                 original_line = next(file)
#                 print(f"REMOVED: {original_line}")
#             else:
#                 line = line.rstrip()
#                 while True:
#                     original_line = next(file)
#                     if original_line.startswith(line):
#                         mutated_file.write(original_line)
#                         break
#                     else:
#                         mutated_file.write(original_line)

#         for line in file:
#             mutated_file.write(line)
        

