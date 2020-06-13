from django.db import models

class YouTubeSearchVideoCache(models.Model):
	search = models.TextField('поисковой запрос')
	title = models.TextField('название')
	video_id = models.TextField('айди')
	duration = models.TextField('время')
	thumbnail = models.TextField('картинка')
	
	def __str__(self):
		return self.title
	
class simpleLikeVideo(models.Model):
	title = models.TextField('название')
	video_id = models.TextField('айди')
	duration = models.TextField('время')
	thumbnail = models.TextField('картинка')
	
	def __str__(self):
		return self.title