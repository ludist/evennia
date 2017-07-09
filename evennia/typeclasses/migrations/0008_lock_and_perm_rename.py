# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-01-25 22:30
from __future__ import unicode_literals

import re
from django.db import migrations

def update_perms_and_locks(apps, schema_editor):

    # update all permissions
    Tag = apps.get_model('typeclasses', 'Tag')
    perm_map = {"guests": "guest", "accounts": "account", "accounthelpers":"helper",
                "builders": "builder", "wizards":"admin", "immortals": "developer"}

    for perm in Tag.objects.filter(db_tagtype="permission"):
        if perm.db_key in perm_map:
            perm.db_key = perm_map[perm.db_key]
            perm.save(update_fields=("db_key",))

    # update all locks on all entities
    apps_models = [("objects", "ObjectDB"), ("accounts", "AccountDB"), ("scripts", "ScriptDB"),
                   ("comms", "ChannelDB")]
    p_reg = re.compile(r"(?<=perm\()(\w+)(?=\))|(?<=perm_above\()(\w+)(?=\))",
                        re.IGNORECASE + re.UNICODE)
    def _sub(match):
        perm = match.group(1)
        return perm_map[perm.lower()].capitalize() if perm.lower() in perm_map else perm

    for app_tuple in apps_models:
        TClass = apps.get_model(*app_tuple)
        for obj in TClass.objects.filter(db_lock_storage__icontains="perm"):
            orig_lock = obj.db_lock_storage
            repl_lock = p_reg.sub(_sub, orig_lock)
            if repl_lock != orig_lock:
                obj.db_lock_storage = repl_lock
                obj.save(update_fields=('db_lock_storage',))

class Migration(migrations.Migration):

    dependencies = [
        ('typeclasses', '0007_tag_migrations_may_be_slow'),
    ]

    operations = [

        migrations.RunPython(update_perms_and_locks)
    ]
