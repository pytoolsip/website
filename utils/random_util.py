import random
import string

def randomMulti(length):
    return ''.join(random.sample(string.ascii_letters + string.digits, length));

def randomStr(length):
    return ''.join(random.sample(string.ascii_letters, length));

def randomNum(length):
    return ''.join(random.sample(string.digits, length));