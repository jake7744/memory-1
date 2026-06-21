# Sipsung Relationship Tool

이 스킬은 원문 아이디어인 "LLM은 해석만 하고, 십성/오행 계산은 규칙 엔진이 맡는다"는 구조를 실제 Connect AI 에이전트에서 재사용할 수 있게 보강한 패키지입니다.

## 언제 사용하나

사용자가 다음을 물으면 이 스킬을 우선 사용합니다.

- 일간 기준 특정 천간의 십성
- 일간 기준 특정 지지의 표면 오행/십성
- 일운, 세운, 대운의 천간/지지가 어떤 십신으로 작동하는지
- 지장간이 어떤 십신으로 열리는지
- 음양오행 생극 방향이 어떻게 되는지

## 중요한 해석 원칙

계산 결과를 과장해서 "절대 오차 0%"라고 표현하지 않습니다. 이 도구는 선택한 규칙 체계 안에서 일관된 계산값을 제공합니다.

## 필수 답변 지침

에이전트는 사주 원국, 대운, 세운, 월운, 일운, 시운을 해석할 때 다음 지침을 반드시 지킵니다.

1. 계산은 `saju_matrix_analyzer` 결과만 근거로 합니다.
2. `matrix.interactions`에 있는 형충파해합은 빠뜨리지 않습니다.
3. `twelve_stages`와 `twelve_spirits`를 오늘 프로필에 포함합니다.
4. 답변 구조는 사용자의 질문 유형에 맞춥니다.
5. 사용자가 오늘, 지금, 현재 시간, 방금, 아까를 말하면 날짜/시간을 추정하지 말고 `saju_datetime_tool` 또는 `saju_feedback_cli.py now` 결과를 기준으로 처리합니다.

지지는 두 층으로 봅니다.

1. `surface`: 지지의 표면 오행과 음양으로 보는 빠른 판정
2. `hidden_all`: 지장간 전체를 일간 기준 십성으로 펼친 판정

실제 통변에서는 `surface`만 단정하지 말고 `hidden_stems` 결과를 함께 확인합니다. 기존 사주 프레임워크의 원칙처럼 지지는 현실 마당이며, 지장간이 어떤 십신으로 열리는지가 중요합니다.

## 음양 모드

- `standard`: 일반적인 지지 음양 순서입니다. 子 양, 丑 음, 寅 양, 卯 음, 辰 양, 巳 음, 午 양, 未 음, 申 양, 酉 음, 戌 양, 亥 음.
- `cheyong`: 원문에서 제안한 체용 변화를 반영합니다. 巳/亥는 양, 子/午는 음으로 계산합니다.

기본값은 원문 호환성을 위해 `cheyong`입니다. 표준표 기준 검산이 필요하면 `standard`로 바꿉니다.

## CLI 사용법

```powershell
python ".\files\saju_sipsung_cli.py" --day-stem 丙 --target 寅 --polarity-mode cheyong --branch-mode hidden_all
```

결과는 JSON으로 출력됩니다. 에이전트는 이 JSON의 `surface`, `hidden_stems`, `primary_sipsung`, `relationship_direction`을 근거로 해설합니다.

## 원국/대운/세운/월운 고정 후 일운/시운 계산

대표님 운용 방식은 다음을 기본으로 합니다.

1. 원국, 대운, 세운, 월운은 `files/saju_luck_config.example.json` 형식으로 미리 세팅합니다.
2. 사용자가 현재 날짜만 알려주면 `saju_daily_luck.py`가 일운과 12시진 시운을 계산합니다.
3. 결과 JSON에는 고정 레이어와 계산 레이어가 함께 들어갑니다.

예시:

```powershell
python ".\files\saju_daily_luck_cli.py" --config ".\files\saju_luck_config.example.json" --date 2026-06-07
```

이 도구는 첨부 자료 기준에 맞춰 `2026-06-07 = 壬子일`을 기준점으로 삼습니다. 다음 날인 `2026-06-08`은 자동으로 `癸丑일`이 됩니다.

