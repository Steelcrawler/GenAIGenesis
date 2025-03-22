# Generated by Django 5.1.7 on 2025-03-22 06:15

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_delete_semester_classmaterial_file_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='myapp.course')),
            ],
        ),
        migrations.CreateModel(
            name='MaterialCut',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('cut_start', models.PositiveIntegerField()),
                ('cut_end', models.PositiveIntegerField()),
                ('class_material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.classmaterial')),
                ('subcategory', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.subcategory')),
            ],
        ),
    ]
