import requests
import json

from isodate import parse_duration

from django.conf import settings
from django.shortcuts import render, redirect
from .models import YouTubeSearchVideoCache,simpleLikeVideo

def index(request):
	videos = []
	context = { 'videos' : videos }
	
	if request.method == 'POST':
		try:
			searchYT = request.POST['search']
		except:
			searchYT =  request.POST.get('searchCurrent')
		
		def favoriteVideos():
			for video in simpleLikeVideo.objects.all():
				video_data = {
				'title' :video.title,
				'id' : video.video_id,
				'url' : f'https://www.youtube.com/watch?v=' + video.video_id,
				'duration' : video.duration,
				'thumbnail' : video.thumbnail }
				
				videos.append(video_data)
				
			context = { 'videos' : videos }
			return render(request, 'search/index.html', context)
		try:
			if request.POST.get('like'):			
				videoLike = request.POST.get('like')
				videoLike = videoLike.replace("'", "\"")
				fVideo = json.loads(videoLike)
				print("User click Like  - " + fVideo['title'])
				fVideoToDB = simpleLikeVideo(title=fVideo['title'],video_id=fVideo['id'],duration=fVideo['duration'],thumbnail=fVideo['thumbnail'])
				
				try:
					tryGetVideo = simpleLikeVideo.objects.get(video_id=fVideo['id'])
				except:
					fVideoToDB.save()
		except:
			pass
			
		try:
			if request.POST.get('dislike'):			
				videoDislike = request.POST.get('dislike')
				videoDislike = videoDislike.replace("'", "\"")
				fVideo = json.loads(videoDislike)
				print("User click Dislike  - " + fVideo['title'])
				
				try:
					fVideoDelFromDB = simpleLikeVideo.objects.get(video_id=fVideo['id'])
					fVideoDelFromDB.delete()
				except:
					pass
		except:
			pass
			
		if request.POST.get('favorite'):
			favoriteVideos()
		
		if not searchYT and not request.POST.get('favorite'):
			favoriteVideos()
			
		if searchYT:
			for video in YouTubeSearchVideoCache.objects.all():
				if video.search == searchYT:
					video_data = {
					'title' :video.title,
					'id' : video.video_id,
					'url' : f'https://www.youtube.com/watch?v=' + video.video_id,
					'duration' : video.duration,
					'thumbnail' : video.thumbnail,
					'searchCurrent' : video.search }
				
					videos.append(video_data)
					
		if (len(videos) != 0 or request.POST.get('favorite')):
			print ("Data work with DB (!)")
		else:
			if not searchYT:
				context = { 'videos' : videos }
				return render(request, 'search/index.html', context)
				
			print ("Data work with YT API (!) ")
			
			search_url = 'https://www.googleapis.com/youtube/v3/search'
			video_url = 'https://www.googleapis.com/youtube/v3/videos'

			search_params = {
				'part' : 'snippet',
				'q' : searchYT,
				'key' : settings.YOUTUBE_DATA_API_KEY,
				'maxResults' : 9,
				'type' : 'video'
			}

			r = requests.get(search_url, params=search_params)
			
			try:
				results = r.json()['items']
			except:
				print("The request cannot be completed!")
				return render(request, 'search/index.html', context)
			
			
			video_ids = []
			for result in results:
				video_ids.append(result['id']['videoId'])

			video_params = {
				'key' : settings.YOUTUBE_DATA_API_KEY,
				'part' : 'snippet,contentDetails',
				'id' : ','.join(video_ids),
				'maxResults' : 9
			}

			r = requests.get(video_url, params=video_params)
			
			try:
				results = r.json()['items']
			except:
				print("The request cannot be completed!")
				return render(request, 'search/index.html', context)
			
			for result in results:
				video_data = {
					'title' : result['snippet']['title'],
					'id' : result['id'],
					'url' : f'https://www.youtube.com/watch?v={ result["id"] }',
					'duration' : int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
					'thumbnail' : result['snippet']['thumbnails']['high']['url'],
					'searchCurrent' : searchYT
				}
				
				videoToDB = YouTubeSearchVideoCache(search = searchYT,title=result['snippet']['title'],video_id=result['id'],duration=int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),thumbnail=result['snippet']['thumbnails']['high']['url'])
				videoToDB.save()
				
				videos.append(video_data)

	context = { 'videos' : videos }
	return render(request, 'search/index.html', context)