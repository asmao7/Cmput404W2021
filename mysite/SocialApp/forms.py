from django import forms
from .models import Post, Comment

#TODO data validation for form data 
class SignUpForm(forms.Form):

    fistName = forms.CharField(label='First Name', max_length=1000, required=True, widget=forms.TextInput(
        attrs={
            # 'class': 'form-control',
            'placeholder': 'First Name'
        }))
    lastName = forms.CharField(label='Last Name', max_length=1000, required=True,widget=forms.TextInput(
        attrs={
            # 'class': 'form-control',
            'placeholder': 'Last Name'
        }))
    displayName = forms.CharField(label='Display Name', max_length=1000, required=True, widget=forms.TextInput(
        attrs={
            # 'class': 'form-control',
            'placeholder': 'User Name'
        }))
    Email = forms.EmailField(label='Email', max_length=100, required=True, widget=forms.EmailInput(
        attrs={
            # 'class': 'form-control',
            'placeholder': 'Email Address'
        }))
    GithubUrl = forms.URLField(label='Github URL', max_length=3000,required=False, widget=forms.TextInput(
        attrs={
            # 'class': 'form-control',
            'placeholder': 'Enter your github url'
        }))
    Password = forms.CharField(label='Password',max_length=32, widget=forms.PasswordInput)
    Confirm_Password = forms.CharField(label='Confirm Password',max_length=32, widget=forms.PasswordInput)


class LoginForm(forms.Form):
    UserName = forms.CharField(label='UserName', max_length=1000, required=True, widget=forms.TextInput)
    Password = forms.CharField(label='Password', max_length=32, required=True, widget=forms.PasswordInput)


# to customize the form when adding new post
# user is hidden, will know the auhtor of the post
# by getting the auhtor whose logged in
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'author', 'content', 'unlisted', 'visibility']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            #'author': forms.Select(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'value':'', 'id':'uniqueid', 'type':'hidden'}),
            'content_type': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'visibility': forms.Select(attrs={'class': 'form-control'}),
        }

# for customizing the form when adding comments
# user is hidden, will know the auhtor of the comment
# we have to hide the post, should which post owns the comments ~ not working for now!
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['post', 'comment', 'author']
        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-control', 'value':'', 'id':'uniqueid', 'type':'hidden'}),
            'post': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }