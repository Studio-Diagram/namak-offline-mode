from django.urls import path
from offline_app import views

urlpatterns = [
    path('create_member/', views.create_member),
    path('create_reserve/', views.create_reserve),
    path('create_waiting_reserve/', views.add_waiting_list),
    path('delete_reserve/', views.delete_reserve),
    path('arrive_reserve/', views.arrive_reserve),
    path('create_new_invoice_sales/', views.create_new_invoice_sales),
    path('end_current_game/', views.end_current_game),
    path('ready_for_settle/', views.ready_for_settle),
    path('print_after_save/', views.print_after_save),
    path('delete_items/', views.delete_items),
    path('delete_invoice/', views.delete_invoice),
]
