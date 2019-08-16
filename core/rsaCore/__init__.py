from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import base64
import os

RANDOM_GENERATOR=Random.new().read

# 生成公钥、秘钥
def _generateKeys_():
    if os.path.exists("rsa-private.pem") and os.path.exists("rsa-public.pem"):
        return;
    rsa = RSA.generate(1024, RANDOM_GENERATOR);
    # 保存秘钥
    PRIVATE_PEM = rsa.exportKey();
    with open("rsa-private.pem", "w") as f:
        f.write(PRIVATE_PEM.decode());
    # 保存公钥
    PUBLIC_PEM = rsa.publickey().exportKey();
    with open("rsa-public.pem", "w") as f:
        f.write(PUBLIC_PEM.decode());

global _private_key;

def _getPrivateKey_():
    global _private_key;
	try:
		if isinstance(_private_key, str):
			return _private_key;
	except Exception:
        pass;
    with open("rsa-private.pem", "r") as f:
        _private_key = f.read();
	return _private_key;

# 解码字符串
def decodeStr(s):
    rsakey = RSA.importKey(_getPrivateKey_());
    cipher = Cipher_pkcs1_v1_5.new(rsakey);
    return cipher.decrypt(base64.b64decode(s), RANDOM_GENERATOR);

# 运行此脚本生成密钥
if __name__ == '__main__':
    _generateKeys_(); # 生成密钥