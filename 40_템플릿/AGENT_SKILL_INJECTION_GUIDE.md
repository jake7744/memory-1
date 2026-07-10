

# 🧠 에이전트 지식·스킬 주입 시스템 가이드

## Connect-AI Brain Skill Injection System Guide

본 문서는 Connect-AI Brain 내에서 각 에이전트, 예를 들어 Developer, YouTube, Writer, Researcher 등에게 새로운 능력, 템플릿, 작업 패턴, 코드 구조, 콘텐츠 포맷을 장착시키는 방법과 그 원리를 정리한 가이드입니다.

이 시스템의 목적은 에이전트가 매번 백지상태에서 작업하지 않도록 하고, 검증된 구조와 반복 가능한 패턴을 기반으로 더 빠르고 일관된 결과물을 만들게 하는 것입니다.

---

# 1. 개요

AI 에이전트가 특정 작업을 수행할 때마다 처음부터 구조를 판단하고, 코드를 작성하고, 문서 형식을 기획하게 두면 다음과 같은 문제가 생깁니다.

* 결과물의 품질이 매번 달라짐
* 이전에 검증한 구조를 재사용하지 못함
* 에이전트마다 작업 방식이 달라짐
* 반복 작업에 불필요한 시간이 소모됨
* 사용자의 의도와 다른 형식의 결과물이 나올 가능성이 커짐

이를 해결하기 위해 Connect-AI Brain에서는 **스킬 주입 시스템**을 사용합니다.

스킬 주입이란 특정 작업 패턴, 예를 들어 SaaS 랜딩 페이지 구조, 유튜브 대본 포맷, SEO 블로그 템플릿, 코드 리팩토링 규칙, 투자 분석 프레임워크 등을 하나의 패키지로 만들어 에이전트의 지식 베이스에 저장해두고, 필요할 때 에이전트가 스스로 찾아서 적용하게 만드는 방식입니다.

즉, 에이전트는 사용자의 요청을 받은 뒤 다음 과정을 거칩니다.

```text
사용자 요청 분석
→ 의도 분류
→ 적합한 스킬 탐색
→ manifest.json 확인
→ README.md 지침 로드
→ files 템플릿 참조
→ 사용자 요구사항에 맞게 커스터마이징
→ 검증 체크리스트 실행
→ 최종 결과물 생성
```

이 시스템은 단순한 프롬프트 저장소가 아니라, **에이전트용 작업 능력 라이브러리**입니다.

---

# 2. 스킬 주입 시스템의 핵심 개념

스킬 주입 시스템은 크게 네 가지 요소로 구성됩니다.

```text
1. 스킬 저장 경로
2. manifest.json
3. README.md
4. files 폴더
```

각 요소의 역할은 다음과 같습니다.

| 구성 요소         | 역할                            |
| ------------- | ----------------------------- |
| 스킬 저장 경로      | 어떤 에이전트에게 어떤 스킬을 장착할지 구분      |
| manifest.json | 스킬의 이름, 발동 조건, 우선순위, 충돌 조건 정의 |
| README.md     | 에이전트가 실제 작업 시 따라야 할 상세 지침     |
| files 폴더      | 복사하거나 참조할 수 있는 실제 템플릿 파일 저장   |

---

# 3. 기본 폴더 구조

스킬은 다음 경로에 배치합니다.

```text
내지식\40_템플릿\[에이전트명]\[스킬명]\
```

예시는 다음과 같습니다.

```text
내지식\40_템플릿\developer\landing-kit\
내지식\40_템플릿\developer\react-dashboard-kit\
내지식\40_템플릿\youtube\tarot-script-kit\
내지식\40_템플릿\youtube\shorts-script-kit\
내지식\40_템플릿\writer\seo-blog-template\
내지식\40_템플릿\writer\sales-copy-template\
```

각 폴더는 하나의 독립된 스킬 패키지를 의미합니다.

---

# 4. 스킬 패키지 표준 구조

하나의 스킬 폴더는 다음 구조를 따릅니다.

```text
내지식\40_템플릿\[에이전트명]\[스킬명]\
│
├─ manifest.json
├─ README.md
└─ files\
   ├─ template.md
   ├─ example.md
   ├─ component.tsx
   └─ config.json
```

