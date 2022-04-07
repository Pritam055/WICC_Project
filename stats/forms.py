from urllib import request
from django import forms 
from django.db.models import Min, Max
from django.core.exceptions import ValidationError

from hotels.models import Reservation

class PdfGenForm(forms.Form):

    fromDate = forms.DateField(required=False)
    toDate = forms.DateField(required=False)

    def clean(self):
        cleaned_data = super().clean() 
        user_toDate = cleaned_data.get('toDate')
        user_fromDate = cleaned_data.get('fromDate')

        reservation_obj = Reservation.objects.values('reserved_date__date')
        min_date = reservation_obj.aggregate(Min('reserved_date__date'))['reserved_date__date__min']
        max_date = reservation_obj.aggregate(Max('reserved_date__date'))['reserved_date__date__max']
  
        if user_toDate and user_fromDate:
            if user_fromDate > user_toDate:
                raise ValidationError("'From-date' cannot be greater than 'To-date'")
            
            if user_fromDate: 
                if not(min_date <= user_fromDate <= max_date):
                    raise ValidationError(f"'From-date' is out of range from all reservation dates. (date range in database[{min_date} to {max_date}].")

            if user_toDate: 
                if not(min_date <= user_toDate <= max_date):
                    raise ValidationError(f"'To-date' is out of range from all reservation dates. (date range in database[{min_date} to {max_date}].")
            
        else: 
            if user_fromDate: 
                if not(min_date <= user_fromDate <= max_date):
                    raise ValidationError(f"'From-date' is out of range from all reservation dates. (date range in database[{min_date} to {max_date}].")
                
            if user_toDate: 
                if not(min_date <= user_toDate <= max_date):
                    raise ValidationError(f"'To-date' is out of range from all reservation dates. (date range in database[{min_date} to {max_date}].")
            
            
