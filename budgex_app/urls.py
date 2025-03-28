from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.login,name='login'),
    path('login',views.login, name='login'),
    path('register',views.register,name='register'),
    path('index',views.index,name='index'),
    path('transactions',views.transactions,name='transactions'),
    path('budget',views.budget,name='budget'),
    path('reports',views.reports,name='reports'),
    path('settings',views.settings,name='settings'),
    path('addtransaction',views.addtransaction,name='addtransaction'),
    path('addbudget',views.addbudget,name='addbudget'),
    path('logout',views.logout,name='logout'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
    path('convert',views.convert_currency_view,name='convert_currency_view')

]
