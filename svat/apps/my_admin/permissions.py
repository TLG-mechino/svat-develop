

def admin_xulydonhang(user):
    return user.role >= 10

def admin_congtacvienvietbai(user):
    return user.role >= 11

def admin_quanly(user):
    return user.role >= 12