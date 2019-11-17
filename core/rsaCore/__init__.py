from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import base64
import os

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__));

RANDOM_GENERATOR=Random.new().read

# 生成公钥、秘钥
def _generateKeys_():
    if os.path.exists(os.path.join(CURRENT_PATH, "rsa-private.pem")) and os.path.exists(os.path.join(CURRENT_PATH, "rsa-public.pem")):
        return;
    rsa = RSA.generate(1024, RANDOM_GENERATOR);
    # 保存秘钥
    PRIVATE_PEM = rsa.exportKey();
    with open(os.path.join(CURRENT_PATH, "rsa-private.pem"), "w") as f:
        f.write(PRIVATE_PEM.decode());
    # 保存公钥
    PUBLIC_PEM = rsa.publickey().exportKey();
    with open(os.path.join(CURRENT_PATH, "rsa-public.pem"), "w") as f:
        f.write(PUBLIC_PEM.decode());

def getPublicKey():
    # 生成公钥、秘钥
    _generateKeys_();
    # 读取公钥
    with open(os.path.join(CURRENT_PATH, "rsa-public.pem"), "r") as f:
        return f.read();
    return "";

global _private_key;

def _getPrivateKey_():
    global _private_key;
    try:
        if isinstance(_private_key, str):
            return _private_key;
    except Exception:
        pass;
    with open(os.path.join(CURRENT_PATH, "rsa-private.pem"), "r") as f:
        _private_key = f.read();
    return _private_key;
    
# 编码字符串
def encodeStr(s):
    rsakey = RSA.importKey(getPublicKey());
    cipher = Cipher_pkcs1_v1_5.new(rsakey);
    return base64.b64encode(cipher.encrypt(s.encode())).decode();

# 解码字符串
def decodeStr(s):
    try:
        rsakey = RSA.importKey(_getPrivateKey_());
        cipher = Cipher_pkcs1_v1_5.new(rsakey);
        return cipher.decrypt(base64.b64decode(s), b"").decode();
    except Exception:
        return "";

# 运行此脚本生成密钥
if __name__ == '__main__':
    _generateKeys_(); # 生成密钥