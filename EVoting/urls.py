"""EVoting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from EVotingApp.views import *

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('',index),
    path('user/login/', userLogin),
    path('user/register/', userRegister),
    path('admin/login/', adminLogin),
    path('admin/', admin),
    path('user/', user),
    path('logout/', logout),

    path('admin/user/', getUsers),
    path('admin/user/status/<int:id>', userStatus),

    path('admin/candidate/add/', addCandidate),
    path('admin/candidate/', getCandidates),
    path('admin/candidate/status/<int:id>', candidateStatus),

    path('admin/info/', voteInfo),
    path('admin/result/status/<int:id>', resultStatus),

    path('user/verification/<int:user_id>', userVerification),
    path('user/thumb_verification/<int:user_id>', thumb_verification),
    path('user/verify/', verifyUser),
    path('user/vote/', userVote),
    path('user/result/', userResult),
    path('user/getUser/', getUser),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
