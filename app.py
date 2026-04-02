from flask import Flask, render_template, request
import base64
import requests
import json

# 个人信息&百度密钥
STUDENT_ID = "202335020537"
STUDENT_NAME = "汤明婷"
API_KEY = "bOhC5kIeul0K1psuvNXBmEZU"
SECRET_KEY = "goYnWWb842iuWYz6MaoldJUM8cBYkBaC"

app = Flask(__name__)

# Token获取逻辑
def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": SECRET_KEY
    }
    try:
        response = requests.post(url, params=params, timeout=10)
        return str(response.json().get("access_token"))
    except:
        return None

# 适配网页上传的图片转base64
def img_to_base64(file_data):
    return base64.b64encode(file_data).decode("utf8")

def ai_recognize(base64_img):
    try:
        token = get_access_token()
        if not token:
            return "❌ 获取Token失败，请检查网络或API_KEY"

        url = "https://aip.baidubce.com/stream/2.0/image-classify/v1/object_recognition?access_token=" + token

        payload = json.dumps({
            "image": base64_img,
            "search_mode": "auto",
            "search_result": False,
            "baike_result": False
        }, ensure_ascii=False)

        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"), timeout=15)
        response.encoding = "utf-8"

        desc_list = []
        for line in response.text.splitlines():
            if line.startswith("data:"):
                json_str = line[5:].strip()
                try:
                    json_data = json.loads(json_str)
                    desc = json_data.get("result", {}).get("description", "")
                    if desc:
                        desc_list.append(desc)
                except:
                    continue

        full_result = "".join(desc_list)
        if full_result:
            return f"✅ 识别成功！\n\n{full_result}"
        else:
            return "⚠️ 未识别到有效物体，请更换清晰图片重试"

    except Exception as e:
        return f"❌ 识别失败：{str(e)}"

# 主页：固定显示学号+姓名
@app.route('/')
def index():
    return render_template("index.html", sid=STUDENT_ID, name=STUDENT_NAME)

# 图片上传+识别接口
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get("img")
    if not file:
        return "❌ 未选择图片"
    img_data = file.read()
    b64 = img_to_base64(img_data)
    return ai_recognize(b64)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
