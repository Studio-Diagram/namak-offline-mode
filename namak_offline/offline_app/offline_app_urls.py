from django.urls import path
from offline_app.offline_views import offlineMemberView, offlineSyncView

urlpatterns = [
    path('addMember/', offlineMemberView.add_member),
    path('getMembers/', offlineMemberView.get_members),
    path('searchMember/', offlineMemberView.search_member),
    path('syncWithOnline/', offlineSyncView.sync_offline_server_with_online),
]
