from django.db import models

class Media(models.Model):
    ID = models.AutoField(primary_key=True)
    creatorName = models.CharField(max_length=25, default=None)
    creatorID = models.ForeignKey('CreatorInfo', on_delete=models.CASCADE)
    data = models.JSONField()

    class Meta:
        verbose_name = 'Media'
        ordering = ['creatorName', 'ID']

    def __str__(self):
        return self.creatorName

class CreatorInfo(models.Model):
    ID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25, unique=True)
    youtubeID = models.CharField(max_length=50, default=None)
    twitchName = models.CharField(max_length=25, default=None)

    def getLiveStatus(self):
        return CreatorLiveStatus.objects.get(creatorID=self.ID)

    class Meta:
        verbose_name = 'CreatorInfo'

    def __str__(self):
        return self.name

class CreatorLiveStatus(models.Model):
    ID = models.AutoField(primary_key=True)
    creatorID = models.ForeignKey('CreatorInfo', on_delete=models.CASCADE)
    isLiveTwitch = models.BooleanField(default=False)
    isLiveYoutube = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'CreatorLiveStatus'
    
    def __str__(self):
        return self.creatorID.__str__()