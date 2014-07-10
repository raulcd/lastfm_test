#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import argparse
import datetime
import shelve
from collections import Counter
import requests

LAST_FM_URL = 'http://ws.audioscrobbler.com/2.0'
API_KEY = '37ec4aba2276f65295c2401e38355447'
GET_RECENT_TRACKS = 'user.getrecenttracks'
FILE_NAME = 'stored_tracks.dict'


def parse_args():
    """
    This function parses the arguments from the command line.
    If no arguments or more than one arguments are provided the execution does
    not continue.
    """
    parser = argparse.ArgumentParser(description='Retrieve user stats from Last.fm')
    parser.add_argument('username', type=str,
                        help='The username you want to retrieve data for.')
    args = parser.parse_args()
    return args.username


def last_fm_http_request(**kwargs):
    """
    Function that uses the module requests to retrieve the data from Last.fm
    """
    kwargs['format']='json'
    r = requests.get(kwargs.pop('last_fm_url', LAST_FM_URL), params=kwargs)
    return convert_data(r.json(), page=kwargs.get('page'))


def convert_data(json, page=0):
    """
    Data parsing from Last.fm JSON format to internal dict with Artists
    """
    data_retrieved = {'artists': {}}
    for x in [x for x in json['recenttracks']['track']]:
        # Parsing information of artists and tracks
        artist_name = x['artist']['#text']
        if artist_name in data_retrieved['artists']:
            artist = data_retrieved['artists'].get(artist_name)
            try:
                artist.add_track(x['name'],
                                 datetime.datetime.fromtimestamp(int(x['date']['uts'])))
            except KeyError, e:
                # If the song is currently streaming date is not in the json. Don't add the track
                # Don't add the track and go to next iteration
                continue
            data_retrieved['artists'][artist.artist_name] = artist
        else:
            artist = Artist(x['artist']['#text'])
            try:
                artist.add_track(x['name'],
                                 datetime.datetime.fromtimestamp(int(x['date']['uts'])))
            except KeyError, e:
                # If the song is currently streaming date is not in the json.
                # Don't add the track and go to next iteration
                continue
            data_retrieved['artists'][artist.artist_name] = artist
    # Oldest song retrieved
    data_retrieved['oldest_date_retrieved'] = datetime.datetime.fromtimestamp(
        int(json['recenttracks']['track'][-1]['date']['uts']))
    # Newest song retrieved. Taking into account that the last one
    # may be streaming at this moment
    if json['recenttracks']['track'][0].get('date', False):
        # In this case the most recent track is not actually being played.
        data_retrieved['newest_date_retrieved'] = datetime.datetime.fromtimestamp(
            int(json['recenttracks']['track'][0]['date']['uts']))
    else:
        # The previous one will always have been played in the past
        data_retrieved['newest_date_retrieved'] = datetime.datetime.fromtimestamp(
            int(json['recenttracks']['track'][1]['date']['uts']))
    # Storing total number of tracks and the last page requested
    data_retrieved['number_of_tracks'] = json['recenttracks']['@attr']['total']
    data_retrieved['page_requested'] = page
    return data_retrieved


def save_data(username, data_retrieved, file_dict):
    # Update current file_dict with retrieved information
    old_data = file_dict.get(username, {})
    oldest_date_retrieved = data_retrieved.pop('oldest_date_retrieved')
    newest_date_retrieved = data_retrieved.pop('newest_date_retrieved')
    number_of_tracks = data_retrieved.pop('number_of_tracks')
    page_requested = data_retrieved.pop('page_requested')
    # Update the dict for all the artists taking into account if they exist.
    for artist_name, artist_inst in data_retrieved['artists'].iteritems():
        old_artists = old_data.get('artists', {})
        if artist_name in old_artists:
            old_artists[artist_name].update(artist_inst)
        else:
            old_artists[artist_name] = artist_inst
        old_data['artists'] = old_artists
    # Calculate the number of the next page to be requested.
    # If the getRecentTrack last song was listened after the newest we have stored
    # we need to keep going with the recent ones. Otherwise ask for older pages. 0 to stop.
    if old_data.get('newest_date_retrieved', False):
        if old_data['newest_date_retrieved'] < oldest_date_retrieved:
            old_data['next_page'] = page_requested + 1
        elif int(old_data['number_of_tracks']) > sum([len(artist) for artist in old_artists.itervalues()]):
            old_data['next_page'] = sum([len(artist) for artist in old_artists.itervalues()])//10 + 1
        else:
            old_data['next_page'] = 0
    else:
        old_data['newest_date_retrieved'] = newest_date_retrieved
        if number_of_tracks == sum([len(artist) for artist in old_artists.itervalues()]):
            old_data['next_page'] = 0
        else:
            old_data['next_page'] = sum([len(artist) for artist in old_artists.itervalues()])//10 + 1
    # We store the number of tracks and the last listened track date
    old_data['number_of_tracks'] = number_of_tracks
    if newest_date_retrieved > old_data['newest_date_retrieved']:
        old_data['newest_date_retrieved'] = newest_date_retrieved
    file_dict[username] = old_data


