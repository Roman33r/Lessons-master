from werkzeug.security import generate_password_hash, check_password_hash

hash = generate_password_hash("123456")
print(hash)

check = check_password_hash(hash,"123456")
print(check)
