from django.urls import path
from .views import SignUpView, TokenObtainView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('token/', TokenObtainView.as_view(), name='token_obtain'),
]
