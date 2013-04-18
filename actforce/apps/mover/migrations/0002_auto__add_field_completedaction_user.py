# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CompletedAction.user'
        db.add_column(u'mover_completedaction', 'user',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CompletedAction.user'
        db.delete_column(u'mover_completedaction', 'user')


    models = {
        u'mover.completedaction': {
            'Meta': {'object_name': 'CompletedAction'},
            'action': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.IntegerField', [], {}),
            'salesforce_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['mover']