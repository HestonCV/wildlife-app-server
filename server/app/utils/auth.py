import bcrypt

def generate_hashed_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(hashed_password, password_attempt):
    return bcrypt.checkpw(password_attempt.encode('utf-8'), hashed_password.encode('utf-8'))
