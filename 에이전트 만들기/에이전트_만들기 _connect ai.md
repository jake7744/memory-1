# Connect AI 에이전트 분석 및 신규 에이전트 추가 가이드

Connect AI의 에이전트 시스템은 **CEO 에이전트가 전체적인 목표를 제어하고, 각 분야의 Specialist 에이전트들에게 세부 태스크를 위임하는 협업 구조(P-Reinforce 아키텍처)**로 설계되어 있습니다.

---

## 1. Connect AI 에이전트들의 구성 및 아키텍처 분석

### A. 에이전트 메타데이터 정의 (`src/agents.ts`)
에이전트들의 ID, 이름, 역할, 이모지, HSL/HEX 색상 코드, 전문 분야(Specialty), 사용자에게 보여질 문구(Tagline), 대화 스타일(Persona) 등은 `src/agents.ts`에 정의되어 관리됩니다.
*   **ceo:** 오케스트레이션 및 작업 분해, 종합 판단을 수행합니다.
*   **youtube (레오):** 유튜브 채널 기획 및 분석을 담당하며 데이터 중심적이고 직설적인 톤을 가집니다.
*   **developer (코다리):** 시니어 풀스택 엔지니어 에이전트입니다. Claude Code처럼 스스로 계획하고, 구현하고, 자가 테스트 루프를 돌리는 방식으로 코딩 작업을 수행합니다.
*   그 외 **instagram, designer, business (현빈), secretary (영숙), editor (루나), writer, researcher** 등의 에이전트가 지정되어 있습니다.
*   `SPECIALIST_IDS` 배열에 지정된 에이전트들만이 CEO가 분배하는 작업의 수행자(Specialist)가 됩니다.

### B. 로컬 작업 공간 구성 (`_agents/<id>/`)
프로그램 초기화 시 각 에이전트의 독립 폴더가 `<지식경로>/_company/_agents/<id>/` 하위에 생성됩니다.
1.  **`goal.md`:** 에이전트의 장/단기 목표, 작업 원칙을 담고 있습니다. 사용자나 에이전트가 이 마크다운을 수정하여 세부 미션을 변경합니다. (기본 템플릿은 `DEFAULT_AGENT_GOALS`에 의해 자동 생성됩니다.)
2.  **`tools.md`:** 해당 에이전트가 사용할 수 있는 도구 카탈로그와 자율 작동 레벨(`AUTONOMY_LEVEL`: 0~3)이 명시되어 있습니다.
3.  **`tools/`:** 에이전트 전용 Python 실행 파일(`.py`), 설정 데이터(`.json`), 설명 마크다운(`.md`)이 보관되는 곳입니다.

### C. 에이전트 협업 & 실행 흐름
1.  **사용자 프롬프트 수신:** 사용자가 지시를 내리면 CEO 에이전트가 이를 1차적으로 수신하여 분석합니다.
2.  **CEO의 태스크 분해:** CEO는 지시사항을 바탕으로 어떤 에이전트들에게 어떤 순서로 작업을 맡길지 계획을 짜고 JSON 포맷(`{"brief": "...", "tasks": [{"agent": "developer", "task": "..."}]}`)으로 결과를 반환합니다.
3.  **태스크 실행 및 Prefetch:**
    *   태스크가 할당된 에이전트가 작동하기 직전, `prefetchAgentRealtimeData`가 호출되어 현재 채널 수치나 외부 API 현황을 가져와 컨텍스트로 미리 주입합니다.
    *   에이전트별 `goal.md`, 공유 비즈니스 결정 로그(`_shared/decisions.md`), 최근 대화 요약 등이 에이전트 LLM의 시스템 프롬프트에 동적으로 빌드되어 호출됩니다.
4.  **도구 실행 & 파일 액션:**
    *   에이전트가 분석 중 필요에 따라 LLM 출력으로 `<run_command>python tools/tool.py</run_command>`를 출력하면 백그라운드 터미널에서 이를 수행하고, 그 아웃풋을 분석 결과에 결합합니다.
    *   마찬가지로 파일 생성이 필요하면 `<create_file>` 태그를 해석하여 익스텐션이 직접 파일을 쓰고 편집합니다.
