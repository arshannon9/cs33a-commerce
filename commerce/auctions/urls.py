from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing_detail/<int:id>", views.listing_detail, name="listing_detail"),
    path("toggle_watchlist/<int:id>",
         views.toggle_watchlist, name="toggle_watchlist"),
    path("make_bid/<int:listing_id>/<int:user_id>/",
         views.make_bid, name="make_bid"),
    path("close_auction/<int:listing_id>",
         views.close_auction, name="close_auction"),
    path("add_comment/<int:listing_id>", views.add_comment, name="add_comment"),
    path("watchlist", views.watchlist, name="watchlist"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
