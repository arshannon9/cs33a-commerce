from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from auctions.models import User, Listing, Bid, Comment, Category
from auctions.forms import ListingForm, CommentForm


@login_required
def index(request):
    # Retrieve active listings and display them on index page
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
    # Render page indicating that user has logged out
    logout(request)
    return render(request, "auctions/logged_out.html")


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
    # Handle the creation of a new listing
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            new_listing = form.save(commit=False)
            new_listing.listing_owner = request.user
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
    # Display the details of a listing, including bid and comment forms
    listing = get_object_or_404(Listing, id=id)
    num_bids = Bid.objects.filter(listing=listing).count()
    current_price = Bid.objects.filter(
        listing=listing).order_by('-bid_amount').first()
    is_highest = current_price.bidder == request.user if current_price else False
    form = CommentForm()

    context = {
        'listing': listing,
        'num_bids': num_bids,
        'is_highest': is_highest,
        'form': form,
    }
    return render(request, 'auctions/listing_detail.html', context)


@login_required
def toggle_watchlist(request, id):
    # Add or remove listing from user watchlist
    listing = get_object_or_404(Listing, id=id)
    if listing in request.user.watchlist.all():
        request.user.watchlist.remove(listing)
    else:
        request.user.watchlist.add(listing)
    return HttpResponseRedirect(reverse('listing_detail', args=[id]))


@login_required
def make_bid(request, listing_id, user_id):
    # Allows user to make bid on a listing
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
            # Create and save new Bid object
            new_bid = Bid(bidder=user, listing=listing,
                          bid_amount=bid_amount)
            new_bid.save()
            # Update current price to the highest bid
            highest_bid = Bid.objects.filter(
                listing=listing).order_by('-bid_amount').first()
            listing.current_price = highest_bid.bid_amount if highest_bid else listing.starting_bid
            listing.save()
            return HttpResponseRedirect(reverse('listing_detail', kwargs={'id': listing_id}))
        else:
            messages.error(
                request, 'Your bid must be higher than the current price.')
            return HttpResponseRedirect(reverse('listing_detail', kwargs={'id': listing_id}))
    else:
        return HttpResponseRedirect(reverse('listing_detail', kwargs={'id': listing_id}))


@login_required
def close_auction(request, listing_id):
    # Allows user to close auction only if they own the listing
    if request.method == 'POST':
        listing = get_object_or_404(Listing, id=listing_id)
        user = request.user
        if user == listing.listing_owner:
            listing.is_active = False
            listing.save()
        else:
            messages.error(request, 'You are not the owner of this listing.')
            return HttpResponseRedirect(reverse('listing_detail', kwargs={'id': listing_id}))
        highest_bid = Bid.objects.filter(
            listing=listing).order_by('-bid_amount').first()
        if highest_bid is not None:
            listing.winner = highest_bid.bidder
        listing.save()
        return HttpResponseRedirect(reverse('listing_detail', kwargs={'id': listing_id}))
    else:
        return HttpResponseRedirect(reverse('listing_detail', kwargs={'id': listing_id}))


@login_required
def add_comment(request, listing_id):
    # Adds comment to listing detail page based on user input
    form = CommentForm(request.POST)
    if form.is_valid():
        comment_text = form.cleaned_data.get('comment')
        user = request.user
        listing = Listing.objects.get(pk=listing_id)

        # Create a new Comment object
        Comment.objects.create(
            commenter=user, listing=listing, comment=comment_text)

        return HttpResponseRedirect(reverse('listing_detail', kwargs={'id': listing_id}))
    else:
        return HttpResponseRedirect(reverse('listing_detail', kwargs={'id': listing_id}))


@login_required
def watchlist(request):
    # Retrieve the user's watchlist and display on the watchlist page
    user = request.user
    watchlist_listings = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {"listings": watchlist_listings})


@login_required
def categories(request):
    # Retrieve all categories and display on categories page
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {"categories": categories})


@login_required
def category_view(request, category_name):
    # Get the category object by name or handle error if not found
    category = get_object_or_404(Category, name=category_name)

    # Filter listings based on the selected category and display on category page
    category_listings = Listing.objects.filter(
        category=category)

    context = {
        'category_listings': category_listings,
        'category_name': category_name,
    }
    return render(request, "auctions/category_view.html", context)
