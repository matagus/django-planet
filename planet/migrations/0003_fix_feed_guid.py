import hashlib

from django.db import migrations


def recompute_feed_guids(apps, schema_editor):
    Feed = apps.get_model("planet", "Feed")

    for feed in Feed.objects.all():
        feed.guid = hashlib.md5(feed.url.encode("utf-8")).hexdigest()
        feed.save(update_fields=["guid"])


class Migration(migrations.Migration):

    dependencies = [
        ("planet", "0002_post_original_content"),
    ]

    operations = [
        migrations.RunPython(recompute_feed_guids, migrations.RunPython.noop),
    ]
