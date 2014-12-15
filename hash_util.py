import hashlib
import hmac
import random
import string

SECRET = 'pandas_are_awesome'

def hash_cookie(val):
    return hmac.new(SECRET,val).hexdigest()

def secure_cookie(val):
    hashed_cookie_val = hash_cookie(val)
    return "%s|%s" % (val, hashed_cookie_val)

def validate_cookie(h):
    split_hash = h.split('|')
    val, hashed_val = split_hash[0], split_hash[1]
    if hash_cookie(val) == hashed_val:
        return val
    else:
        return None


def make_salt():
    """
    Create a salt for use in password and cookie hashing.
    """
    output = ''
    for n in range(5):
        output += random.choice(string.letters)
    return output

salt = make_salt()

def hash_item(name, pw, salt=salt):
    """
    Hash a username+password given the item and a salt.
    """
    hashed_item = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s,%s" % (hashed_item,salt)

def validate_item(name, pw, h):
    """
    Validate whether a username+password matches a provided hash (sha256 encoded with a salt).
    """
    split_hash = h.split(',')
    hashed_item, salt = split_hash[0], split_hash[1]
    if hash_item(name, pw, salt=salt) == h:
        return True
    else:
        return False

