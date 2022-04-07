from django import forms 
from django.contrib.auth import get_user_model

from .models import Hotel, Reservation, Comment
 
class HotelAddForm(forms.ModelForm): 
    image = forms.ImageField(widget= forms.FileInput(attrs={'multiple':True,"accept":"image/*", "required":False}))
    
    class Meta:
        model = Hotel 
        fields = ["name", "address","email", "phone", "total_rooms", "room_price", "established", "description", "map_link"]

        help_texts = {
            'map_link': 'copy the embeded link code from google map/ * (optional)',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows':5}),
            'map_link': forms.Textarea(attrs={'rows':8}),
            'established': forms.NumberInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields: 
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class ReservationForm(forms.ModelForm):

    class Meta:
        model = Reservation
        fields = ['no_of_rooms', 'phone']
        labels = {
            'phone': 'Your mobile no.'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()   
        phn = cleaned_data.get('phone')
        no_of_rooms = cleaned_data.get('no_of_rooms')
        if no_of_rooms == 0:
            self.add_error('no_of_rooms', 'No. of rooms should be greater than zero.')
        if phn:
            import re
            if not re.match(r'^98[0-9]{8}$', phn):
                # raise ValidationError('Phone no. must be numeric of length 10.')
                self.add_error('phone', 'Phone no. must be numeric of length 10 and start with 98.')
        return cleaned_data

class ReservationUpdateForm(forms.ModelForm): 
    
    class Meta:
        model = Reservation
        fields = ['no_of_rooms', 'payment_method', 'amount', 'paid', 'checkin_status']
        widgets = {
            'paid': forms.CheckboxInput
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if not(field=='paid'):
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-check-input'})

class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ('content',)