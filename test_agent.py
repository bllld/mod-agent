import urllib.request
import urllib.error
import json

BRIDGE_URL = "http://127.0.0.1:8080/bridge"

def run_test(name, payload, expected_status, check_key=None):
    print(f"Testing: {name} ... ", end="")
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BRIDGE_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as res:
            status = res.status
            body = json.loads(res.read().decode("utf-8"))
            if status == expected_status and (check_key is None or check_key in body):
                print("PASSED ✅")
            else:
                print(f"FAILED ❌ (Status: {status}, Body: {body})")
    except urllib.error.HTTPError as e:
        if e.code == expected_status:
            print(f"PASSED ✅ (Expected HTTP {e.code})")
        else:
            print(f"FAILED ❌ (HTTP {e.code})")
    except Exception as e:
        print(f"FAILED ❌ (Error: {e})")

# 1. اختبار Payload غير صالح
run_test("Invalid Payload / Empty JSON", {}, 400)

# 2. اختبار Task غير مدعومة
run_test("Unknown Task", {"task": "invalid_task", "messages": []}, 400)

# 3. اختبار طلب صحيح للهيكل
run_test("Valid Chat Structure", {
    "task": "ask_llm",
    "messages": [{"role": "user", "content": "مرحبا"}]
}, 200, "response")