시운은 자료 예시처럼 `23:30~01:30` 자시 기준으로 계산합니다. 그래서 `壬子일`에는 `05:30~07:30 = 癸卯시`, `07:30~09:30 = 甲辰시`, `15:30~17:30 = 戊申시`가 나옵니다.

에이전트는 다음 규칙을 지킵니다.

- 원국/대운/세운/월운은 config 값을 그대로 사용합니다.
- 사용자가 날짜만 주면 일운과 시운만 계산합니다.
- 사용자가 “세운/월운이 바뀌었다”고 말할 때만 config의 고정 운을 갱신합니다.
- 시간대별 답변은 `calculated.hour_pillars` 배열을 기준으로 작성합니다.

## 십이운성 계산

`files/saju_twelve_stages.py`는 일간과 대상 지지를 받아 십이운성을 계산합니다.

예시:

```powershell
python ".\files\saju_twelve_stages_cli.py" --day-stem 辛 --target-branch 子
```

자료 예시처럼 辛 일간에게 子는 `장생`으로 반환됩니다. 壬 일간에게 子는 `제왕`으로 반환되므로, "일간 기준 십이운성"과 "일진 壬子 자체의 왕쇠"를 구분해서 설명합니다.

## 종합 매트릭스 분석

`files/saju_matrix_analyzer.py`는 현재 스킬의 통합 입구입니다.

```powershell
python ".\files\saju_matrix_analyzer_cli.py" --config ".\files\saju_luck_config.example.json" --date 2026-06-07
```

특정 시운까지 지정하려면:

```powershell
python ".\files\saju_matrix_analyzer_cli.py" --config ".\files\saju_luck_config.example.json" --date 2026-06-07 --hour-pillar 庚申
```

이 통합 결과에는 다음이 들어갑니다.

- 일운/시운 계산
- 십성/지장간
- 십이운성
- 십이신살
- 천간합/천간충
- 지지 육합/반합/삼합/방합/충/형/파/해/원진/귀문
- 충/형 등 지지 2글자 관계의 벡터 각도, 합성 방향, 행동 전략
- 중복 지지 전체를 합산한 `matrix.vector_summary`

에이전트는 형충파해합을 사용자가 따로 “누락 확인”하라고 말할 때까지 기다리지 않습니다. `matrix.interactions`를 먼저 보고, 감지된 관계를 모두 반영한 뒤 중요도에 따라 해설합니다.

## 명리 벡터 모델

`files/saju_vector_model.py`는 `충 형 백터 계산법 (1).md`의 계산 가능한 부분을 코드화한 모듈입니다.

```powershell
python ".\files\saju_vector_model_cli.py" --branch-a 丑 --branch-b 戌
```

핵심 기준:

- 卯=0°, 寅=30°, 丑=60°, 子=90°, 亥=120°, 戌=150°, 酉=180°, 申=210°, 未=240°, 午=270°, 巳=300°, 辰=330°
- 180°는 충으로 보고, 기존 방향성 상쇄와 리셋 구조로 해석합니다.
- 90°는 형적 직교 압력으로 보고, 합성 방향을 계산해 행동 전략으로 전환합니다.
- 예: 丑戌은 60°와 150°의 90° 관계이므로 평균 방향 105°가 나오며, 子水와 亥水 사이의 水 방향 행동인 기록, 언어화, 데이터화, 코딩, 흐름 분석으로 전환합니다.
- 예: 午 4개와 丑 3개처럼 중복 지지가 있을 때는 단순 평균을 쓰지 않고 가중 벡터 합산을 합니다. 이 경우 합성 방향은 약 316.94°이며 巳火와 辰土 사이, 辰 쪽에 가까운 화/토 구조화 방향으로 해석합니다.

금지:

- “물리학적으로 증명된다”라고 말하지 않습니다.
- “진공이 생긴다”라고 말하지 않습니다.
- “100% 원하는 대로 된다”라고 말하지 않습니다.

