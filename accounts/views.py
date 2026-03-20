from django.views.generic import TemplateView, FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout
from django.shortcuts import redirect

from .forms import UserProfileForm
from .models import UserProfile


# =============================================================================
# OAuth 入口頁（GET only）
# 頁面只有說明文字 + 「使用 @ntub.edu.tw Google 帳號登入」按鈕。
# 按鈕 href="/accounts/google/login/"（藍圖 URL，W5 以後實作 OAuth 串接）。
# =============================================================================
class OAuthEntryView(TemplateView):
    template_name = 'accounts/login.html'


# =============================================================================
# 登出
# =============================================================================
def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')


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


# =============================================================================
# 會員 Dashboard（W4 最小骨架頁）
# LoginRequiredMixin：未登入時自動 redirect 到 login
# =============================================================================
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_tab'] = self.request.GET.get('tab', 'profile')
        user = self.request.user
        try:
            ctx['user_profile'] = user.profile
        except UserProfile.DoesNotExist:
            ctx['user_profile'] = None
        ctx['unread_notification_count'] = 0  # TODO: 實作通知未讀數
        return ctx


# =============================================================================
# 編輯個人資料（分頁 1：Edit Profile）
# =============================================================================
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = '/accounts/dashboard/?tab=profile'

    def get_object(self):
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj is None:
            return redirect('accounts:first_login')
        return super().get(request, *args, **kwargs)
