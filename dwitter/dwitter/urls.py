from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dwitter.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^tweet/(\d+)/$', 'website.views.tweet_page', name='tweet-page'),
    url(r'^user/(\w+)/$', 'website.views.user_page', name='user-page'),
    url(r'^$', 'website.views.timeline', name='timeline'),
)
