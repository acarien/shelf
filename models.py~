from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta

# Duration
class Duration(models.Model):
	name = models.CharField(max_length=100)
	numberDays = models.PositiveIntegerField(null=True, blank=True)
	date = models.DateField(null=True, blank=True)

	def getEndDate(self):
		today = date.today()
		if self.numberDays is None:
			if self.date is None:
				return null # todo exception
			else:
				return date(today.year, self.date.month, self.date.day)	
		else:
			return today + timedelta(self.numberDays);
			
	def __unicode__(self):
		return self.name

# Article
class Article(models.Model):
	title = models.CharField(max_length=200)
	url = models.URLField(max_length=200)
	creationDate = models.DateTimeField(auto_now_add=True, auto_now=False, editable=False)
	endDate = models.DateField(null=True)
	hasBeenRead = models.BooleanField(default=False)
	#user = models.ForeignKey(User, editable=False)

	def __unicode__(self):
		return self.title

class KeepAllArticlesFilter:	
	def get_articles(self):
		return Article.objects.all()
	
	def __str__(self):
		return 'All'

class OverdueArticlesFilter:
	def get_articles(self):
		return Article.objects.filter(endDate__lt=date.today(), hasBeenRead=False)

	def __str__(self):
		return 'Overdue'

class ArticlesDueTomorrowFilter:
	def get_articles(self):
		tomorrow = date.today() + timedelta(days=1)
		return Article.objects.filter(endDate__lte=tomorrow, hasBeenRead=False)

	def __str__(self):
		return 'Due tomorrow'

class ArticlesDueTenDaysFilter:
	def get_articles(self):
		days = date.today() + timedelta(days=10)
		return Article.objects.filter(endDate__lte=days, hasBeenRead=False)

	def __str__(self):
		return 'Due in 10 days'

class ArticlesDueFilter:
	def get_articles(self):
		return Article.objects.filter(endDate__isnull=False, hasBeenRead=False)

	def __str__(self):
		return 'With deadline'

class AlreadyReadArticlesFilter:
	def get_articles(self):		
		return Article.objects.filter(hasBeenRead=True)

	def __str__(self):
		return 'Already read'

class ArticleFilters:
		Filters = {
			1:KeepAllArticlesFilter(),
			2:ArticlesDueFilter(),
			3:OverdueArticlesFilter(),
			4:ArticlesDueTomorrowFilter(),
			5:ArticlesDueTenDaysFilter(),
			6:AlreadyReadArticlesFilter(),
		}	