예를 들어 SEO 블로그 템플릿 스킬은 다음처럼 구성할 수 있습니다.

```text
내지식\40_템플릿\writer\seo-blog-template\
│
├─ manifest.json
├─ README.md
└─ files\
   ├─ blog_base.md
   ├─ title_patterns.md
   ├─ faq_patterns.md
   └─ meta_description_examples.md
```

개발용 랜딩 페이지 스킬은 다음처럼 구성할 수 있습니다.

```text
내지식\40_템플릿\developer\landing-kit\
│
├─ manifest.json
├─ README.md
└─ files\
   ├─ Hero.tsx
   ├─ Features.tsx
   ├─ Pricing.tsx
   ├─ CTA.tsx
   └─ landing-copy-guide.md
```

---

# 5. manifest.json 역할

`manifest.json`은 에이전트가 **언제 이 스킬을 사용해야 하는지 판단하는 명세서**입니다.

기존 방식에서는 `keywords`만으로 스킬을 발동했지만, 실제 운영에서는 이것만으로 부족합니다.

예를 들어 사용자가 이렇게 말할 수 있습니다.

```text
블로그처럼 읽히는 유튜브 대본 써줘.
```

이 문장에는 “블로그”라는 키워드가 들어 있지만, 실제 목적은 블로그 글 작성이 아니라 유튜브 대본 작성입니다.

따라서 스킬 발동은 단순 키워드가 아니라 다음 요소를 함께 보고 판단해야 합니다.

```text
keywords
intent
avoid_keywords
priority
required_inputs
conflicts_with
can_combine_with
```

---

# 6. manifest.json 표준 예시

아래는 확장된 manifest 구조입니다.

```json
{
  "name": "SEO Blog Template",
  "version": "1.0.0",
  "agent": "writer",
  "description": "검색 노출을 고려한 정보성 블로그 포스팅 작성 스킬",
  "keywords": ["블로그", "SEO", "포스팅", "검색노출", "상위노출", "글쓰기"],
  "intent": ["blog_writing", "seo_content", "information_article"],
  "avoid_keywords": ["유튜브 대본", "쇼츠", "랜딩페이지", "광고 카피", "앱 UI"],
  "base": "markdown",
  "tested_with": ["ChatGPT", "Claude", "DeepSeek"],
  "required_inputs": ["topic", "target_reader", "main_keyword"],
  "optional_inputs": ["tone", "word_count", "cta", "reference_links"],
  "output_type": "markdown",
  "priority": 70,
  "components": [
    "seo_title",
    "meta_description",
    "intro",
    "h2_sections",
    "faq",
    "conclusion_cta"
  ],
  "entry_file": "files/blog_base.md",
  "readme": "README.md",
  "can_combine_with": ["seo-title-kit", "faq-generator-kit"],
  "conflicts_with": ["youtube-script-template", "landing-page-copy-kit"]
}
```

---

# 7. manifest.json 필드 설명

| 필드                 | 설명                       |
| ------------------ | ------------------------ |
| `name`             | 스킬의 공식 이름                |
| `version`          | 스킬 버전                    |
| `agent`            | 이 스킬을 사용할 대상 에이전트        |
| `description`      | 스킬의 목적과 간단한 설명           |
| `keywords`         | 스킬 발동 후보로 잡을 키워드         |
| `intent`           | 사용자의 실제 의도 유형            |
| `avoid_keywords`   | 이 키워드가 있으면 발동을 피해야 하는 조건 |
| `base`             | 기본 포맷 또는 기술 기반           |
| `tested_with`      | 검증된 모델 또는 환경             |
| `required_inputs`  | 작업에 반드시 필요한 입력값          |
| `optional_inputs`  | 있으면 품질이 좋아지는 선택 입력값      |
| `output_type`      | 결과물 형식                   |
| `priority`         | 여러 스킬이 동시에 후보가 될 때 우선순위  |
| `components`       | 스킬을 구성하는 주요 요소           |
| `entry_file`       | 기본으로 참조할 파일              |
| `readme`           | 작업 지침 파일                 |
| `can_combine_with` | 함께 사용할 수 있는 스킬           |
| `conflicts_with`   | 동시에 사용하면 안 되는 스킬         |

