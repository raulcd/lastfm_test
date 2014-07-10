#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import unittest

from src.myscript import Artist


class ArtistTestCase(unittest.TestCase):
    def test_add_track(self):
        artist = Artist('my_artist_name')
        artist.add_track('my_track_name', '10/01/01')
        self.assertEqual(len(artist), 1)
        artist.add_track('my_second_track_name', '10/01/01')
        self.assertEqual(len(artist), 2)
        artist.add_track('my_track_name', '09/01/01')
        self.assertEqual(len(artist), 3)
        # Use of ducktyping on the real world the date will be a datetime
        artist.add_track('my_track_name', '09/01/01')
        self.assertEqual(len(artist), 3)

    def test_get_dict(self):
        artist = Artist('my_artist_name')
        artist.add_track('my_track_name', '10/01/01')
        artist.add_track('my_second_track_name', '10/01/01')
        artist.add_track('my_track_name', '10/01/01')
        self.assertEqual(artist.get_dict(),
                         {'my_artist_name': {'my_track_name': ['10/01/01'],
                                             'my_second_track_name': ['10/01/01']}})

    def test_update_artists(self):
        artist = Artist('my_artist_name')
        artist.add_track('my_track_name', '10/01/01')
        artist.add_track('my_second_track_name', '10/01/01')
        artist2 = Artist('my_artist_name')
        artist2.add_track('my_track_name', '11/01/01')
        artist2.add_track('my_second_track_name', '11/01/01')
        #This one will not be added because it is the same date
        artist2.add_track('my_track_name', '11/01/01')
        artist.update(artist2)
        self.assertEqual(len(artist), 4)
        artist3 = Artist('my_other_artist_name')
        artist3.add_track('my_track_name', '11/01/01')
        self.assertRaises(AttributeError, artist.update, artist3)
        self.assertEqual(len(artist), 4)

if __name__ == '__main__':
    unittest.main()