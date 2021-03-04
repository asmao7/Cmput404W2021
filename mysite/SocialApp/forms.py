from django import forms

#TODO data validation for form data 
class SignUpForm(forms.Form):

    Fist_Name = forms.CharField(max_length=1000, required=True, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        }))
    Last_Name = forms.CharField(max_length=1000, required=True,widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        }))
    display_name = forms.CharField(max_length=1000, required=True, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'User Name'
        }))
    Email = forms.EmailField(max_length=100, required=True, widget=forms.EmailInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        }))
    GithubUrl = forms.URLField(max_length=3000,required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter your github url'
        })))
    Password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    Confirm_Password = fforms.CharField(max_length=32, widget=forms.PasswordInput)


class LoginForm(forms.Form):
    user_name = forms.CharField(max_length=1000, required=True)
    Password = forms.CharField(max_length=32, widget=forms.PasswordInput)