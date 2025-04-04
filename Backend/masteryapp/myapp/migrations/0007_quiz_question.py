# Generated by Django 5.1.7 on 2025-03-22 17:06

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_rename_subcategory_materialsnippet_subject_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=1000)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('optimize_learning', models.BooleanField(default=True)),
                ('quiz_length', models.SmallIntegerField(default=20)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizzes', to='myapp.course')),
                ('materials', models.ManyToManyField(blank=True, to='myapp.materialsnippet')),
                ('subjects', models.ManyToManyField(blank=True, to='myapp.subject')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question', models.TextField()),
                ('type', models.CharField(choices=[('SHORT_ANSWER', 'Short answer'), ('MULTIPLE_ANSWER', 'Multiple answer'), ('MULTIPLE_CHOICE', 'Multiple choice')], max_length=25)),
                ('choices', models.TextField()),
                ('correct_choices', models.CharField(max_length=100, null=True)),
                ('correct_short_answer', models.TextField()),
                ('attempted_choices', models.CharField(max_length=100, null=True)),
                ('attempted_short_answer', models.TextField(null=True)),
                ('is_correct', models.BooleanField(null=True)),
                ('snippet', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.subject')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.quiz')),
            ],
        ),
    ]