---

# 8. README.md 역할

`README.md`는 에이전트가 스킬을 발동한 뒤 실제로 어떻게 작업해야 하는지 알려주는 **작업 지침서**입니다.

이 파일은 자유롭게 작성할 수 있지만, 안정적인 운영을 위해 표준 섹션을 사용하는 것이 좋습니다.

---

# 9. README.md 표준 구조

```md
# Skill Name

## Purpose
이 스킬의 목적을 설명한다.

## When to Use
이 스킬을 사용해야 하는 상황을 정의한다.

## When Not to Use
이 스킬을 사용하면 안 되는 상황을 정의한다.

## Required Inputs
작업 전에 필요한 입력값을 정의한다.

## Optional Inputs
있으면 결과물 품질이 좋아지는 입력값을 정의한다.

## Output Structure
최종 결과물의 구조를 정의한다.

## Assembly Steps
files 폴더의 자료를 어떻게 조립할지 설명한다.

## Style Rules
문체, 디자인, 코드 스타일, 네이밍 규칙 등을 정의한다.

## Do
반드시 해야 할 일을 정의한다.

## Don't
절대 하지 말아야 할 일을 정의한다.

## Validation Checklist
작업 완료 후 점검해야 할 기준을 정의한다.
```

---

# 10. README.md 예시: SEO Blog Template

```md
# SEO Blog Template

## Purpose
검색 노출을 고려한 정보성 블로그 글을 작성한다.

## When to Use
- 사용자가 블로그 글, 포스팅, SEO 글, 정보성 콘텐츠 작성을 요청할 때
- 검색 키워드 중심의 글 구조가 필요한 경우
- 독자가 특정 문제를 검색해서 들어오는 콘텐츠를 작성할 때

## When Not to Use
- 유튜브 대본 작성 요청
- 쇼츠 대본 작성 요청
- 랜딩페이지 카피 작성 요청
- 짧은 광고 문구 작성 요청
- 감성 에세이 작성 요청

## Required Inputs
- 주제
- 핵심 키워드
- 대상 독자

## Optional Inputs
- 원하는 문체
- 글자 수
- CTA 목적
- 참고 링크
- 브랜드 톤

## Output Structure
1. SEO 제목
2. 메타 디스크립션
3. 도입부
4. H2 본문 섹션
5. FAQ
6. 마무리 CTA

## Assembly Steps
1. files/blog_base.md를 기본 구조로 사용한다.
2. files/title_patterns.md를 참고하여 제목 후보를 만든다.
3. files/faq_patterns.md를 참고하여 FAQ를 구성한다.
4. 사용자의 주제와 키워드에 맞게 본문을 재작성한다.
5. 최종 결과물을 Validation Checklist 기준으로 점검한다.

## Style Rules
- H1은 문서 내 1개만 사용한다.
- H2는 최소 3개 이상 사용한다.
- 도입부는 3문장 이내로 작성한다.
- 문장은 짧고 명확하게 작성한다.
- 핵심 키워드는 자연스럽게 포함한다.
- 같은 키워드를 과도하게 반복하지 않는다.

## Do
- 검색 의도를 먼저 파악한다.
- 독자가 궁금해할 질문을 본문에 포함한다.
- 제목과 도입부에 핵심 키워드를 자연스럽게 배치한다.
- 마지막에는 독자의 다음 행동을 유도한다.

## Don't
- 근거 없는 수치를 만들지 않는다.
- 어색하게 키워드를 반복하지 않는다.
- 광고성 문장으로 시작하지 않는다.
- 사용자가 요청하지 않은 과장 표현을 넣지 않는다.

## Validation Checklist
- 핵심 키워드가 제목과 도입부에 자연스럽게 포함되었는가?
- H2 구조가 검색 의도와 맞는가?
- 본문이 독자의 문제를 실제로 해결하는가?
- FAQ가 실제 검색 질문처럼 구성되었는가?
- 마무리 CTA가 자연스러운가?
```

---

# 11. files 폴더 역할

`files` 폴더는 에이전트가 실제 작업에 가져다 쓸 수 있는 원본 템플릿, 코드, 문서, 예시 파일을 저장하는 공간입니다.

