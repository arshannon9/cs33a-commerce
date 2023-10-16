from django import forms
from django.forms import ModelForm

from auctions.models import Listing, Comment


# Form handling the creation of a listing
class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image', 'category']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if not image.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raise forms.ValidationError('Invalid image URL')
        else:
            image = 'https://img.icons8.com/ios/100/no-image.png'
        return image


# Form handling the input of a new comment
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
