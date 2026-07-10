# 💻 코다리 (시니어 풀스택 엔지니어) 개인 메모리

_코다리 에이전트만 읽고 쓰는 개인 노트. 학습·교훈·자주 쓰는 패턴이 누적됩니다._

## 학습 기록

- [2026-06-21] designer가 제공할 비주얼 브리프를 기반으로, Stripe 또는 국내 PG사 연동이 가능한 최소 기능 제품(MVP) 형태의 랜딩 페이지 웹 프로토타입 구조를 작성하고 코드를 구현하시오. 결제 플로우와 핵심 CTA 버튼을 중심으로 하며, 현재는 플레이스홀더 콘텐츠로 구성하되 실제 판매 환경에 즉시 투입될 수 있는 프레임워크 형태로 완성해야 한다. → 산출물 sessions/2026-06-21T15-50/developer.md
- [2026-06-21] business 에이전트가 결정할 최종 가격대와 번들 상품 구성을 가정하여, 랜딩 페이지의 'PricingSection' 프로토타입을 완성하고, 가상의 결제 플로우(PG 연동 시뮬레이션)를 포함한 테스트 환경 배포 코드를 작성 및 수정하십시오. 실제 판매에 투입될 수 있도록 오류 검증과 기능 구현을 최우선으로 합니다. → 산출물 sessions/2026-06-21T16-50/developer.md
- [2026-06-21] designer가 제공한 '즉시 적용 가능성'을 강조하는 비주얼 자산 5종(Mockup, 배너)과 Deep Navy Blue(#0A1932) 기반의 가이드라인을 활용하여, 랜딩 페이지 MVP를 즉시 판매 가능한 형태로 구현하십시오. 핵심은 결제 플로우와 CTA 버튼이 가장 눈에 잘 띄고 명확하게 작동하도록 하는 것입니다. (결제 시스템 연동 테스트 코드를 포함할 것) → 산출물 sessions/2026-06-21T17-35/developer.md
- [2026-06-21] designer가 제공할 '결과물 Mockup' 비주얼 자산을 활용하여, 랜딩 페이지 MVP의 핵심 가치 증명 영역에 동적 콘텐츠(Dynamic Content) 삽입을 테스트하고 구현하십시오. 이 기능은 단순 이미지가 아니라 사용자가 '실제 결과를 보는 듯한' 인터랙티브 요소를 포함해야 하며, 오류 없이 부드럽게 로드되는지 유효성 검증을 완료합니다. 이와 함께, 최종 CTA 버튼 근처에 배치될 간결한 '즉시 적용 가능 미니 가이드(Mini-Guide)' 섹션의 기능적 프레임워크도 준비하십시오. → 산출물 sessions/2026-0
- [2026-07-09] Complete the payment gateway integration in `components/PaymentCheckout.jsx`. Wire Stripe Elements with auth token from `/api/auth/login`, implement webhook handler for `checkout_session.completed` at `/api/webhooks/stripe`, and add loading/error states matching design system. Test flow end-to-end. 
- [2026-07-09] Complete Stripe payment integration testing: verify session creation, webhook signature validation, and frontend UI state sync (loading/error states) for the paid subscription flow on the landing page MVP. → 산출물 sessions/2026-07-09T23-14/developer.md
- [2026-07-10] Create a `.env` file in the root directory of the Matrixonic project. Add `OPENAI_API_KEY=[YOUR-KEY]` inside it (do not commit this file to git). Also update `.gitignore` or ensure any existing environment variables are correctly mapped so that all agents can read and use this key for LLM communicat