from functools import wraps
from django.http import HttpResponseNotAllowed, HttpResponse

def group_required(groups):
    def inner(original_func):

        @wraps(original_func)
        def wrapper_func(request, *args, **kwargs): 
            if request.user.groups.filter(name__in=groups).exists():
                return original_func(request, *args, **kwargs)
            else:
                return  HttpResponse("Permission denied") 

        return wrapper_func
    return inner 


