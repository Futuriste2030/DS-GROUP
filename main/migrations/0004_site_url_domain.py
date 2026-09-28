# Domaine canonique bsgroup.ml.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_hero_video_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='site_url',
            field=models.URLField(default='https://bsgroup.ml'),
        ),
    ]
