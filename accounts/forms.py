from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from django.core.exceptions import ValidationError

# from .models import CustomUser
from .models import Certificate

User = get_user_model()

class UserForm(UserCreationForm):

    class Meta:
        model = User 
        fields = ['username', 'email','address', 'phone', 'user_type']

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()  
        phn = cleaned_data.get('phone')
        if phn:
            import re
            if not re.match(r'^98[0-9]{8}$', phn):
                # raise ValidationError('Phone no. must be numeric of length 10.')
                self.add_error('phone', 'Phone no. must be numeric of length 10 and start with 98.')
        return cleaned_data

class UserAuthenticationForm(AuthenticationForm):

    # doing only this way does not work
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class CertificateForm(forms.ModelForm):
    
    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop('request')
    #     super().__init__(*args, **kwargs)
    #     self.fields['user'].initial = self.request.user.username

    class Meta:
        model = Certificate
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'control-form'}), 
        }
        help_texts = {
            'image': 'You can upload only one certificate.'
        }
     
class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'address', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            self.fields[field].required = True

class UserPasswordResetForm(PasswordResetForm):
    
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control'})   
        

class UserSetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})