from django.urls import path
from .views import *

urlpatterns = [
    path('create-ride/', RideCreateView.as_view(), name='ride-create'),
    path('ride-details/<int:id>/', RideDetailView.as_view(), name='ride-detail'),
    path('my-rides/', RideListView.as_view(), name='ride-list'),
    path('<int:ride_id>/update-status/', RideStatusUpdateView.as_view(), name='ride-update-status'),
    path('accept-ride/', DriverAcceptRideView.as_view(), name='driver-accept-ride'),
    path('<int:ride_id>/update-location/', RideTrackingUpdateView.as_view(), name='update-ride-location'),
    path('<int:ride_id>/match-driver/', MatchRideView.as_view(), name='ride-match-driver'),

]
