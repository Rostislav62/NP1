from django.contrib.auth.models import User

def user_context(request):
    return {
        'user': request.user
    }
