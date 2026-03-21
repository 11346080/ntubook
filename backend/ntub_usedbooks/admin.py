from django.contrib import admin


class NtubAdminSite(admin.AdminSite):
    site_header = '北商傳書後台管理系統'
    site_title = 'NTUB Used Books Admin'
    index_title = '系統管理首頁'


ntub_admin_site = NtubAdminSite(name='ntub_admin')
