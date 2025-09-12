from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid

AGE_GROUPS = [
    ('Under 18','Under 18'),('18-24','18-24'),('25-34','25-34'),('35-44','35-44'),('45-54','45-54'),('55-64','55-64'),('65+','65+'),
]

LOCATION = [('Home','Home'),('Gym','Gym'),('Outdoor','Outdoor')]
SPACE = [('Small','Small'),('Medium','Medium'),('Large','Large')]
IMPACT = [('Low','Low'),('Moderate','Moderate'),('High','High')]

GOALS = [
    ('Fat Loss','Fat Loss'),('Strength','Strength'),('Hypertrophy','Hypertrophy'),
    ('Conditioning','Conditioning'),('Mobility','Mobility'),('Power','Power'),('Rehab','Rehab'),
]
RPE_FAMILIARITY = [('New','New'),('Some','Some'),('Comfortable','Comfortable')]

class TimeStampedUUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Client(TimeStampedUUIDModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='clients', null=True, blank=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    preferred_name = models.CharField(max_length=80, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)

    age_group = models.CharField(max_length=16, choices=AGE_GROUPS)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    training_age_years = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    trains_with_me = models.BooleanField(default=False)
    primary_location = models.CharField(max_length=16, choices=LOCATION, default='Gym')
    gym_name = models.CharField(max_length=120, blank=True)
    space_available = models.CharField(max_length=8, choices=SPACE, default='Small')
    impact_tolerance = models.CharField(max_length=9, choices=IMPACT, default='Low')
    session_length_min = models.IntegerField(default=60)
    days_per_week = models.IntegerField(default=3)
    preferred_days = models.JSONField(default=list, blank=True)   # e.g., ["Mon","Wed","Fri"]


    



    goals = models.JSONField(default=list)                        # e.g., ["Strength","Hypertrophy"]

    sport_focus = models.CharField(max_length=80, blank=True)

    knee_issue = models.BooleanField(default=False)
    shoulder_issue = models.BooleanField(default=False)
    back_issue = models.BooleanField(default=False)
    injury_notes = models.TextField(blank=True)

    rpe_familiarity = models.CharField(max_length=16, choices=RPE_FAMILIARITY, blank=True)
    power_interest = models.BooleanField(default=False)

    likes_notes = models.TextField(blank=True)
    dislikes_notes = models.TextField(blank=True)

    def __str__(self):
        return self.preferred_name or f"{self.first_name} {self.last_name}"

class ClientInjury(TimeStampedUUIDModel):
    REGION = [(r,r) for r in ['Knee','Shoulder','Back','Hip','Ankle','Wrist','Neck','Elbow','Other']]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='injuries')
    region = models.CharField(max_length=16, choices=REGION)
    description = models.TextField(blank=True)
    severity = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)

class ClientPreference(TimeStampedUUIDModel):
    KIND = [('Exercise','Exercise'),('Movement Pattern','Movement Pattern')]
    SENTIMENT = [('Like','Like'),('Dislike','Dislike'),('Hard No','Hard No')]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='preferences')
    kind = models.CharField(max_length=20, choices=KIND)
    value = models.CharField(max_length=160)
    sentiment = models.CharField(max_length=16, choices=SENTIMENT)

class ClientEquipment(TimeStampedUUIDModel):
    LOCATION = [('Home','Home'),('Gym','Gym')]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='equipment')
    location = models.CharField(max_length=8, choices=LOCATION)
    category = models.CharField(max_length=40)  # align with your taxonomy
    details = models.JSONField(default=dict, blank=True)

class ClientProfile(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    profile = models.JSONField()  # normalized, generator-ready
    updated_at = models.DateTimeField(default=timezone.now)


class ClientBlock(TimeStampedUUIDModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='blocks')
    name = models.CharField(max_length=160, blank=True)
    block = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name or f"Block {self.id}"
