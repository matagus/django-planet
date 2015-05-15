# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Name', blank=True)),
                ('email', models.EmailField(db_index=True, max_length=75, verbose_name='Author email', blank=True)),
                ('profile_url', models.URLField(null=True, verbose_name='Profile URL', blank=True)),
            ],
            options={
                'ordering': ('name', 'email'),
                'verbose_name': 'Author',
                'verbose_name_plural': 'Authors',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(db_index=True, max_length=255, verbose_name='title', blank=True)),
                ('url', models.URLField(unique=True, verbose_name='Url', db_index=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('owner', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('title', 'url'),
                'verbose_name': 'Blog',
                'verbose_name_plural': 'Blogs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=100, verbose_name='Category Title')),
                ('date_created', models.DateField(auto_now_add=True, verbose_name='Date created')),
            ],
            options={
                'ordering': ('title', 'date_created'),
                'verbose_name': 'Feed Category',
                'verbose_name_plural': 'Feed Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Enclosure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('length', models.CharField(max_length=20, verbose_name='Length')),
                ('mime_type', models.CharField(max_length=50, verbose_name='MIME type', db_index=True)),
                ('link', models.URLField(max_length=500, verbose_name='Url', db_index=True)),
            ],
            options={
                'ordering': ('post', 'mime_type', 'link'),
                'verbose_name': 'Post Enclosure',
                'verbose_name_plural': 'Post Enclosures',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(unique=True, verbose_name='Url', db_index=True)),
                ('title', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Title', blank=True)),
                ('subtitle', models.TextField(null=True, verbose_name='Subtitle', blank=True)),
                ('rights', models.CharField(max_length=255, null=True, verbose_name='Rights', blank=True)),
                ('info', models.CharField(max_length=255, null=True, verbose_name='Infos', blank=True)),
                ('language', models.CharField(max_length=50, null=True, verbose_name='Language', blank=True)),
                ('guid', models.CharField(db_index=True, max_length=32, null=True, verbose_name='Global Unique Identifier', blank=True)),
                ('icon_url', models.URLField(null=True, verbose_name='Icon URL', blank=True)),
                ('image_url', models.URLField(null=True, verbose_name='Image URL', blank=True)),
                ('etag', models.CharField(db_index=True, max_length=50, null=True, verbose_name='Etag', blank=True)),
                ('last_modified', models.DateTimeField(db_index=True, null=True, verbose_name='Last modified', blank=True)),
                ('last_checked', models.DateTimeField(null=True, verbose_name='Last checked', blank=True)),
                ('is_active', models.BooleanField(default=True, help_text='If disabled, this feed will not be further updated.', db_index=True, verbose_name='Is active')),
                ('blog', models.ForeignKey(blank=True, to='planet.Blog', null=True)),
                ('category', models.ForeignKey(blank=True, to='planet.Category', null=True)),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Feed',
                'verbose_name_plural': 'Feeds',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeedLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rel', models.CharField(max_length=50, verbose_name='Relation', db_index=True)),
                ('mime_type', models.CharField(max_length=50, verbose_name='MIME type', db_index=True)),
                ('link', models.URLField(max_length=500, verbose_name='Url', db_index=True)),
                ('feed', models.ForeignKey(to='planet.Feed')),
            ],
            options={
                'ordering': ('feed', 'rel', 'mime_type'),
                'verbose_name': 'Feed Link',
                'verbose_name_plural': 'Feed Links',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Generator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('link', models.URLField(null=True, verbose_name='Url', blank=True)),
                ('version', models.CharField(max_length=200, null=True, verbose_name='Version', blank=True)),
            ],
            options={
                'ordering': ('name', 'version'),
                'verbose_name': 'Generator',
                'verbose_name_plural': 'Generators',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='Title', db_index=True)),
                ('url', models.URLField(max_length=1000, verbose_name='Url', db_index=True)),
                ('guid', models.CharField(max_length=32, verbose_name='Guid', db_index=True)),
                ('content', models.TextField(verbose_name='Content')),
                ('comments_url', models.URLField(null=True, verbose_name='Comments URL', blank=True)),
                ('date_modified', models.DateTimeField(db_index=True, null=True, verbose_name='Date modified', blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
            ],
            options={
                'ordering': ('-date_created', '-date_modified'),
                'verbose_name': 'Post',
                'verbose_name_plural': 'Posts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PostAuthorData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_contributor', models.BooleanField(default=False, verbose_name='Is Contributor?')),
                ('date_created', models.DateField(auto_now_add=True, verbose_name='Date created')),
                ('author', models.ForeignKey(to='planet.Author')),
                ('post', models.ForeignKey(to='planet.Post')),
            ],
            options={
                'ordering': ('author', 'post', 'is_contributor'),
                'verbose_name': 'Post Author Data',
                'verbose_name_plural': 'Post Author Data',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PostLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rel', models.CharField(max_length=50, verbose_name='Relation', db_index=True)),
                ('mime_type', models.CharField(max_length=50, verbose_name='MIME type', db_index=True)),
                ('link', models.URLField(max_length=500, verbose_name='Url', db_index=True)),
                ('title', models.CharField(max_length=255, verbose_name='Title', db_index=True)),
                ('post', models.ForeignKey(to='planet.Post')),
            ],
            options={
                'ordering': ('post', 'title', 'rel'),
                'verbose_name': 'Post Link',
                'verbose_name_plural': 'Post Links',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='post',
            name='authors',
            field=models.ManyToManyField(to='planet.Author', through='planet.PostAuthorData'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='feed',
            field=models.ForeignKey(to='planet.Feed'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='post',
            unique_together=set([('feed', 'guid')]),
        ),
        migrations.AlterUniqueTogether(
            name='generator',
            unique_together=set([('name', 'link', 'version')]),
        ),
        migrations.AddField(
            model_name='feed',
            name='generator',
            field=models.ForeignKey(blank=True, to='planet.Generator', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='feed',
            name='site',
            field=models.ForeignKey(blank=True, to='sites.Site', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='enclosure',
            name='post',
            field=models.ForeignKey(to='planet.Post'),
            preserve_default=True,
        ),
    ]
