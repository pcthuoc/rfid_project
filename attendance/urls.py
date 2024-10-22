"""iot_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index , name = 'index'),
    path('home/', views.index , name = 'index'),
    path('manage/', views.manage , name = 'manage'),
    path('users/', views.alluser, name = 'alluser'),
    path('update_finger_id/', views.update_finger_id_via_url, name='update_finger_id_via_url'),  # update lại vân tay mới
    path('process/', views.process, name='process'),# điểm danh 
    path('getid/', views.getid, name='getid'),# lấy id điểm danh
    path('download_logs/', views.download_logs, name='download_logs'),

    path('upload-excel/', views.upload_excel, name='upload_excel'),
    path('save-uploaded-data/', views.save_uploaded_data, name='save_uploaded_data'),
    path('edit-student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('card-delete/<int:id>/', views.card_delete, name='card_delete'),
    path('download-excel/', views.download_student_data, name='download_excel'),

    path('cardselect/', views.card , name = 'card'),
   
    path('cardadd/', views.add , name = 'cardadd'),
    path("card-id/<int:pk>/",views.CardUidDetailApiView,name="card-uid-Detail"),
    path('searchuser/', views.search , name = 'search'),
]
