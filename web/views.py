import copy
import datetime
import json
import operator

import dateparser
import pytz
from django.conf import settings
from django.views.generic import TemplateView
import urllib.request


def process_timetrial(profiles, recent_timetrials, t1, t2, t3, t4, tt):
    tt_start = dateparser.parse(tt['start_time'])
    if 'godkendt' in tt['comment'].lower() and tt_start > t1 and tt['residue']:
        tt['beers'] = len(tt['durations'])
        tt['sum_of_durations'] = sum(tt['durations'])
        period = 0
        if t1 < tt_start < t2:
            period = 1
        if t2 < tt_start < t3:
            period = 2
        if t3 < tt_start < t4:
            period = 3
        tt['penalty'] = 0
        if float(tt['residue']) > len(tt['durations']) - 1:
            tt['penalty'] = (float(tt['residue']) - (len(tt['durations']) - 1)) * 5
        tt['sum_of_durations_plus_penalty'] = tt['sum_of_durations'] + tt['penalty']
        _profile = profiles.setdefault(tt['profile'], {})
        _period = _profile.setdefault(str(period), {})
        _beers = _period.setdefault(str(len(tt['durations'])), {})
        if _beers.keys():
            if tt['sum_of_durations_plus_penalty'] < _beers['sum_of_durations_plus_penalty']:
                _period[str(len(tt['durations']))] = tt
        else:
            _period[str(len(tt['durations']))] = tt
        recent_timetrials.append(tt)


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        profiles = {}
        recent_timetrials = []
        context = super(IndexView, self).get_context_data(**kwargs)
        with urllib.request.urlopen("https://enkasseienfestforening.dk/timetrial/json/") as response:
            timetrials = response.read().decode('utf-8')
        timetrials = json.loads(timetrials)
        tz = pytz.timezone(settings.TIME_ZONE)
        t1 = datetime.datetime(year=2017, month=9, day=18).replace(tzinfo=tz)
        t2 = datetime.datetime(year=2018, month=1, day=28, hour=4).replace(tzinfo=tz)
        t3 = datetime.datetime(year=2018, month=2, day=11, hour=4).replace(tzinfo=tz)
        t4 = datetime.datetime(year=2018, month=2, day=18, hour=4).replace(tzinfo=tz)
        for tt in timetrials:
            process_timetrial(profiles, recent_timetrials, t1, t2, t3, t4, tt)
            if 7 > len(tt['durations']) > 3:
                tt2 = copy.deepcopy(tt)
                tt2['durations'] = tt2['durations'][:-1]
                process_timetrial(profiles, recent_timetrials, t1, t2, t3, t4, tt2)
        context['profiles'] = profiles
        context['recent_timetrials'] = recent_timetrials
        return context


class FilteredView(TemplateView):
    template_name = 'filtered.html'

    def get_context_data(self, **kwargs):
        context = super(FilteredView, self).get_context_data(**kwargs)
        with urllib.request.urlopen("https://enkasseienfestforening.dk/timetrial/json/") as response:
            timetrials = response.read().decode('utf-8')
        timetrials = json.loads(timetrials)
        real_times = []
        for timetrial in timetrials:
            timetrial['beers'] = len(timetrial['durations'])
            timetrial['sum_of_durations'] = sum(timetrial['durations'])
            if not timetrial['residue'] is None:
                if timetrial['residue'] <= timetrial['beers'] and \
                        timetrial['result'] == 'f':
                    real_times.append(timetrial)
        real_times = sorted(sorted(real_times, key=operator.itemgetter('sum_of_durations')),
                            key=operator.itemgetter('beers'))
        context['real_times'] = real_times
        return context
