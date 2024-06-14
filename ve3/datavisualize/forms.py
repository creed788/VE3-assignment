from django import forms


class UploadCSVForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={
        'class': 'form-control',
        'id': 'customFile',
    }))



'''
class Plots(forms.Form):

    def set_column_choices(self):
        x = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
        y = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
        include_scatter = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Include Scatter Plot'
    )
        include_histogram = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Include Histogram'
    )
        include_box = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Include Box Plot'
    )    
    def __init__(self, *args, **kwargs):
        column_choices = kwargs.pop('column_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['x'].choices = column_choices
        self.fields['y'].choices = column_choices
'''