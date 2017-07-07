from __future__ import unicode_literals

from django.db import models


# Used for registering users for a conference
class ConferenceRegistration(models.Model):
    # Required entries: name, email, sessions
    name = models.CharField(max_length=250, blank=True)
    organization = models.CharField(max_length=250, blank=True)
    email = models.EmailField(max_length=250, blank=True)
    sessions = models.TextField(blank=False)
    foodinfo = models.CharField(max_length=250, blank=True)
    accommodations = models.CharField(max_length=250, blank=True)
    code = models.CharField(max_length=250)


class MortgageBase(models.Model):
    """An abstract model base for County and MSA mortgage records."""
    fips = models.CharField(max_length=6, blank=True, db_index=True)
    date = models.DateField(blank=True, db_index=True)
    total = models.IntegerField(null=True)
    current = models.IntegerField(null=True)
    thirty = models.IntegerField(null=True)
    sixty = models.IntegerField(null=True)
    ninety = models.IntegerField(null=True)
    other = models.IntegerField(null=True)

    class Meta:
        abstract = True
        ordering = ['date']

    @property
    def time_series(self):
        # return [self.epoch, self.percent_30_60]
        return {'date': self.epoch,
                'pct30': self.percent_30_60,
                'pct90': self.percent_90}

    @property
    def percent_30_60(self):
        """Returns percentage of loans between 30 and 90 days delinquent."""
        if self.total == 0:
            return 0
        else:
            return (self.thirty + self.sixty) * 1.0 / self.total
            # return round(((self.thirty + self.sixty) * 100.0) / self.total)

    @property
    def percent_90(self):
        if self.total == 0:
            return 0
        else:
            return self.ninety * 1.0 / self.total
            # return round((self.ninety * 100.0) / self.total)

    @property
    def epoch(self):
        return int(self.date.strftime('%s')) * 1000


class CountyMortgageData(MortgageBase):
    """
    A model to store base mortgage performance data by date and county,
    updated quarterly.
    """
    fips_type = models.CharField(max_length=6, default='county')


class MSAMortgageData(MortgageBase):
    """
    A model for aggregating mortgage performance data from
    a set of counties included in a metro area.
    """
    fips_type = models.CharField(max_length=6, default='msa')
    counties = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="A comma-separated list of FIPS for included counties.")
    states = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="A comma-separated list of state abbreviations  touched by FIPS for included counties.")

    def save(self, **kwargs):
        self.aggregate_county_data()
        super(MSAMortgageData, self).save(**kwargs)

    def aggregate_county_data(self):
        if not self.counties:
            return
        count_fields = {
            'total': 0, 'current': 0, 'thirty': 0,
            'sixty': 0, 'ninety': 0, 'other': 0}
        county_fips = self.counties.split(',')
        county_records = CountyMortgageData.objects.filter(
            fips__in=county_fips, date=self.date)
        for county in county_records:
            for field in count_fields:
                count_fields[field] += getattr(county, field)
        for field in count_fields:
            setattr(self, field, count_fields[field])
