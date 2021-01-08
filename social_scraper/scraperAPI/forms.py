from django import forms

class creatorForm(forms.Form):
    option = forms.ChoiceField(label='Option', required=True, choices=(('create', 'create'), ('update', 'update'), ('delete', 'delete')))
    name = forms.CharField(label='Name', max_length=40, required=True)
    urlYT = forms.CharField(label='YouTube URL', max_length=60, required=False) 
    twitchUser = forms.CharField(label='Twitch Name', max_length=25, required=False)  
