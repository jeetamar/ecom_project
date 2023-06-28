class Password:
    password="Buybetter@123"


def current_user(request):
    curr_usr=request.user
    print(curr_usr)
