from django.urls import path
from . import views

app_name = 'explorer'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/plugins/', views.get_plugins, name='get_plugins'),
    path('api/load-graph/', views.load_graph, name='load_graph'),
    path('api/upload-graph/', views.upload_graph, name='upload_graph'),
    path('api/switch-workspace/', views.switch_workspace, name='switch_workspace'),
    path('api/visualize/', views.visualize, name='visualize'),
    path('api/search/', views.search, name='search'),
    path('api/filter/', views.filter_graph, name='filter'),
    path('api/reset/', views.reset, name='reset'),
    path('api/tree-view/', views.tree_view, name='tree_view'),
    path('api/bird-view/', views.bird_view, name='bird_view'),
    path('api/node-details/', views.get_node_details, name='node_details'),
]