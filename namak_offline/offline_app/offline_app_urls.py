from django.urls import path
from offline_app.offline_views import offlineMemberView, offlineSyncView, offlineCashView, offlineInvoiceSaleView, \
    offlineReserveView

urlpatterns = [
    path('addMember/', offlineMemberView.add_member),
    path('getMembers/', offlineMemberView.get_members),
    path('searchMember/', offlineMemberView.search_member),
    path('syncWithOnline/', offlineSyncView.sync_offline_server_with_online),
    path('getTodayCash/', offlineCashView.get_today_cash),
    path('getMenuItemsWithCategories/', offlineInvoiceSaleView.get_menu_items_with_categories),
    path('getTables/', offlineInvoiceSaleView.get_tables),
    path('getMenuItems/', offlineInvoiceSaleView.get_menu_items),
    path('getMember/', offlineMemberView.get_member),
    path('getAllTodayInvoices/', offlineInvoiceSaleView.get_all_today_invoices),
    path('getInvoice/', offlineInvoiceSaleView.get_invoice),
    path('getTodayStatus/', offlineInvoiceSaleView.get_today_status),
    path('getTodayForReserve/', offlineReserveView.get_today_for_reserve),
    path('getWorkingTime/', offlineReserveView.get_working_time_for_reserve),
    path('getAllReserves/', offlineReserveView.get_reserves),
    path('getWaitingList/', offlineReserveView.get_waiting_list_reserves),
    path('addReserve/', offlineReserveView.add_reserve),
    path('arriveReserve/', offlineReserveView.arrive_reserve),
    path('deleteReserve/', offlineReserveView.delete_reserve),
    path('getReserve/', offlineReserveView.get_reserve),
    path('addWaitingList/', offlineReserveView.add_waiting_list),
    path('addInvoiceSales/', offlineInvoiceSaleView.create_new_invoice_sales),
    path('endCurrentGame/', offlineInvoiceSaleView.end_current_game),
    path('readyForSettle/', offlineInvoiceSaleView.ready_for_settle),
    path('printAfterSave/', offlineInvoiceSaleView.print_after_save),
    path('deleteInvoiceSale/', offlineInvoiceSaleView.delete_invoice),
    path('deleteItems/', offlineInvoiceSaleView.delete_items),
    path('settleInvoiceSale/', offlineInvoiceSaleView.settle_invoice_sale),
    path('closeCash/', offlineCashView.close_cash),
    path('openCash/', offlineCashView.open_cash)
]