에이전트는 이 파일들을 그대로 복사하거나, 필요한 부분만 참조한 뒤 사용자의 요청에 맞게 수정합니다.

중요한 점은 `files` 폴더 안의 파일은 반드시 **실제로 작동 가능한 상태**여야 한다는 것입니다.

개발 스킬이라면 코드가 실행 가능해야 하고, 문서 스킬이라면 구조가 완성되어 있어야 합니다.

---

# 12. files 폴더 구성 예시

SEO 블로그 스킬:

```text
files\
├─ blog_base.md
├─ title_patterns.md
├─ faq_patterns.md
└─ meta_description_examples.md
```

SaaS 랜딩 페이지 스킬:

```text
files\
├─ Hero.tsx
├─ Problem.tsx
├─ Features.tsx
├─ Pricing.tsx
├─ CTA.tsx
├─ layout.tsx
└─ copy-guide.md
```

유튜브 타로 대본 스킬:

```text
files\
├─ intro_template.md
├─ reading_flow.md
├─ card_interpretation_patterns.md
├─ closing_template.md
└─ title_thumbnail_patterns.md
```

자동매매 분석 스킬:

```text
files\
├─ market_checklist.md
├─ risk_management_template.md
├─ entry_exit_rules.md
├─ scenario_report.md
└─ validation_log_template.md
```

---

# 13. 스킬 발동 흐름

에이전트는 사용자 요청을 받으면 다음 순서로 스킬을 탐색합니다.

```text
1. 사용자 요청 수신
2. 현재 담당 에이전트 확인
3. 해당 에이전트 폴더 탐색
4. 각 스킬의 manifest.json 로드
5. keywords 기반 후보 스킬 추출
6. intent 기반으로 실제 목적 판단
7. avoid_keywords 조건 확인
8. priority 기준으로 우선순위 계산
9. conflicts_with 여부 확인
10. can_combine_with 여부 확인
11. 최종 스킬 선택
12. README.md 로드
13. files 폴더의 템플릿 참조
14. 사용자 요구사항에 맞게 커스터마이징
15. Validation Checklist로 결과 검증
16. 최종 결과물 출력
```

---

# 14. 스킬 선택 기준

스킬 선택은 단순히 키워드가 포함되었는지만 보지 않습니다.

다음 네 가지를 함께 판단합니다.

```text
키워드 일치도
+ 의도 일치도
+ 회피 조건
+ 우선순위
```

예를 들어 사용자가 이렇게 요청했다고 가정합니다.

```text
타로 유튜브 영상용으로 검색 잘 되는 제목이랑 설명글까지 써줘.
```

이 요청에는 다음 키워드가 포함됩니다.

```text
타로
유튜브
검색
제목
설명글
```

이 경우 후보 스킬은 여러 개가 될 수 있습니다.

```text
youtube\tarot-script-kit
youtube\title-thumbnail-kit
writer\seo-blog-template
```

하지만 실제 의도는 블로그 작성이 아니라 유튜브 콘텐츠 작성입니다.

따라서 최종적으로는 다음처럼 선택되어야 합니다.

```text
메인 스킬: youtube\tarot-script-kit
보조 스킬: youtube\title-thumbnail-kit
제외 스킬: writer\seo-blog-template
```

---

# 15. 스킬 충돌 처리

여러 스킬이 동시에 발동될 수 있는 경우에는 충돌 처리가 필요합니다.

이를 위해 manifest에 다음 필드를 둡니다.

```json
{
  "can_combine_with": ["seo-title-kit", "thumbnail-copy-kit"],
  "conflicts_with": ["longform-blog-template"]
}
```

예를 들어 `youtube\tarot-script-kit`은 `thumbnail-copy-kit`과 조합할 수 있습니다.

하지만 `seo-blog-template`과는 충돌할 수 있습니다.

```text
가능한 조합:
youtube\tarot-script-kit
+ youtube\thumbnail-copy-kit

충돌하는 조합:
youtube\tarot-script-kit
+ writer\seo-blog-template
```

이렇게 정의하면 에이전트가 잘못된 템플릿을 섞는 일을 줄일 수 있습니다.

---

# 16. 스킬 우선순위

`priority`는 여러 스킬이 동시에 후보가 되었을 때 어떤 스킬을 먼저 적용할지 결정합니다.

