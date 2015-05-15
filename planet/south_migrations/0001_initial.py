# encoding: utf-8
# python 3.x compatibility helpers
from __future__ import unicode_literals

import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Blog'
        db.create_table('planet_blog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200, db_index=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('planet', ['Blog'])

        # Adding model 'Generator'
        db.create_table('planet_generator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
        ))
        db.send_create_signal('planet', ['Generator'])

        # Adding unique constraint on 'Generator', fields ['name', 'link', 'version']
        db.create_unique('planet_generator', ['name', 'link', 'version'])

        # Adding model 'Feed'
        db.create_table('planet_feed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('blog', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planet.Blog'], null=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'], null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, null=True, blank=True)),
            ('subtitle', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('rights', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('generator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planet.Generator'], null=True, blank=True)),
            ('info', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, null=True, blank=True)),
            ('icon_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('image_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('etag', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('last_checked', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
        ))
        db.send_create_signal('planet', ['Feed'])

        # Adding model 'PostAuthorData'
        db.create_table('planet_postauthordata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planet.Post'])),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planet.Author'])),
            ('is_contributor', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_created', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('planet', ['PostAuthorData'])

        # Adding model 'Post'
        db.create_table('planet_post', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planet.Feed'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, db_index=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('comments_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('planet', ['Post'])

        # Adding unique constraint on 'Post', fields ['feed', 'guid']
        db.create_unique('planet_post', ['feed_id', 'guid'])

        # Adding model 'Author'
        db.create_table('planet_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('profile_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('planet', ['Author'])

        # Adding model 'FeedLink'
        db.create_table('planet_feedlink', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planet.Feed'])),
            ('rel', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=500, db_index=True)),
        ))
        db.send_create_signal('planet', ['FeedLink'])

        # Adding model 'PostLink'
        db.create_table('planet_postlink', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planet.Post'])),
            ('rel', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=500, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('planet', ['PostLink'])

        # Adding model 'Enclosure'
        db.create_table('planet_enclosure', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planet.Post'])),
            ('length', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=500, db_index=True)),
        ))
        db.send_create_signal('planet', ['Enclosure'])


    def backwards(self, orm):

        # Removing unique constraint on 'Post', fields ['feed', 'guid']
        db.delete_unique('planet_post', ['feed_id', 'guid'])

        # Removing unique constraint on 'Generator', fields ['name', 'link', 'version']
        db.delete_unique('planet_generator', ['name', 'link', 'version'])

        # Deleting model 'Blog'
        db.delete_table('planet_blog')

        # Deleting model 'Generator'
        db.delete_table('planet_generator')

        # Deleting model 'Feed'
        db.delete_table('planet_feed')

        # Deleting model 'PostAuthorData'
        db.delete_table('planet_postauthordata')

        # Deleting model 'Post'
        db.delete_table('planet_post')

        # Deleting model 'Author'
        db.delete_table('planet_author')

        # Deleting model 'FeedLink'
        db.delete_table('planet_feedlink')

        # Deleting model 'PostLink'
        db.delete_table('planet_postlink')

        # Deleting model 'Enclosure'
        db.delete_table('planet_enclosure')


    models = {
        'planet.author': {
            'Meta': {'ordering': "('name', 'email')", 'object_name': 'Author'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'profile_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'planet.blog': {
            'Meta': {'ordering': "('title', 'url')", 'object_name': 'Blog'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        },
        'planet.enclosure': {
            'Meta': {'ordering': "('post', 'mime_type', 'link')", 'object_name': 'Enclosure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '500', 'db_index': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planet.Post']"})
        },
        'planet.feed': {
            'Meta': {'ordering': "('title', 'url')", 'object_name': 'Feed'},
            'blog': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planet.Blog']", 'null': 'True', 'blank': 'True'}),
            'etag': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planet.Generator']", 'null': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'icon_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'info': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'last_checked': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'rights': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']", 'null': 'True', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        },
        'planet.feedlink': {
            'Meta': {'ordering': "('feed', 'rel', 'mime_type')", 'object_name': 'FeedLink'},
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planet.Feed']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '500', 'db_index': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'rel': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'planet.generator': {
            'Meta': {'ordering': "('name', 'version')", 'unique_together': "(('name', 'link', 'version'),)", 'object_name': 'Generator'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        'planet.post': {
            'Meta': {'ordering': "('-date_modified',)", 'unique_together': "(('feed', 'guid'),)", 'object_name': 'Post'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['planet.Author']", 'through': "orm['planet.PostAuthorData']", 'symmetrical': 'False'}),
            'comments_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planet.Feed']"}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'planet.postauthordata': {
            'Meta': {'ordering': "('author', 'post', 'is_contributor')", 'object_name': 'PostAuthorData'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planet.Author']"}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_contributor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planet.Post']"})
        },
        'planet.postlink': {
            'Meta': {'ordering': "('post', 'title', 'rel')", 'object_name': 'PostLink'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '500', 'db_index': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['planet.Post']"}),
            'rel': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['planet']
