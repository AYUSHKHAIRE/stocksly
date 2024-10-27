from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home_redirect),
    path('get_available_stocks/', views.get_available_stocks),
    path('get_stock_daily_data/',views.not_get_stockname),
    path('get_stock_daily_data/<str:stocksymbol>/', views.get_stocks_daily_data),
    path('get_stock_daily_data_chart/<str:stocksymbol>/', views.get_stocks_daily_data_chart),
    path('get_stock_per_minute_data/',views.not_get_stockname),
    path('get_stock_per_minute_data/<str:stocksymbol>/', views.get_stocks_per_minute_data),
    path('get_stock_per_minute_data_chart/<str:stocksymbol>/', views.get_stocks_per_minute_data_chart),
]