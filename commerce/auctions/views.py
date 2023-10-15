from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from auctions.models import User, Listing, Bid, Comment, Category
from auctions.forms import ListingForm


@login_required
def index(request):
    listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {"listings": listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            new_listing = form.save(commit=False)
            new_listing.user = request.user
            new_listing.current_price = new_listing.starting_bid
            new_listing.save()
            return redirect('listing_detail', id=new_listing.id)
        else:
            print(form.errors)
    else:
        form = ListingForm()
    return render(request, 'auctions/create_listing.html', {'form': form})


@login_required
def listing_detail(request, id):
    listing = get_object_or_404(Listing, id=id)
    num_bids = Bid.objects.filter(listing=listing).count()
    current_price = Bid.objects.filter(
        listing=listing).order_by('-bid_amount').first()
    is_highest = current_price.bidder == request.user if current_price else False

    context = {
        'listing': listing,
        'num_bids': num_bids,
        'is_highest': is_highest,
    }
    return render(request, 'auctions/listing_detail.html', context)


@login_required
def toggle_watchlist(request, id):
    listing = get_object_or_404(Listing, id=id)
    if listing in request.user.watchlist.all():
        request.user.watchlist.remove(listing)
    else:
        request.user.watchlist.add(listing)
    return HttpResponseRedirect(reverse('listing_detail', args=[id]))


@login_required
def make_bid(request, listing_id, user_id):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, id=listing_id)
        user = get_object_or_404(User, id=user_id)
        bid_amount = request.POST.get('bid_amount')

        # Check if bid amount is provided
        if bid_amount is None:
            messages.error(request, 'You must enter a bid amount')
            return HttpResponseRedirect(reverse('listing_detail', kwargs={'id': listing_id}))
        else:
            bid_amount = Decimal(bid_amount)

        # Check if bid amount is higher than current price
        if bid_amount > listing.current_price:
            new_bid = Bid(bidder=user, listing=listing,
                          bid_amount=bid_amount)
            new_bid.save()
            return HttpResponseRedirect(reverse('listing_detail', kwargs={'id': listing_id}))
        else:
            messages.error(
                request, 'Your bid must be higher than the current price.')
            return HttpResponseRedirect(reverse('listing_detail', kwargs={'id': listing_id}))
    else:
        return HttpResponseRedirect(reverse('listing_detail', kwargs={'id': listing_id}))
