import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
import arabic_reshaper
from bidi.algorithm import get_display

HOST = "127.0.0.1"
PORT = 8080

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen2.5:1.5b"
MAX_PAYLOAD_SIZE = 1024 * 1024  # 1MB Max Payload

def fix_arabic(text):
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

class LocalBridgeHandler(BaseHTTPRequestHandler):
    def send_json(self, status, content):
        response = json.dumps(content, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def do_POST(self):
        if self.path != "/bridge":
            self.send_json(404, {"error": "المسار غير مدعوم."})
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            if length > MAX_PAYLOAD_SIZE:
                self.send_json(413, {"error": "حجم الطلب كبير جداً."})
                return

            body = self.rfile.read(length).decode("utf-8")
            request_data = json.loads(body)

            task = request_data.get("task")
            messages = request_data.get("messages", [])

            if task != "ask_llm":
                self.send_json(400, {"error": "مهمة غير معروفة."})
                return

            if not messages or not isinstance(messages, list):
                self.send_json(400, {"error": "صيغة الرسائل غير صحيحة."})
                return

            ollama_payload = {
                "model": MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 150
                }
            }

            data = json.dumps(ollama_payload, ensure_ascii=False).encode("utf-8")

            ollama_req = urllib.request.Request(
                OLLAMA_URL,
                data=data,
                headers={"Content-Type": "application/json; charset=utf-8"},
                method="POST"
            )

            with urllib.request.urlopen(ollama_req, timeout=120) as ollama_res:
                ollama_data = json.loads(ollama_res.read().decode("utf-8"))

            message_obj = ollama_data.get("message", {})
            answer = message_obj.get("content", "").strip()

            if not answer:
                answer = "لم يتم توليد إجابة من النموذج."

            self.send_json(200, {
                "status": "success",
                "response": answer
            })

        except urllib.error.URLError:
            self.send_json(503, {"error": "تعذر الاتصال بمحرك Ollama المحلي."})
        except json.JSONDecodeError:
            self.send_json(400, {"error": "بيانات JSON غير صالحة."})
        except Exception as e:
            self.send_json(500, {"error": f"خطأ داخلي: {str(e)}"})

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    print(fix_arabic(f"MOD Local Bridge يعمل على: http://{HOST}:{PORT}/bridge"))
    print(fix_arabic(f"توجيه الطلبات إلى: {OLLAMA_URL} ({MODEL})"))
    
    server = HTTPServer((HOST, PORT), LocalBridgeHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n" + fix_arabic("تم إيقاف الجسر المحلي."))
    finally:
        server.server_close()
