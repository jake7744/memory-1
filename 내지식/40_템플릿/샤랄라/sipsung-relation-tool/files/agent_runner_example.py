from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama

from saju_sipsung_langchain_tool import analyze_sipsung_relationship


llm = ChatOllama(model="exaone3.5:7.8b", temperature=0.1)
tools = [analyze_sipsung_relationship]
llm_with_tools = llm.bind_tools(tools)

system_prompt = SystemMessage(
    content=(
        "당신은 사주 명리 해설 에이전트입니다.\n"
        "십성, 십신, 육친, 오행 관계를 묻는 경우 직접 추정하지 말고 "
        "반드시 analyze_sipsung_relationship 도구의 JSON 결과를 근거로 답하십시오.\n"
        "지지 대상은 surface와 hidden_stems를 구분해서 설명하십시오.\n"
        "학파 차이가 가능한 지점은 현재 polarity_mode 기준이라고 밝히십시오."
    )
)

user_query = HumanMessage(content="내 일간이 丙이고 월지가 寅이면 어떤 십성으로 열려?")
first_response = llm_with_tools.invoke([system_prompt, user_query])

messages = [system_prompt, user_query, first_response]
for tool_call in first_response.tool_calls:
    tool_output = analyze_sipsung_relationship.invoke(tool_call["args"])
    messages.append(
        ToolMessage(
            content=str(tool_output),
            tool_call_id=tool_call["id"],
        )
    )

final_response = llm_with_tools.invoke(messages)
print(final_response.content)

