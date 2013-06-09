#-*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Q
from shelf.forms import ArticleForm, SearchForm, EditArticleForm, SelectEditArticleForm
from shelf.models import Article, Duration, KeepAllArticlesFilter, OverdueArticlesFilter, AlreadyReadArticlesFilter, ArticleFilters
from datetime import date, timedelta
import math

def home(request):
	if request.method == 'POST':
		if 'delete' in request.POST:
			delete_article(request.POST['delete'])
		elif 'read' in request.POST:
			read_article(request.POST['read'])

	today = date.today()
	number_overrdue_articles = Article.objects.filter(endDate__lt=today, hasBeenRead=False).count()
	articles = Article.objects\
		.filter(endDate__gte=today, hasBeenRead=False)\
		.extra(select={'lower_title':'lower(title)'})\
		.order_by('endDate', 'lower_title')[:10]
	return render(request, 'home.html', locals())

def search(request, filter_name=None):	
	page_size = 20

	if request.method == 'GET':				
		filter_id = ArticleFilters.get_filter_id(filter_name)
		if filter_name is not None:
			page, nb_pages, articles, nb_articles = search_articles(0, page_size, None, filter_id)

			postValues = request.POST.copy()
			postValues['paging'] = page
			postValues['filter'] = filter_id
			form = SearchForm(postValues)
		else:
			form = SearchForm(initial={'paging': 0, 'filter': filter_id})
	else:
		form = SearchForm(request.POST)
		if form.is_valid():
			page = int(form.cleaned_data['paging'])
						
			if 'delete' in request.POST:
				delete_article(request.POST['delete'])
			elif 'read' in request.POST:
				read_article(request.POST['read'])
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

def delete_article(article_id):
	Article.objects.filter(id=article_id).delete()

def read_article(article_id):
	Article.objects.filter(id=article_id).update(hasBeenRead=True)	

def search_articles(page, page_size, url_title, filter_id):
	articles = ArticleFilters.get_filter(filter_id).get_articles()
	articles = articles.extra(select={'lower_title':'lower(title)'})
	if url_title is not None and len(url_title.strip()) > 0:
		articles = articles.filter(Q(url__icontains=url_title) | Q(title__icontains=url_title))

	nb_articles = articles.count()
	nb_pages = int(math.ceil(float(nb_articles) / page_size))

	# in case another filter is applied and less records are returned
	if page < 0 or page > nb_pages:
		page = 0

	start_index = page * page_size
	end_index = (page + 1) * page_size
	articles = articles.order_by('endDate', 'lower_title')[start_index:end_index]
	return page, nb_pages, articles, nb_articles

def addArticle(request):
	if request.method == 'POST':
		form = ArticleForm(request.POST)

		if form.is_valid():
			article = form.save(commit=False)
			duration = form.cleaned_data['duration']
			if duration is not None:
				article.endDate = duration.getEndDate()
			article.save()

			messages.success(request, u'The article has been added.')
			form = ArticleForm
	else:
		form = ArticleForm

	return render(request, 'addArticle.html', locals())

def edit_article(request, article_id):
	article = get_object_or_404(Article, id=article_id)		
	if request.method == 'GET':
		form = EditArticleForm(instance = article)
	elif request.method == 'POST':
		form = EditArticleForm(request.POST, instance=article)
		if form.is_valid():
			form.save()
			postValues = request.POST.copy()
			postValues['id'] = article_id
			messages.success(request, u'The article has been updated.')
	print article.creationDate 
	readOnlyFields = { 'Creation Date': article.creationDate }
	return render(request, 'editArticle.html', locals())

