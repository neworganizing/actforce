# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CompletedAction'
        db.create_table(u'mover_completedaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action', self.gf('django.db.models.fields.IntegerField')()),
            ('page', self.gf('django.db.models.fields.IntegerField')()),
            ('salesforce_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'mover', ['CompletedAction'])


    def backwards(self, orm):
        # Deleting model 'CompletedAction'
        db.delete_table(u'mover_completedaction')


    models = {
        u'mover.completedaction': {
            'Meta': {'object_name': 'CompletedAction'},
            'action': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.IntegerField', [], {}),
            'salesforce_id': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['mover']