## 실제 사건 피드백 저장

`files/saju_feedback_cli.py`는 매일의 일진/시운 분석과 실제 사건 피드백을 함께 저장합니다. 저장 위치는 스킬 코드 폴더가 아니라 사용자 데이터 폴더입니다.

현재 날짜/시간 확인:

```powershell
python ".\files\saju_feedback_cli.py" now
```

`add-event`에서 `--date`나 `--time-text`를 생략하면 Asia/Seoul 기준 현재 날짜와 시간을 자동으로 사용합니다.

- Markdown: `C:\Users\coldp\Documents\ConnectAI\자료\사주_피드백\daily\YYYY-MM-DD.md`
- 사건 로그: `C:\Users\coldp\Documents\ConnectAI\자료\사주_피드백\events.jsonl`
- 연관 분석: `C:\Users\coldp\Documents\ConnectAI\자료\사주_피드백\correlations.jsonl`

일일 로그 초안 생성:

```powershell
python ".\files\saju_feedback_cli.py" init-day --config ".\files\saju_luck_config.example.json" --date 2026-06-07
```

실제 사건 추가:

```powershell
python ".\files\saju_feedback_cli.py" add-event --config ".\files\saju_luck_config.example.json" --date 2026-06-07 --time-text 15:40 --event-type emotion --emotion stress --event-text "일하다가 갑자기 스트레스를 크게 느낌"
```

정정 피드백은 덮어쓰지 않고 별도 사건으로 기록합니다.

```powershell
python ".\files\saju_feedback_cli.py" add-event --config ".\files\saju_luck_config.example.json" --date 2026-06-07 --time-text 15:40 --event-type correction --emotion anger --event-text "아까 일이 아니라 지금 다시 생각나서 화가 남"
```

에이전트는 실제 사건을 저장할 때 해당 시운의 십성, 형충파해합, 십이운성, 십이신살, `matrix.vector_summary` 스냅샷을 함께 저장합니다. 이후 대화에서는 `correlations.jsonl`을 근거로 계산 구조가 실제 사건, 정정, 지연 반응, 물상 대체와 어떻게 연결됐는지 설명합니다.

주간 연결 리포트는 사건이 추가될 때 자동으로 갱신됩니다.

- 위치: `C:\Users\coldp\Documents\ConnectAI\자료\사주_피드백\reports\weekly\YYYY-Www.md`
- 목적: 계산 구조가 실제 사건, 정정, 지연 반응, 물상 대체와 어떻게 연결됐는지 기록합니다.

수동 재생성:

```powershell
python ".\files\saju_feedback_cli.py" weekly-report --week-of 2026-06-07
```

## LangChain 사용법

`files/saju_sipsung_langchain_tool.py`는 선택적 래퍼입니다. LangChain이 없는 환경에서도 핵심 계산기는 작동해야 하므로, LangChain 의존성은 이 파일에만 둡니다.

도구 호출 뒤에는 반환값을 다시 LLM에 넣어 최종 답변을 생성해야 합니다. 도구 출력만 화면에 찍고 끝내면 사용자가 자연어 해설을 받지 못합니다.

## Connect AI 업데이트 안전성

이 패키지는 `Connect AI.exe` 또는 `resources/app.asar`를 수정하지 않습니다. 앱 업데이트가 설치 폴더를 덮어써도, 사용자 워크스페이스의 `내지식\40_템플릿\샤랄라\sipsung-relation-tool` 폴더는 유지됩니다.

## 에이전트 출력 규칙

- 계산 전에는 십성을 추정하지 않습니다.
- 천간 대상은 `primary_sipsung`을 중심으로 설명합니다.
- 지지 대상은 `surface`와 `hidden_stems`를 구분해서 설명합니다.
- 지장간이 여러 개면 본기, 중기, 여기 순서와 비중을 함께 설명합니다.
- 학파 차이가 가능한 지점은 "이 도구의 현재 모드 기준"이라고 밝힙니다.
