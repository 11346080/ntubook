from django.views.generic import TemplateView


# =============================================================================
# OAuth 入口頁（GET only）
# 頁面只有說明文字 + 「使用 @ntub.edu.tw Google 帳號登入」按鈕。
# 按鈕 href="/accounts/google/login/"（藍圖 URL，W5 以後實作 OAuth 串接）。
# =============================================================================
class OAuthEntryView(TemplateView):
    template_name = 'accounts/login.html'
