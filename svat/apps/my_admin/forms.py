from django import forms
from apps.my_admin.models import ArticleLanguage, ProductLanguage

class ArticleForm(forms.ModelForm):
    class Meta:
        model = ArticleLanguage
        fields = ('content', )
        labels = {
            "content": ""
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductLanguage
        fields = ('des', )
        labels = {
            "des": ""
        }
