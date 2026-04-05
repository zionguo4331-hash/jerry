import requests
from config import SERVER_SEND_KEY, SERVER_API_URL


def send_wechat(title, content):
    """通过 Server酱 推送消息到微信"""
    if not SERVER_SEND_KEY:
        print("Server酱 SendKey 未配置，跳过推送")
        return False

    url = f"{SERVER_API_URL}/{SERVER_SEND_KEY}.send"

    data = {
        "title": title,
        "desp": content,
    }

    try:
        resp = requests.post(url, data=data, timeout=15)
        resp.raise_for_status()
        result = resp.json()

        if result.get("code") == 0:
            print("推送成功！")
            return True
        else:
            print(f"推送失败: {result}")
            return False
    except Exception as e:
        print(f"推送异常: {e}")
        return False
