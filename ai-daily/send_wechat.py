import requests
from config import SERVER_SEND_KEYS, SERVER_API_URL


def send_wechat(title, content):
    """通过 Server酱 推送消息到多个微信"""
    if not SERVER_SEND_KEYS:
        print("Server酱 SendKey 未配置，跳过推送")
        return False

    success_count = 0
    for i, key in enumerate(SERVER_SEND_KEYS):
        if not key:
            continue

        url = f"{SERVER_API_URL}/{key}.send"
        data = {
            "title": title,
            "desp": content,
        }

        try:
            resp = requests.post(url, data=data, timeout=15)
            resp.raise_for_status()
            result = resp.json()

            if result.get("code") == 0:
                print(f"推送成功！发送到微信 {i+1}")
                success_count += 1
            else:
                print(f"微信 {i+1} 推送失败: {result}")
        except Exception as e:
            print(f"微信 {i+1} 推送异常: {e}")

    print(f"共推送到 {success_count}/{len(SERVER_SEND_KEYS)} 个微信")
    return success_count > 0