from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from .forms import UserProfileForm


# =============================================================================
# OAuth 入口頁（GET only）
# 頁面只有說明文字 + 「使用 @ntub.edu.tw Google 帳號登入」按鈕。
# 按鈕 href="/accounts/google/login/"（藍圖 URL，W5 以後實作 OAuth 串接）。
# =============================================================================
class OAuthEntryView(TemplateView):
    template_name = 'accounts/login.html'


# =============================================================================
# 首次登入：建立 UserProfile（含 display_name、student_no、program_type、
# department、class_group、grade_no）
# GET：若已有 profile 直接 redirect；否則顯示表單
# POST：建立 UserProfile 後 redirect
# =============================================================================
class FirstLoginView(LoginRequiredMixin, FormView):
    template_name = 'accounts/first_login.html'
    form_class = UserProfileForm
    success_url = '/accounts/dashboard/'

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'profile'):
            return redirect('/accounts/dashboard/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)
