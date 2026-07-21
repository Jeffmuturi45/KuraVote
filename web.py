from py_vapid import Vapid
v = Vapid()
v.generate_keys()
print('PUBLIC:', v.public_key.decode())
print('PRIVATE:', v.private_key.decode())