예시:

```json
{
  "name": "Tarot YouTube Script Kit",
  "priority": 90
}
```

```json
{
  "name": "SEO Blog Template",
  "priority": 70
}
```

위 경우 사용자의 요청에 둘 다 걸리더라도, 유튜브 대본 의도가 강하면 `Tarot YouTube Script Kit`이 우선됩니다.

권장 우선순위 기준은 다음과 같습니다.

| 우선순위   | 의미                 |
| ------ | ------------------ |
| 90~100 | 특정 에이전트의 핵심 작업 스킬  |
| 70~89  | 자주 사용하는 주요 스킬      |
| 50~69  | 보조 스킬              |
| 30~49  | 제한적으로 사용하는 스킬      |
| 0~29   | 실험용 또는 비활성에 가까운 스킬 |

---

# 17. 입력값 부족 처리

스킬에 필요한 입력값이 부족할 경우, 에이전트는 무조건 작업을 중단하지 않습니다.

먼저 `required_inputs`를 확인합니다.

예를 들어 SEO 블로그 스킬에 다음 입력값이 필요하다고 가정합니다.

```json
{
  "required_inputs": ["topic", "target_reader", "main_keyword"]
}
```

사용자가 이렇게 요청한 경우:

```text
SEO 블로그 글 하나 써줘.
```

필수 입력값이 부족합니다.

이때 에이전트는 다음 두 가지 방식 중 하나를 선택합니다.

## 1) 반드시 필요한 정보가 없으면 질문하기

```text
주제와 핵심 키워드가 필요해요. 어떤 주제로 작성할까요?
```

## 2) 합리적으로 추정 가능한 경우 기본값 적용하기

```text
주제가 명확하지 않아 일반적인 SEO 블로그 구조 예시로 작성합니다.
```

운영 기준은 다음과 같습니다.

| 상황          | 처리 방식         |
| ----------- | ------------- |
| 주제 자체가 없음   | 질문            |
| 문체만 없음      | 기본값 적용        |
| 분량만 없음      | 기본값 적용        |
| 대상 독자가 불명확함 | 일반 독자로 가정     |
| 기술 스택이 불명확함 | README 기본값 적용 |

---

# 18. Validation Checklist

모든 스킬은 작업 완료 후 검증 체크리스트를 가져야 합니다.

검증 체크리스트는 에이전트가 결과물을 출력하기 전에 마지막으로 점검해야 하는 기준입니다.

예를 들어 Developer 스킬이라면 다음과 같은 체크리스트가 필요합니다.

```md
## Validation Checklist

- 코드가 실행 가능한 구조인가?
- 사용하지 않는 import가 없는가?
- 컴포넌트 이름이 명확한가?
- 반응형 레이아웃이 적용되었는가?
- 사용자의 요구사항이 모두 반영되었는가?
- 불필요한 더미 텍스트가 남아 있지 않은가?
```

Writer 스킬이라면 다음 기준이 필요합니다.

```md
## Validation Checklist

- 요청한 주제에서 벗어나지 않았는가?
- 문체가 일관적인가?
- 도입부가 너무 길지 않은가?
- 핵심 메시지가 분명한가?
- 사용자가 요청하지 않은 내용을 임의로 추가하지 않았는가?
```

YouTube 스킬이라면 다음 기준이 필요합니다.

```md
## Validation Checklist

- 초반 10초 안에 몰입 포인트가 있는가?
- 제목과 본문 흐름이 일치하는가?
- 시청자 공감 포인트가 충분한가?
- 중간 이탈을 줄이는 전환 문장이 있는가?
- 마무리 CTA가 자연스러운가?
```

---

# 19. 스킬 버전 관리

스킬은 시간이 지나면서 개선될 수 있으므로 `version` 필드를 반드시 사용합니다.

예시:

```json
{
  "name": "SEO Blog Template",
  "version": "1.2.0"
}
```

권장 버전 규칙은 다음과 같습니다.

```text
1.0.0 = 최초 안정 버전
1.1.0 = 기능 또는 구조 추가
1.1.1 = 작은 문구 수정 또는 버그 수정
2.0.0 = 기존 구조와 호환되지 않는 큰 변경
```

