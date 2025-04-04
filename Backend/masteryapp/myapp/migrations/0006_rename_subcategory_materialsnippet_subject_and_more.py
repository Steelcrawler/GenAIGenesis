# Generated by Django 5.1.7 on 2025-03-22 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_remove_subcategory_course_subject_materialsnippet_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='materialsnippet',
            old_name='subcategory',
            new_name='subject',
        ),
        migrations.AddField(
            model_name='classmaterial',
            name='custom_name',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='classmaterial',
            name='file_name',
            field=models.CharField(max_length=1000),
        ),
    ]
