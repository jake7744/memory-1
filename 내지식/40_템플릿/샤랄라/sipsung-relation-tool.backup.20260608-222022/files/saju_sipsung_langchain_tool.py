from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from saju_sipsung_rules import SipsungCalculator, analyze_sipsung

try:
    from langchain_core.tools import tool
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "langchain_core is required only for the LangChain wrapper. "
        "Use saju_sipsung_rules.py or saju_sipsung_cli.py for dependency-free execution."
    ) from exc


class SipsungAnalysisInput(BaseModel):
    day_stem: str = Field(..., description="기준 일간 천간 한 글자: 甲乙丙丁戊己庚辛壬癸")
    target_character: str = Field(..., description="비교 대상 천간 또는 지지 한 글자")
    polarity_mode: Literal["standard", "cheyong"] = Field(
        "cheyong",
        description="지지 음양 기준. standard는 일반 지지 음양, cheyong은 원문 체용 변환 기준.",
    )
    branch_mode: Literal["surface", "hidden_main", "hidden_all"] = Field(
        "hidden_all",
        description="지지 처리 방식. surface는 표면 오행, hidden_main은 본기, hidden_all은 전체 지장간.",
    )

    @field_validator("day_stem")
    @classmethod
    def validate_day_stem(cls, value: str) -> str:
        return SipsungCalculator.validate_day_stem(value)

    @field_validator("target_character")
    @classmethod
    def validate_target_character(cls, value: str) -> str:
        return SipsungCalculator.validate_target(value)


@tool("analyze_sipsung_relationship", args_schema=SipsungAnalysisInput)
def analyze_sipsung_relationship(
    day_stem: str,
    target_character: str,
    polarity_mode: Literal["standard", "cheyong"] = "cheyong",
    branch_mode: Literal["surface", "hidden_main", "hidden_all"] = "hidden_all",
) -> dict:
    """
    일간과 대상 천간/지지의 오행, 음양, 생극 방향, 십성 및 지장간 십성을 계산합니다.
    LLM은 십성을 추정하지 말고 이 도구의 structured output을 근거로 해설해야 합니다.
    """
    try:
        return {
            "status": "success",
            "data": analyze_sipsung(day_stem, target_character, polarity_mode, branch_mode),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

