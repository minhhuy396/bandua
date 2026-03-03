from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # 👇 dòng này liên kết app store
    path('', include('store.urls')),
]

# 👇 cho phép load ảnh media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)