5.  **최종 보고 및 자동 백업 (Git Sync):**
    *   결과물은 `sessions/` 내에 세션별 마크다운 파일로 기록되고, 처리가 끝나면 깃허브 저장소로 자동 `push` 동기화됩니다.

---

## 2. 프로그램에 새로운 에이전트를 추가하는 방법 (Step-by-Step)

마케팅을 전담할 에이전트(ID: `marketer`, 이름: 마크)를 새로 설계하고 추가한다고 가정했을 때의 작업 절차는 다음과 같습니다.

### Step 1: 에이전트 정보 및 페르소나 등록
`src/agents.ts` 파일에 새 에이전트 객체를 선언하고, `AGENT_ORDER`와 `SPECIALIST_IDS` 배열에 추가합니다.
```typescript
export const AGENTS: Record<string, AgentDef> = {
  // ... 기존 에이전트 목록 ...
  marketer: {
    id: 'marketer',
    name: '마크',
    role: 'Head of Marketing',
    emoji: '📢',
    color: '#3B82F6',
    specialty: '마케팅 캠페인 기획, SEO 분석, 타겟 고객층 분석, 이메일 카피라이팅 기획',
    tagline: '고객 획득과 서비스 홍보 전략을 책임집니다',
    profileImage: 'marketer_profile.png',
    persona: '열정적이고 설득력 있는 톤. ROI와 시장 침투율을 중시하며, 데이터에 기반한 잠재고객 분석 내용을 "사장님"께 제안 형식으로 보고함. 이모지는 📢, 📈, 🚀를 주로 사용.'
  }
};

export const AGENT_ORDER = ['ceo', 'youtube', 'instagram', 'designer', 'developer', 'business', 'secretary', 'editor', 'writer', 'researcher', 'marketer'];
export const SPECIALIST_IDS = ['youtube', 'instagram', 'designer', 'developer', 'business', 'secretary', 'editor', 'writer', 'researcher', 'marketer'];
```

### Step 2: 기본 목표(Goal) 설정 추가
`src/extension.ts` 파일 내부의 `DEFAULT_AGENT_GOALS` 레코드에 마케터 에이전트의 목표 템플릿을 등록합니다. 에이전트가 최초 생성될 때 이 마크다운이 `goal.md`로 시드됩니다.
```typescript
const DEFAULT_AGENT_GOALS: Record<string, string> = {
  // ... 기존 에이전트 목표 목록 ...
  marketer: `# 📢 마크 — 마케팅 에이전트 — 나의 미션
  
${_GOAL_PREAMBLE}
## 장기 목표 (3~6개월)
- 서비스 유입 트래픽 50% 증가 및 광고 전환율 3% 돌파
- 잠재고객 메일링 리스트 2,000명 확보

## 이번 주 목표
- 신규 홍보용 랜딩페이지에 탑재할 카피 3안 분석
- 주요 마케팅 키워드 10개 및 경쟁사 광고 단어 수집

## 작업 원칙
- 마케팅 광고 아이디어 제안 시 예상되는 ROI(투자대비효과)를 반드시 명시
- 단순 마케팅 트렌드 나열 대신 구체적으로 실행 가능한 카피 초안과 타겟 지표 제시
`
};
```

### Step 3: 에이전트 전용 실행 도구(Tools) 설계 및 시드 바인딩
마케터 에이전트만의 독자적인 도구(예: `seo_keywords.py`)가 필요한 경우 추가해 줍니다.
1.  `assets/tool-seeds/marketer/` 디렉토리를 생성하고, `seo_keywords.py`, `seo_keywords.json` (기본 설정값), `seo_keywords.md` (도구 설명서) 파일을 작성합니다.
2.  `src/extension.ts` 파일의 `AGENT_TOOLS_CATALOG`에 마케터 에이전트의 도구 정보를 등록합니다.
    ```typescript
    marketer: [
        { tool: 'seo_keywords', desc: '특정 주제에 대한 인기 키워드 추천 및 검색엔진 노출 강도 분석' }
    ]
    ```
