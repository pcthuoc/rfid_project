from django.shortcuts import redirect

class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Kiểm tra nếu người dùng chưa đăng nhập, không truy cập trang đăng nhập và không truy cập trang process
        if not request.user.is_authenticated and request.path != '/login/' and request.path != '/process/':
            return redirect('login')
        
        return response
