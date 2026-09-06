import json
import urllib.request
import urllib.error
import subprocess
import arabic_reshaper
from bidi.algorithm import get_display

BRIDGE_URL = "http://127.0.0.1:8080/bridge"

def fix_arabic(text):
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

def trigger_toast(text):
    try:
        subprocess.run(["termux-toast", "-g", "middle", text], check=False)
    except FileNotFoundError:
        pass

def load_user_profile():
    try:
        with open("user_profile.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"user": {}, "facts": {}}

def resolve_memory(question, profile):
    clean_q = question.strip().lower()
    facts = profile.get("facts", {})
    
    # 1. Fact Resolution (الحقائق والمطابقة المباشرة)
    for key, data in facts.items():
        if key in clean_q:
            if isinstance(data, dict):
                return data.get("value")
            return data
    return None

user_profile = load_user_profile()
user_data = user_profile.get("user", {})

SYSTEM_IDENTITY = (
    "أنت MOD AGENT، مساعد محلي ذكي يعمل بالكامل داخل بيئة Termux للمبرمج مود.\n"
    "طبيعة عملك: دقيق، موجه للبرمجة وإدارة النظام، وتعتمد على الحقائق الموثوقة.\n"
    "قواعد الرد:\n"
    "- أجب بالعربية دائماً وبشكل مباشر.\n"
    "- لا تخترع أو تخمن أي معلومات غير متوفرة في الذاكرة."
)

def build_system_prompt(u_data):
    return (
        f"{SYSTEM_IDENTITY}\n\n"
        f"معلومات المستخدم المحلية (User Context):\n"
        f"- الاسم: {u_data.get('name', 'مود')}\n"
        f"- الدور: {u_data.get('role', 'المطور')}\n"
        f"- البيئة: {u_data.get('environment', 'Termux')}\n"
    )

conversation_history = [
    {"role": "system", "content": build_system_prompt(user_data)}
]

print(fix_arabic("MOD Communication Agent Ready (Local Mode)."))
print(fix_arabic("اكتب سؤالك، أو اكتب خروج لإنهاء الجلسة.\n"))

while True:
    try:
        question = input("You: ").strip()
    except KeyboardInterrupt:
        print("\n" + fix_arabic("تم الإغلاق."))
        break

    if not question:
        continue

    if question.lower() in ("exit", "quit", "خروج"):
        print(fix_arabic("تم إغلاق المحادثة."))
        break

    # Path 1: Memory Resolver (FACTS - 0ms LLM Overhead)
    direct_fact = resolve_memory(question, user_profile)
    if direct_fact:
        conversation_history.append({"role": "user", "content": question})
        conversation_history.append({"role": "assistant", "content": direct_fact})
        print("\nAssistant (Local Memory):\n" + fix_arabic(direct_fact) + "\n")
        trigger_toast(direct_fact)
        continue

    # Path 2: LLM Reasoning (Qwen via Local Bridge)
    conversation_history.append({"role": "user", "content": question})

    payload = {
        "task": "ask_llm",
        "messages": conversation_history
    }

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(
        BRIDGE_URL,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))

        answer = result.get("response", "لم يصل رد من الجسر المحلي.").strip()
        conversation_history.append({"role": "assistant", "content": answer})

        print("\nAssistant (LLM Reasoning):\n" + fix_arabic(answer) + "\n")
        trigger_toast(answer)

    except urllib.error.HTTPError as error:
        print("\n" + fix_arabic(f"خطأ في الجسر المحلي: HTTP {error.code}\n"))
    except urllib.error.URLError as error:
        print("\n" + fix_arabic(f"تعذر الاتصال بالجسر المحلي: {error.reason}\n"))
    except json.JSONDecodeError:
        print("\n" + fix_arabic("استجابة غير صالحة من الجسر.\n"))
    except Exception as error:
        print("\n" + fix_arabic(f"حدث خطأ: {error}\n"))