3.  시드 설치 코드를 구현합니다. `_seedMarketerTools` 같은 헬퍼 함수를 선언해 seed 폴더의 자산들을 에이전트의 로컬 폴더로 복사해 주고, `_seedAgentToolsIfMissing(agentId)` 함수에 marketer 분기를 지정합니다.
    ```typescript
    } else if (agentId === 'marketer') {
      const toolsDir = path.join(getCompanyDir(), '_agents', agentId, 'tools');
      fs.mkdirSync(toolsDir, { recursive: true });
      _seedMarketerTools(toolsDir);
    }
    ```

### Step 4: 기본 활성화 지정 및 렌더링 리소스 준비
1.  `src/extension.ts` 상단의 `DEFAULT_ON_AGENTS` 및 `OPTIONAL_AGENTS_DEFAULT` Set에 `'marketer'`를 포함하여 첫 시작 시 활성화 상태가 되도록 합니다.
2.  사용자 화면(Office View)에서 캐릭터가 렌더링될 수 있도록 `assets/pixel/characters/marketer.png`에 캐릭터 스프라이트 파일을 배치합니다.

### Step 5: 컴파일 및 패키징 테스트
모든 수정을 마친 후 익스텐션 소스 코드의 루트 폴더에서 컴파일을 돌려보고 VSIX 설치 패키지를 빌드합니다.
```bash
npm run compile
npx vsce package --no-dependencies
```
생성된 `.vsix` 파일을 설치한 후 VS Code를 재실행하면, 에이전트 팀에 마케터가 새로 추가되고 CEO 에이전트가 마케팅 업무가 발생했을 때 계획을 수립하여 마크에게 태스크를 올바르게 전달하는 모습을 보실 수 있습니다.

---

## 3. 에이전트 전용 스킬(Skill) 주입 시스템 개요

Connect AI 에이전트들은 단순한 지식 저장소(`memory.md`)를 넘어, 특정 반복 작업에 최적화된 **'스킬 패키지'**를 장착하여 실행할 수 있습니다. 스킬을 통해 에이전트는 동일한 품질의 일관된 결과물을 훨씬 빠르고 안정적으로 도출하게 됩니다.

### A. 스킬의 유형 및 장착 방식
1. **성공 산출물 기반 자동 스킬 추출 (RAG):**
   - 대화 중 성공적으로 도출된 에이전트의 산출물에서 LLM(`skill-distill.md` 프롬프트 사용)이 패턴을 요약해 `_agents/{agentId}/skills/<slug>.md`로 자동 큐레이션 및 저장하는 방식입니다.
2. **패키지형 구조적 스킬 주입 (고도화 템플릿):**
   - 보다 복잡하고 반복적인 모듈형 작업을 위해 `manifest.json`, `README.md`, `files/` 폴더를 한 세트로 묶은 **스킬 패키지** 형태로 에이전트에게 지침과 템플릿 코드를 강제하는 설계입니다.

### B. 템플릿 저장 경로 및 파일 구조
스킬 패키지는 아래 경로에 배치하여 에이전트별로 능력을 분리 장착합니다:
```text
내지식\40_템플릿\[에이전트명]\[스킬명]\
```

### C. 고도화 스킬 주입에 관한 상세 가이드
스킬 발동 조건 제어(`intent`, `priority`, `avoid_keywords`), 표준 README.md 행동 지침 작성법, 에이전트 스킬 조합 및 체크리스트 검증 흐름 등 구체적인 스킬 제작과 주입 방법론은 아래의 독립된 상세 가이드 문서를 참조하세요:

👉 **[스킬_주입_시스템_가이드.md](file:///c:/Users/coldp/.connect-ai-brain/%EB%82%B4%EC%A7%80%EC%8B%9D/%EC%8A%A4%ED%82%AC_%EC%A3%BC%EC%9E%85_%EC%8B%9C%EC%8A%A4%ED%85%9C_%EA%B0%80%EC%9D%B4%EB%93%9C.md)**
