from django.shortcuts import render
from django.http import HttpResponseRedirect

from .models import Media, CreatorInfo, CreatorLiveStatus
from .forms import creatorForm
from scraperAPI.tasks import connectAndCreate, isOnlineTwitch, isOnlineYT

def baseMedia(request):
    medias = reversed(Media.objects.all())
    context = {'media': medias}
    return render(request,'base.html', context)

def viewCreators(request):
    if request.method == 'POST':
        form = creatorForm(request.POST)
        if form.is_valid():
            if form.data['option'] == 'delete': deleteCreator(form)
            else: checkCreateOrUpdate(form)
            return HttpResponseRedirect('/creators/')
    else:
        form = creatorForm()
        creators = CreatorInfo.objects.all()
        return render(request, 'viewCreator.html', {'creators': creators, 'form': form})

def checkCreateOrUpdate(form):
    urlID = form.data['urlYT'].rpartition('/')[2]
    if (len(urlID) == 24):
        if form.data['option'] == 'create': newCreator(form, urlID) #create
    else: updateCreator(form, urlID) #update

def newCreator(form, urlID):
    if CreatorInfo.objects.filter(name = form.data['name']).exists():  return           #check if exists

    newCreator = CreatorInfo.objects.create (
        name = form.data['name'],
        youtubeID = urlID,
        twitchName = form.data['twitchUser']
    )
    createLiveStatus(newCreator)
    connectAndCreate.delay(urlID)           #populate media via task

#change url
def updateCreator(form, urlID):
    creatorInfo = CreatorInfo.objects.filter(name = form.data['name']).first()
    if creatorInfo is None: return
    if form.data['urlYT'] is not "": 
        creatorInfo.youtubeID = urlID
        media = Media.objects.filter(creatorID = creatorInfo.ID).delete()           #delete old media
        connectAndCreate.delay(urlID)                                               #populate media via task
    if form.data['twitchUser'] is not "": 
        creatorInfo.twitchName = form.data['twitchUser']
    createLiveStatus(creatorInfo)
    creatorInfo.save()


#delete creator and all media which has same name
def deleteCreator(form):
    creatorInfo = CreatorInfo.objects.filter(name = form.data['name']).first()
    if creatorInfo is None: return

    Media.objects.filter(creatorID = creatorInfo.ID).delete()
    CreatorLiveStatus.objects.filter(creatorID = creatorInfo.ID).delete()
    creatorInfo.delete()

def createLiveStatus(creator):
    newLiveStatus = CreatorLiveStatus.objects.create (
        creatorID = creator,
        isLiveTwitch = isOnlineTwitch(creator.twitchName),
        isLiveYoutube = isOnlineYT(creator.youtubeID)
    )