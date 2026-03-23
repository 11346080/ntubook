from django.urls import path
from . import views

urlpatterns = [
    path('campuses/', views.campus_list_api, name='api-campus-list'),
    path('program-types/', views.programtype_list_api, name='api-programtype-list'),
    path('departments/', views.department_list_api, name='api-department-list'),
    path('class-groups/', views.classgroup_list_api, name='api-classgroup-list'),
]