스킬 폴더 안에 변경 이력을 남기고 싶다면 `CHANGELOG.md`를 추가할 수 있습니다.

```text
내지식\40_템플릿\writer\seo-blog-template\
│
├─ manifest.json
├─ README.md
├─ CHANGELOG.md
└─ files\
```

---

# 20. 권장 CHANGELOG.md 구조

```md
# CHANGELOG

## 1.1.0
- FAQ 생성 규칙 추가
- 메타 디스크립션 예시 추가
- 검색 의도 분류 기준 추가

## 1.0.0
- 최초 SEO 블로그 템플릿 생성
- 제목, 도입부, 본문, FAQ, CTA 구조 정의
```

---

# 21. 스킬 조합 시스템

하나의 사용자 요청이 여러 작업을 포함할 경우, 하나의 스킬만으로는 부족할 수 있습니다.

예를 들어:

```text
타로 유튜브 영상 대본 만들고, 제목이랑 썸네일 문구도 같이 만들어줘.
```

이 경우 다음 스킬을 조합할 수 있습니다.

```text
메인 스킬:
youtube\tarot-script-kit

보조 스킬:
youtube\title-thumbnail-kit
youtube\cta-kit
```

조합 가능한 스킬은 manifest에서 정의합니다.

```json
{
  "can_combine_with": [
    "title-thumbnail-kit",
    "cta-kit",
    "seo-title-kit"
  ]
}
```

스킬 조합 시에는 반드시 메인 스킬을 먼저 결정하고, 보조 스킬은 결과물을 강화하는 용도로만 사용합니다.

---

# 22. 에이전트별 스킬 예시

## Developer 에이전트

```text
developer\landing-kit
developer\react-dashboard-kit
developer\api-client-kit
developer\refactor-kit
developer\test-runner-kit
```

주요 목적:

```text
코드 생성
UI 구성
API 연결
리팩토링
테스트 코드 작성
```

## YouTube 에이전트

```text
youtube\tarot-script-kit
youtube\shorts-script-kit
youtube\title-thumbnail-kit
youtube\storytelling-kit
youtube\retention-hook-kit
```

주요 목적:

```text
영상 대본 작성
쇼츠 구성
제목/썸네일 문구 생성
시청 지속률 개선
```

## Writer 에이전트

```text
writer\seo-blog-template
writer\sales-copy-template
writer\email-template
writer\essay-template
writer\report-template
```

주요 목적:

```text
블로그 글 작성
세일즈 카피 작성
이메일 작성
에세이 작성
리포트 작성
```

## Researcher 에이전트

```text
researcher\paper-summary-kit
researcher\market-analysis-kit
researcher\comparison-report-kit
researcher\fact-check-kit
```

주요 목적:

```text
자료 조사
논문 요약
시장 분석
팩트 체크
비교 리포트 작성
```

---

# 23. 실전 예시: SEO 블로그 스킬 주입

## Step 1. 폴더 생성

```text
내지식\40_템플릿\writer\seo-blog-template\
```

## Step 2. manifest.json 작성

```json
{
  "name": "SEO Blog Template",
  "version": "1.0.0",
  "agent": "writer",
  "description": "검색 노출에 최적화된 정보성 블로그 포스팅 구조",
  "keywords": ["블로그", "SEO", "포스팅", "검색노출", "상위노출"],
  "intent": ["blog_writing", "seo_content"],
  "avoid_keywords": ["유튜브", "쇼츠", "랜딩페이지"],
  "base": "markdown",
  "required_inputs": ["topic", "main_keyword"],
  "optional_inputs": ["target_reader", "tone", "word_count"],
  "output_type": "markdown",
  "priority": 70,
  "components": [
    "title",
    "meta_description",
    "intro",
    "body_sections",
    "faq",
    "conclusion"
  ],
  "entry_file": "files/blog_base.md",
  "readme": "README.md",
  "can_combine_with": ["faq-generator-kit", "seo-title-kit"],
  "conflicts_with": ["youtube-script-template"]
}
```

## Step 3. files 폴더 구성

```text
files\
├─ blog_base.md
├─ title_patterns.md
├─ faq_patterns.md
└─ meta_description_examples.md
```

## Step 4. README.md 작성