def more_requests_needed(username, file_dict):
    """
    Generator that requests more pages or stops if no more pages are needed.
    """
    for n in range(1, 5):
        if n == 1:
            # We always want the first iteration to retrieve the latest ones
            yield last_fm_http_request(user=username, method=GET_RECENT_TRACKS,
                                       page=1, api_key=API_KEY)
        page_needed = file_dict[username]['next_page']
        # If there is more pages to be retrieved continue retrieving. Maximum 4 more.
        if page_needed:
            yield last_fm_http_request(user=username, method=GET_RECENT_TRACKS,
                                       page=page_needed, api_key=API_KEY)
        else:
            raise StopIteration("No more calls needed")


def aggregate_and_print_data(username, file_dict):
    """
    Function that agregates all the data and prints to the output
    """
    print("You have listened to a total of {0} tracks.".format(file_dict[username]['number_of_tracks']))
    # Counters to count artists and dates.
    artist_counter = Counter()
    date_list = []
    days_counter = Counter()
    for artist_name, artist_inst in file_dict[username]['artists'].iteritems():
        # Retrieve all artists from the file_dict
        artist_counter[artist_name] = len(artist_inst)
        artist_date_list = artist_inst.get_date_list()
        date_list.extend(artist_date_list)
        days_counter.update((dt.strftime("%A") for dt in artist_date_list))
    top_artists = artist_counter.most_common(5)
    print(u"Your top 5 favorite artists: {0}, {1}, {2}, {3}, {4}.".format(
        *[x for x, y in artist_counter.most_common(5)]))

    # Use timedelta to know the number of days of the window of listened tracks
    days = (max(date_list) - min(date_list)).days
    average = sum(artist_counter.itervalues()) // (days if days else 1)

    print ('You listen to an average of {0} tracks a day.'.format(average))
    print ('Your most active day is {0}.'.format(days_counter.most_common(1)[0][0]))


class Artist(object):
    """
    The class Artist organizes the artist information to count it
    and compare.
    """
    def __init__(self, artist_name):
        self.artist_name = artist_name
        self.tracks = {}

    def __eq__(self, other):
        """
        Use of the data model of python to check equality
        """
        return len(self) == len(other)

    def __lt__(self, other):
        return len(self) < len(other)

    def __len__(self):
        """
        For every track count the number of dates the track has been
        listened and sum all the different tracks.
        """
        return sum([len(x) for x in self.tracks.itervalues()])

    def __iter__(self):
        """
        Generator to iterate over an artist. On each iteration returns a
        tuple with track_name and date
        """
        for track in self.tracks:
            for date in self.tracks[track]:
                yield track, date

    def add_track(self, track_name, track_listening_date):
        """
        In order to add tracks check if it has already been added.
        If the track exists only add the date when the track was listened
        """
        if self.tracks.get(track_name, False):
            if track_listening_date not in self.tracks[track_name]:
                self.tracks[track_name].append(track_listening_date)
        else:
            self.tracks[track_name] = [track_listening_date]

    def get_dict(self):
        """
        Generates a dict from an artist.
        """
        return {self.artist_name: self.tracks}

    def update(self, other):
        """
        Method to update an artist with the same artist.
        We add all the new tracks
        """
        if self.artist_name != other.artist_name:
            raise AttributeError("{0} is not the same artist as {1}".format(
                self.artist_name, other.artist_name))
        for track, date in other:
            # Thanks to the __iter__ method on artist we are able to iterate
            self.add_track(track, date)

    def get_date_list(self):
        """
        Method to retrieve a list of dates of all the tracks listened
        """
        dates = []
        for track_dates_list in self.tracks.itervalues():
            for date in track_dates_list:
                dates.append(date)
        return dates

if __name__ == '__main__':
    # Parse args
    username = parse_args()
    # Open shelve (dict file)
    file_dict = shelve.open(FILE_NAME)
    # Iterator that requests info and we save it
    for artists_info in more_requests_needed(username, file_dict):
        save_data(username, artists_info, file_dict)
    # Save to disk once we have finished requesting information
    file_dict.sync()
    # Print and extract statistics
    aggregate_and_print_data(username, file_dict)
    # Close of the shelve
    file_dict.close()
