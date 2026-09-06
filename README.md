# MOD Agent (Local Termux Architecture)

MOD Agent هو مساعد شخصي محلي يعمل بالكامل داخل بيئة Android Termux بنمط Local-First وبدون أي استدعاء لخدمات أو مفاتيح API خارجية.

---

## مبادئ التصميم الأساسية (Core Principles)

- Local-First & Zero External API Keys: الاتصال بين المكونات يتم محلياً بالكامل عبر 127.0.0.1 بدون الحاجة إلى أي API Keys.
- Architecture-Based Security: حماية معمارية معتمدة على الـ Loopback Binding، معالجة أخطاء المدخلات، وتحديد الحد الأقصى لحجم البيانات المقبولة (1MB Payload Limit).
- Deterministic Memory vs. LLM Reasoning: الفصل التام بين الحقائق الثابتة المسجلة في الذاكرة المباشرة، وبين الأسئلة البرمجية والتحليلية التي تحال إلى النموذج.

---

## معمارية النظام (System Architecture)

MOD Communication Agent (client.py)
       │
  ┌────┴────────────────────────┐
  │                             │
Memory Resolver            LLM Reasoning
  │                             │
user_profile.json             Qwen
(User Facts)               (Analysis/Coding)
  │                             │
  └────┬────────────────────────┘
       ↓
Local Bridge (server.py) -> 127.0.0.1:8080
       ↓
Termux / Android
       ↓
Ollama (/api/chat)

---

## حالة المشروع والميزات المختبرة (Implemented & Verified)

- Memory Resolver (Fast Path - No LLM Invocation): فحص الأسئلة المباشرة المتعلقة بحقائق المستخدم والرد عليها فوراً من الذاكرة دون استهلاك الوقت أو موارد النموذج.
- LLM Reasoning Path: توجيه المحادثات الاستنتاجية والتحليلية إلى النموذج المحلي qwen2.5:1.5b عبر مسار /api/chat.
- Hardened Local Bridge: سيرفر خفيف يعتمد على بايثون القياسي على المنفذ 8080 مع تدقيق هيكلية الـ JSON والحد الأقصى للبيانات.
- RTL & OS Integration: دعم كامل للغة العربية وتفاعل مع نظام أندرويد عبر termux-toast.
- Automated Test Suite: سكربت اختبارات تلقائية (test_agent.py) للتحقق من أمان الجسر وصحة مسارات البيانات.

---

## طريقة التشغيل والإنشاء المحلي

1. تشغيل السيرفر المحلي:
python server.py

2. تشغيل الـ Agent والعميل:
python client.py

3. تشغيل وحدة الاختبارات:
python test_agent.py

---

## هيكلة الملفات
- server.py: الجسر المحلي الرابط بين العميل ومحرك Ollama.
- client.py: العميل والـ Agent الذي يدير الذاكرة والمنطق.
- user_profile.json: ذاكرة البيانات والحقائق الثابتة للمستخدم.
- test_agent.py: سكربت الاختبارات والتحقق البرمجي.
- README.md: ملف التوثيق المعماري الرسمي.
