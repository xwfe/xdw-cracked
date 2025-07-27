import json
import hmac
import hashlib
import time

def get_secret_key() -> bytes:
    """解密并返回 HMAC 密钥。此函数已验证无误。"""
    obfuscated_key = bytearray([
        0x4F, 0x06, 0x48, 0x6C, 0x59, 0x5A, 0x59, 0x55, 0x52, 0x77, 0x6B, 0x6C, 0x1D, 0x06, 0x05, 0x5A,
        0x13, 0x53, 0x00, 0x14, 0x11, 0x01, 0x61, 0x34, 0x77, 0x70, 0x29, 0x01, 0x1F, 0x1A, 0x05, 0x11
    ])
    obfuscated_key[0] = 101
    i = 1
    while i < len(obfuscated_key):
        decrypted_byte = obfuscated_key[i] ^ (i + 42)
        obfuscated_key[i] = decrypted_byte
        if decrypted_byte == 0: break
        i += 1
    return bytes(obfuscated_key[:i])

def forge_server_response(user_info_dict: dict) -> dict:
    """
    接收一个 user_info 字典，动态生成时间戳和签名，
    并返回一个可以通过验证的完整对象。
    """
    user_info_string = json.dumps(user_info_dict, separators=(',', ':'), sort_keys=False)
    timestamp = int(time.time())
    data_to_sign = f"{user_info_string}{timestamp}"
    secret_key = get_secret_key()
    computed_hmac = hmac.new(secret_key, data_to_sign.encode('utf-8'), hashlib.sha256).digest()
    valid_sign_hex = computed_hmac.hex()

    forged_response = {
        "timestamp": timestamp,
        "sign": valid_sign_hex,
        "user_info": user_info_string
    }

    return forged_response

def write_utools_script(filename: str, response_data: dict):
    """
    将伪造的服务器响应数据格式化并写入到 uTools 脚本文件中。
    """
    # 1. 将 Python 字典转换为 JSON 字符串，用于嵌入到 JS 代码中
    #    这里需要两次 JSON 转换：
    #    第一次：将 response_data（Python 字典）转换成 JSON 字符串
    #    这样它就可以被正确地插入到 JS 模板中
    body_content_json = json.dumps(response_data, indent=2, ensure_ascii=False)

    # 2. 构建 uTools 脚本模板
    script_template = f"""$done({{
  status: 200,
  body: JSON.stringify(
    {body_content_json}
  )
}})
"""

    # 3. 将内容写入文件，使用 utf-8 编码
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(script_template)
        print(f"✅ 成功！已生成 uTools 脚本文件: '{filename}'")
        print("   现在您可以将此文件用于 uTools 的网络请求重写功能。")
    except IOError as e:
        print(f"❌ 错误：无法写入文件 '{filename}'。原因: {e}")

# --- 主程序 ---
if __name__ == "__main__":
    # 定义你的 user_info 数据
    my_user_info = {
        "id": 110, # ID
        "uid": "test", # 用户ID
        "nickname": "XeeMan", # 昵称
        "cellphone": "18822228888", # 手机号
        "avatar": "https://testingcf.jsdelivr.net/gh/macklee6/hahah/c399002482ef17d9a8c5a90fb876776e.gif", # 头像
        "country_code": 86, # 国家代码
        "is_activated": True,
        "db_secrect_key": "test_key", # 数据库密钥
        "db_sync": 0,# 数据库同步开关
        "type": 1,# 用户类型 （会员1 普通用户0）
        "token_expired_at": 4070908800, "create_at": 8888888888,
        "expired_at": 8888888888, # 会员到期日
        "utools_last_login": "2045-05-22", "token": "", "access_token": "", "teams": [{"uid": "uid0001"}]
    }

    # 1. 生成伪造的服务器响应
    forged_data = forge_server_response(my_user_info)

    # 2. 将响应写入到指定的 uTools 脚本文件中
    output_filename = "utools-profile.js"
    write_utools_script(output_filename, forged_data)
