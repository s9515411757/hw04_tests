from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control', 'name': 'text', 'cols': '40',
                'rows': '10', 'required id': 'id_text'}
            ),
            'group': forms.Select(attrs={
                'name': 'group', 'class': 'form-control', 'id': 'id_group'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст',
        }
        help_texts = {
            'text': 'Текст нового комментария',
        }