```md
# SEO Blog Template

## Purpose
검색 노출을 고려한 정보성 블로그 글을 작성한다.

## When to Use
- 사용자가 블로그 글 작성을 요청할 때
- SEO 최적화가 필요한 글을 요청할 때
- 정보성 포스팅 구조가 필요한 경우

## When Not to Use
- 유튜브 대본 작성
- 쇼츠 대본 작성
- 랜딩페이지 카피 작성

## Required Inputs
- 주제
- 핵심 키워드

## Optional Inputs
- 대상 독자
- 원하는 문체
- 글자 수

## Output Structure
1. 제목
2. 메타 디스크립션
3. 도입부
4. 본문 섹션
5. FAQ
6. 마무리

## Style Rules
- H1은 1개만 사용한다.
- H2는 최소 3개 이상 사용한다.
- 도입부는 짧게 작성한다.
- 키워드는 자연스럽게 포함한다.

## Don't
- 근거 없는 수치를 만들지 않는다.
- 키워드를 과도하게 반복하지 않는다.
- 사용자가 요청하지 않은 광고 문구를 넣지 않는다.

## Validation Checklist
- 검색 의도에 맞는 구조인가?
- 제목에 핵심 키워드가 들어갔는가?
- 본문이 독자의 문제를 해결하는가?
- FAQ가 실제 질문처럼 구성되었는가?
```

## Step 5. 테스트

사용자가 다음처럼 요청합니다.

```text
SEO 최적화된 블로그 글 하나 써줘. 주제는 초보자를 위한 노션 사용법이야.
```

에이전트는 다음처럼 판단합니다.

```text
agent: writer
matched skill: seo-blog-template
intent: blog_writing
required_inputs:
- topic: 초보자를 위한 노션 사용법
- main_keyword: 노션 사용법으로 추정 가능
```

그 뒤 README와 files를 참조해 글을 작성합니다.

---

# 24. 실전 예시: 유튜브 타로 대본 스킬 주입

## 폴더 구조

```text
내지식\40_템플릿\youtube\tarot-script-kit\
│
├─ manifest.json
├─ README.md
└─ files\
   ├─ intro_template.md
   ├─ reading_flow.md
   ├─ card_interpretation_patterns.md
   ├─ transition_phrases.md
   └─ closing_template.md
```

## manifest.json

```json
{
  "name": "Tarot YouTube Script Kit",
  "version": "1.0.0",
  "agent": "youtube",
  "description": "타로 리딩 유튜브 콘텐츠 대본을 구성하는 스킬",
  "keywords": ["타로", "유튜브", "리딩", "카드", "대본", "선택지"],
  "intent": ["youtube_script", "tarot_reading_content"],
  "avoid_keywords": ["블로그", "논문", "랜딩페이지", "코드"],
  "base": "markdown",
  "required_inputs": ["theme", "card_spread"],
  "optional_inputs": ["tone", "target_viewer", "video_length", "cta"],
  "output_type": "script",
  "priority": 90,
  "components": [
    "opening_hook",
    "viewer_empathy",
    "card_reading",
    "transition",
    "solution",
    "closing_cta"
  ],
  "entry_file": "files/reading_flow.md",
  "readme": "README.md",
  "can_combine_with": ["title-thumbnail-kit", "retention-hook-kit"],
  "conflicts_with": ["seo-blog-template", "sales-copy-template"]
}
```

## README.md 핵심 내용

```md
# Tarot YouTube Script Kit

## Purpose
타로를 단순 점술이 아니라 무의식을 드러내는 도구로 활용하는 유튜브 대본을 작성한다.

## When to Use
- 사용자가 타로 유튜브 대본을 요청할 때
- 카드 선택형 콘텐츠를 구성할 때
- 시청자의 현재 상태, 반복 패턴, 전환 방향을 리딩하는 콘텐츠를 만들 때

## When Not to Use
- 일반 블로그 글 작성
- 짧은 광고 카피 작성
- 기술 문서 작성

## Required Inputs
- 콘텐츠 주제
- 카드 배열 또는 리딩 구조

## Optional Inputs
- 선택지 개수
- 영상 길이
- 말투
- 타깃 시청자
- 마무리 CTA

## Output Structure
1. 오프닝 훅
2. 시청자 공감 문장
3. 선택지 안내
4. 카드별 리딩
5. 반복 구조 분석
6. 전환 메시지
7. 마무리 안내

## Style Rules
- 시청자의 상황을 구체적으로 짚는다.
- 추측형 표현을 줄이고 단정적이되 부드럽게 말한다.
- 카드가 미래를 결정한다고 표현하지 않는다.
- 타로는 무의식을 보여주는 도구라는 관점을 유지한다.
- 전문 용어는 쉽게 풀어 쓴다.

## Don't
- 불안감을 자극하지 않는다.
- 과도하게 운명론적으로 말하지 않는다.
- 시청자에게 죄책감을 주지 않는다.
- 카드 의미만 나열하지 않는다.

## Validation Checklist
- 초반 10초 안에 몰입 포인트가 있는가?
- 시청자가 자신의 상황과 연결할 수 있는가?
- 카드 해석이 단순 의미 나열에 그치지 않는가?
- 반복 패턴과 전환 방향이 명확한가?
- 마무리가 따뜻하고 자연스러운가?
```

---

# 25. 스킬 운영 모범 사례

## 1) 키워드는 넓게, 의도는 정확하게

`keywords`는 후보를 찾기 위한 장치입니다.
최종 선택은 반드시 `intent` 기준으로 해야 합니다.

좋은 예:

```json
"keywords": ["타로", "리딩", "유튜브", "대본"],
"intent": ["youtube_script", "tarot_reading_content"]
```

부족한 예:

```json
"keywords": ["타로"]
```

---

## 2) When Not to Use를 반드시 작성하기

스킬 오작동은 대부분 “언제 쓰지 말아야 하는지”가 없어서 발생합니다.

따라서 README에는 반드시 다음 항목을 넣어야 합니다.

```md
## When Not to Use
```

그리고 manifest에는 다음 항목을 넣어야 합니다.

```json
"avoid_keywords": []
```

---

## 3) files 폴더에는 완성도 높은 원본만 넣기

에이전트는 `files` 폴더를 신뢰하고 사용합니다.

따라서 이 안에는 미완성 코드, 오류 있는 코드, 임시 문서, 테스트용 조각을 넣으면 안 됩니다.

잘못된 예:

```text
test_old.tsx
임시복사본.md
대충쓴버전.md
```

좋은 예:

```text
Hero.tsx
Pricing.tsx
blog_base.md
reading_flow.md
validation_checklist.md
```

---

## 4) 스킬은 작게 만들고 조합 가능하게 만들기

하나의 스킬에 너무 많은 기능을 넣으면 재사용성이 떨어집니다.

나쁜 예:

```text
youtube-all-in-one-kit
```

좋은 예:

```text
youtube\tarot-script-kit
youtube\title-thumbnail-kit
youtube\retention-hook-kit
youtube\shorts-convert-kit
```

작게 나눈 뒤 `can_combine_with`로 연결하는 것이 좋습니다.

---

## 5) 검증 체크리스트를 반드시 포함하기

스킬의 품질은 결과물을 만든 뒤 결정되는 것이 아니라, **검증 기준이 있느냐 없느냐**에서 결정됩니다.

모든 README에는 다음 항목을 넣습니다.

```md
## Validation Checklist
```

---

# 26. 최종 권장 구조

Connect-AI Brain의 스킬 주입 시스템은 최종적으로 다음 구조를 따르는 것이 좋습니다.

```text
내지식\40_템플릿\
│
├─ developer\
│  ├─ landing-kit\
│  │  ├─ manifest.json
│  │  ├─ README.md
│  │  ├─ CHANGELOG.md
│  │  └─ files\
│  │
│  └─ react-dashboard-kit\
│
├─ youtube\
│  ├─ tarot-script-kit\
│  │  ├─ manifest.json
│  │  ├─ README.md
│  │  ├─ CHANGELOG.md
│  │  └─ files\
│  │
│  └─ title-thumbnail-kit\
│
└─ writer\
   ├─ seo-blog-template\
   │  ├─ manifest.json
   │  ├─ README.md
   │  ├─ CHANGELOG.md
   │  └─ files\
   │
   └─ sales-copy-template\
```

---

