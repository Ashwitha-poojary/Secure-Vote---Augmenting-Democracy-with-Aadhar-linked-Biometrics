from django.db import models

# Create your models here.

# constituency
class Constituency(models.Model):
    title=models.CharField(max_length=100)

class Party(models.Model):
    title=models.CharField(max_length=100)

class User(models.Model):
    name=models.CharField(max_length=30)
    email=models.CharField(max_length=30)
    phone=models.CharField(max_length=15)
    aadhar=models.CharField(max_length=20)
    password=models.CharField(max_length=50)
    dob=models.CharField(max_length=30)
    constituency=models.ForeignKey('constituency', on_delete=models.CASCADE)
    status=models.IntegerField()

class Candidate(models.Model):
    name=models.CharField(max_length=30)
    dob=models.CharField(max_length=30)
    constituency=models.ForeignKey('constituency', on_delete=models.CASCADE)
    party=models.ForeignKey('party', on_delete=models.CASCADE)
    image=models.ImageField(upload_to='candidate/')
    status=models.IntegerField()

class VoteInfo(models.Model):
    vote_date=models.CharField(max_length=30)
    result_status=models.IntegerField()

class Vote(models.Model):
    vote_date=models.CharField(max_length=30)
    user=models.ForeignKey('user', on_delete=models.CASCADE)
    candidate=models.ForeignKey('candidate', on_delete=models.CASCADE)
