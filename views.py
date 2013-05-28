#-*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Q
from shelf.forms import ArticleForm, SearchForm, EditArticleForm, SelectEditArticleForm
from shelf.models import Article, Duration, KeepAllArticlesFilter, OverdueArticlesFilter, AlreadyReadArticlesFilter, ArticleFilters
import datetime
import math

def addArticle(request):
	if request.method == 'POST':
		form = ArticleForm(request.POST)

		if form.is_valid():
			title = form.cleaned_data['title']
			url = form.cleaned_data['url']
			duration = form.cleaned_data['duration']
			
			article = Article(title=title, url=url)
			if duration is not None:
				article.endDate = duration.getEndDate()
			article.save()
			messages.success(request, u'The article has been added.')

			form = ArticleForm
	else:
		form = ArticleForm

	return render(request, 'addArticle.html', locals())

def home(request):
	print request.method	
	if request.method == 'POST':
		if 'delete' in request.POST:
			delete_article(request)
		elif 'read' in request.POST:
			read_article(request)

	today = datetime.date.today()
	todayArticles = Article.objects.filter(endDate=today, hasBeenRead=False).order_by('title')
	additionalArticles = Article.objects.filter(endDate__gt=today, hasBeenRead=False).order_by('endDate','title')[:5]
	return render(request, 'home.html', locals())

def search(request):	
	page_size = 2

	if request.method == 'GET':		
		form = SearchForm(initial={'paging': 0})
	else:
		form = SearchForm(request.POST)
		if form.is_valid():
			page = int(form.cleaned_data['paging'])
						
			if 'delete' in request.POST:
				delete_article(request)
			elif 'read' in request.POST:
				read_article(request)
			elif 'next' in request.POST:
				page += 1				
			elif 'previous' in request.POST:
				page -= 1	

			url_title = form.cleaned_data['urlTitle']
			filter_id = int(form.cleaned_data['filter'])

			page, nb_pages, articles, nb_articles = search_articles(page, page_size, url_title, filter_id)

			postValues = request.POST.copy()
			postValues['paging'] = page
			form = SearchForm(postValues)

		else:
			return HttpResponseBadRequest('<h4>Bad request</h4>')
			
	return render(request, 'search.html', locals())

def delete_article(request):
	id = request.POST['delete']	
	article = get_object_or_404(Article, id=id)
	article.delete()

def read_article(request):
	id = request.POST['read']	
	article = get_object_or_404(Article, id=id)
	article.hasBeenRead = True;
	article.save()

def search_articles(page, page_size, url_title, filter_id):
	articles = ArticleFilters.Filters[filter_id].get_articles()
	if len(url_title.strip()) > 0:
		articles = articles.filter(Q(url__contains=url_title) | Q(title__contains=url_title))

	nb_articles = articles.count()
	nb_pages = int(math.ceil(float(nb_articles) / page_size))

	# in case another filter is applied and less records are returned
	if page < 0 or page > nb_pages:
		page = 0

	start_index = page * page_size
	end_index = (page + 1) * page_size
	articles = articles.order_by('endDate', 'title')[start_index:end_index]
	return page, nb_pages, articles, nb_articles

def select_edit_article(request, article_id=None):
	if request.method == 'GET':
		if article_id is not None:
			article = get_object_or_404(Article, id=article_id)		
			form = SelectEditArticleForm(initial = {'articles': article_id})
		else:
			form = SelectEditArticleForm()
	elif request.method == 'POST' and request.is_ajax():
		form = SelectEditArticleForm(request.POST)
		if form.is_valid():
			articles = form.cleaned_data['articles']
			try:
				article = Article.objects.get(id=articles.id)	
				form = EditArticleForm(instance = article)
				postValues = request.POST.copy()
				postValues['id'] = articles.id
				return render(request, 'editArticle.html', locals())
			except Article.DoesNotExist:
				form = EditArticleForm()
			return render(request, 'editArticle.html', locals())
		else:
			return HttpResponse()
	else:
		form = SelectEditArticleForm()
	return render(request, 'selectEditArticle.html', locals())

def edit_article(request):
	if request.method == 'POST' and request.is_ajax():
		form = EditArticleForm(request.POST)	
		if form.is_valid():
			article_id = form.cleaned_data['id']
			article = get_object_or_404(Article, id = article_id) # todo raise exception
			article.title = form.cleaned_data['title']
			article.url = form.cleaned_data['url']
			article.hasBeenRead = form.cleaned_data['hasBeenRead']
			article.endDate = form.cleaned_data['endDate']						
			article.save()
			messages.success(request, u'The article has been updated.')
		else:
			print 'not cleaned'
		return render(request, 'editArticle.html', locals())
	else:
		form = SelectEditArticleForm()
		return render(request, 'selectEditArticle.html', locals())

