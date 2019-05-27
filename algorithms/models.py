from django.db.models import *


class TimeStampedModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Algorithm(TimeStampedModel):
    name = CharField(max_length=200)

    def __str__(self):
        return "({}) {}".format(self.pk, self.name)

    def records(self):
        return Record.objects.filter(algorithm=self)


class Record(TimeStampedModel):
    algorithm = ForeignKey(Algorithm, on_delete=CASCADE)
    m_size = BigIntegerField()
    n_size = BigIntegerField()
    l_size = BigIntegerField()
    time = DecimalField(max_digits=20, decimal_places=5, blank=True, null=True)
    average_time = DecimalField(max_digits=20, decimal_places=5, blank=True, null=True)

    def __str__(self):
        return "({}, {}, {}) {} search time : {}ms".format(self.n_size, self.l_size, self.m_size, self.algorithm.name ,self.time)