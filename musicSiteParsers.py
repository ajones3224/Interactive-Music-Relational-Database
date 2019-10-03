import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import datetime
import sqlite3
import random

db = sqlite3.connect('MusicDB1_6.db')

def initialize(db):
    db = sqlite3.connect('MusicDB1_6.db')
    cursor = db.cursor()
    q1 = """
CREATE TABLE IF NOT EXISTS Songs (
    title CHARACTER VARYING(50) NOT NULL,
    artist CHARACTER VARYING(100) NOT NULL,
    album CHARACTER VARYING(50) DEFAULT NULL,
    rank INTEGER NOT NULL,
    BByear INTEGER NOT NULL,
    length CHARACTER VARYING(50) DEFAULT NULL,
    bpm INTEGER DEFAULT NULL,
    tonality CHARACTER VARYING(50) DEFAULT NULL,
    PRIMARY KEY (title, artist, BByear)
    );
"""
    cursor.execute(q1)
    q2 = """
CREATE TABLE IF NOT EXISTS Albums (
    title CHARACTER VARYING(50) NOT NULL,
    artist CHARACTER VARYING(50) NOT NULL,
    genre CHARACTER VARYING(50) NOT NULL,
    release_date CHARACTER VARYING(50) NOT NULL,
    PRIMARY KEY (title, artist)
    );
"""
    cursor.execute(q2)
    cursor.close()
    start_over = False
    try:
        start_over
    except NameError:
        start_over = False
    if start_over:
        parseBillboardToDB()


def reset(db):
    cursor = db.cursor()
    q = "DELETE FROM Numbers"
    cursor.execute(q)
    db.commit()
    cursor.close()

def parseBillboardToDB():
    cursor = db.cursor()
    for i in range(2006, 2019):
        webAddress = 'https://www.billboard.com/charts/year-end/' + str(i) + '/hot-100-songs'
        r = requests.get(webAddress)
        soup = BeautifulSoup(r.text, 'html.parser')
        #bbData = open(textFileBase + "_" + str(i), mode='w')
        results = soup.find_all('article', attrs={'class':'ye-chart-item'})
        for result in results:
            songTitle = result.find('div', attrs={'class':'ye-chart-item__title'}).text[1:-1]
            rank = result.find('div', attrs={'class':'ye-chart-item__rank'}).text[1:-1]
            artist = result.find('div', attrs={'class':'ye-chart-item__artist'}).text[1:-1]
            #entry = songTitle + ', ' + artist + ', ' + rank
            #entry = entry.replace('\n', '')
            #bbData.write(entry + '\n')
            artist.replace('"', "'")
            songTitle.replace('"', "'")
            q = """
            INSERT INTO Songs (title, artist, rank, BByear)
            VALUES (?, ?, ?, ?);
            """
            cursor.execute(q, (songTitle.strip(), artist.strip(), int(rank), i))
        #bbData.close()
    cursor.close()
    db.commit()
    #db.close()

def parseBillboardNormal(webAddress, textFile, printIt):
    r = requests.get(webAddress)
    soup = BeautifulSoup(r.text, 'html.parser')
    bbData = open(textFile, mode='w')
    results = soup.find_all('article', attrs={'class':'ye-chart-item'})
    for result in results:
        songTitle = result.find('div', attrs={'class':'ye-chart-item__title'}).text[1:-1]
        rank = result.find('div', attrs={'class':'ye-chart-item__rank'}).text[1:-1]
        artist = result.find('div', attrs={'class':'ye-chart-item__artist'}).text[1:-1]
        entry = artist + ', ' + songTitle + ', ' + rank
        entry = entry.replace('\n', '')
        bbData.write(entry + '\n')
        if printIt:
            print(entry)
    bbData.close()
    

def getAlbumDiscogs(inTextFile, outTextFile_songs, outTextFile_albums):
    with open(inTextFile, 'r') as bbData:
        reader = csv.reader(bbData, delimiter=',')
        songData = open(outTextFile_songs, mode='w')
        albumData = open(outTextFile_albums, mode='w')
        accesses = 0
        rank = 0
        for row in reader:
            rank += 1
            strank = str(rank)
            billboard_year = inTextFile[-4:]
            cleanArtist = row[0]
            if cleanArtist[0] == ' ':
                cleanArtist = cleanArtist[1:]
            cleanArtist = cleanArtist.lower()
            artist = cleanArtist
            artist = artist.replace("'", '')
            artist = artist.replace("& ", ' ')
            artist = artist.replace("*", '')
            artist = artist.replace(", ", " ")
            artist = artist.replace("featuring ", '')
            artist = artist.replace(" x ", ' ')
            artist = artist.replace("$", "s")
            artist = artist.replace(" ", "+") + '+'
            cleanSong = row[1]
            if cleanSong[0] == ' ':
                cleanSong = cleanSong[1:]
            cleanSong = cleanSong.lower()
            song = cleanSong
            song = song.replace("'", '')
            song = song.replace("& ", ' ')
            song = song.replace(", ", " ")
            song = song.replace(".", '')
            song = song.replace(" ", "+")
            query_base_album = 'https://www.discogs.com/search/?q='
            query_base_other = 'https://www.discogs.com/search/?q='
            query_album = query_base_album + artist + song + '&format_exact=Album&type=all'
            query_other = query_base_other + artist + song + '&type=all'
            initial_page = requests.get(query_album)
            #accesses += 1
            time.sleep(15)
            initial_soup = BeautifulSoup(initial_page.text, 'html.parser')
            initial_results = initial_soup.find('a', attrs={'class':'search_result_title'})
            if initial_results is None:
                initial_page = requests.get(query_other)
                #accesses += 1
                time.sleep(15)
                initial_soup = BeautifulSoup(initial_page.text, 'html.parser')
                initial_results = initial_soup.find('a', attrs={'class':'search_result_title'})
            if initial_results is None:
                print("couldn't get album data for " + cleanArtist + ": " + cleanSong)
                continue
            album_title = initial_results['title'].lower()
            next_page_tail = initial_results['href']
            next_page_site = 'https://www.discogs.com' + next_page_tail
            next_page = requests.get(next_page_site)
            #accesses += 1
            time.sleep(15)
            next_soup = BeautifulSoup(next_page.text, 'html.parser')
            profile_results = next_soup.find('div', attrs={'class':'profile'})
            if profile_results is None:
                print("couldn't get album data for " + cleanArtist + ': ' + cleanSong)
                continue
            genre_results = profile_results.find_all('a')
            genre = ''
            album_artist = ''
            firstGenre = True
            firstArtist = True
            for result in genre_results:
                if "genre" in result['href']:
                    if firstGenre:
                        genre = result.get_text()
                        firstGenre = False
                    else:
                        genre += ', ' + result.get_text()
                elif "artist" in result['href']:
                    if firstArtist:
                        album_artist = result.get_text().strip()
                        firstArtist = False
                    else:
                        album_artist += ', ' + result.get_text().strip()
            genre = genre.lower()
            album_artist = album_artist.lower()
            for entry in genre_results:
                if "year" in entry['href']:
                    album_year = entry.get_text().strip()
            songData.write('%s, %s, %s, %s, %s\n' % (cleanSong, cleanArtist, album_title, strank, billboard_year))
            print('%s, %s, %s, %s, %s written to file %s' % (cleanSong, cleanArtist, album_title, strank, billboard_year, outTextFile_songs))
            albumData.write('%s, %s, %s, %s\n' % (album_title, cleanArtist, album_year, genre))
            print('%s, %s, %s, %s written to file %s' % (album_title, album_artist, album_year, genre, outTextFile_albums))            
            
def getAlbumDiscogsToDB(outTextFile_songs, outTextFile_albums):
    cursor = db.cursor()
    songs_not_found = []
    songData = open(outTextFile_songs, mode='w')
    albumData = open(outTextFile_albums, mode='w')
    for i in range(2016, 2019):
        low = 1
        high = 101
        if i == 2016:
            low = 39
        for n in range(low, high):
            q = ("SELECT title, artist FROM Songs WHERE BByear=? AND rank=?;")
            cursor.execute(q, (i, n))
            cleanArtist, cleanSong = cursor.fetchone()
            if cleanArtist[0] == ' ':
                cleanArtist = cleanArtist[1:]
            cleanArtist = cleanArtist.lower()
            artist = cleanArtist
            artist = artist.replace("'", '')
            artist = artist.replace("& ", ' ')
            artist = artist.replace("*", '')
            artist = artist.replace(", ", " ")
            artist = artist.replace("featuring ", '')
            artist = artist.replace(" x ", ' ')
            artist = artist.replace("$", "s")
            artist = artist.replace(" ", "+") + '+'
            if cleanSong[0] == ' ':
                cleanSong = cleanSong[1:]
            cleanSong = cleanSong.lower()
            song = cleanSong
            song = song.replace("'", '')
            song = song.replace("& ", ' ')
            song = song.replace(", ", " ")
            song = song.replace(".", '')
            song = song.replace(" ", "+")
            query_base_album = 'https://www.discogs.com/search/?q='
            query_base_other = 'https://www.discogs.com/search/?q='
            query_album = query_base_album + artist + song + '&format_exact=Album&type=all'
            query_other = query_base_other + artist + song + '&type=all'
            initial_page = requests.get(query_album)
            #accesses += 1
            time.sleep(15)
            initial_soup = BeautifulSoup(initial_page.text, 'html.parser')
            initial_results = initial_soup.find('a', attrs={'class':'search_result_title'})
            if initial_results is None:
                initial_page = requests.get(query_other)
                #accesses += 1
                time.sleep(15)
                initial_soup = BeautifulSoup(initial_page.text, 'html.parser')
                initial_results = initial_soup.find('a', attrs={'class':'search_result_title'})
            if initial_results is None:
                print("couldn't get album data for " + cleanArtist + ': ' + cleanSong)
                songs_not_found.append([cleanSong, cleanArtist])
                continue
            album_title = initial_results['title'].lower()
            next_page_tail = initial_results['href']
            next_page_site = 'https://www.discogs.com' + next_page_tail
            next_page = requests.get(next_page_site)
            #accesses += 1
            time.sleep(15)
            next_soup = BeautifulSoup(next_page.text, 'html.parser')
            profile_results = next_soup.find('div', attrs={'class':'profile'})
            if profile_results is None:
                print("couldn't get album data for " + cleanArtist + ': ' + cleanSong)
                songs_not_found.append([cleanSong, cleanArtist])
                continue
            genre_results = profile_results.find_all('a')
            genre = ''
            album_artist = ''
            firstGenre = True
            firstArtist = True
            for result in genre_results:
                if "genre" in result['href']:
                    if firstGenre:
                        genre = result.get_text()
                        firstGenre = False
                    else:
                        genre += ', ' + result.get_text()
                elif "artist" in result['href']:
                    if firstArtist:
                        album_artist = result.get_text().strip()
                        firstArtist = False
                    else:
                        album_artist += ', ' + result.get_text().strip()
            genre = genre.lower()
            album_artist = album_artist.lower()
            if any(char == '(' for char in album_artist):
                album_artist = album_artist[:-3]
                album_artist.strip()
            for entry in genre_results:
                if "year" in entry['href']:
                    album_year = entry.get_text().strip()
            songData.write('%s, %s, %s, %s, %s\n' % (cleanSong, cleanArtist, album_title, str(n), str(i)))
            print('%s, %s, %s, %s, %s written to file %s' % (cleanSong, cleanArtist, album_title, str(n), str(i), outTextFile_songs))
            albumData.write('%s, %s, %s, %s\n' % (album_title, cleanArtist, album_year, genre))
            print('%s, %s, %s, %s written to file %s' % (album_title, album_artist, album_year, genre, outTextFile_albums))            
            q1 = """
            UPDATE Songs
            SET album=?
            WHERE rank=? AND BByear=?;
            """
            cursor.execute(q1, (album_title, n, i))
            db.commit()
            q2 = """
            INSERT OR REPLACE INTO Albums(title, artist, genre, release_date)
            VALUES (?, ?, ?, ?);
            """
            cursor.execute(q2, (album_title, album_artist, genre, album_year))
            db.commit()
        print(songs_not_found)
    db.commit()
    db.close()
    print("Songs not found: ")
    for entry in songs_not_found:
        print(entry[0], entry[1])
    return songs_not_found

def reverse_genre_year():
    entries = db.cursor()
    q = "SELECT * FROM Albums;"
    entries.execute(q)
    albums = []
    keep_goin = True
    while type(entries) != None:
        cursor = db.cursor()
        try:
            title, artist, release_date, genre = entries.fetchone()
        except TypeError:
            break
        if any(char == '(' for char in artist):
            artist = artist[:-3]
            artist = artist.strip()
        q2 = """
        UPDATE Albums
        SET genre=?, release_date=?, artist=?
        WHERE title=?;
        """
        cursor.execute(q2, (genre, release_date, artist, title))
    db.commit()


def find_missing():
    cursor = db.cursor()
    missing = []
    for i in range(2006, 2019):
        for n in range(1, 101):
            q = """
            SELECT title, artist
            FROM Songs
            WHERE BByear=? AND rank=?
            """
            cursor.execute(q, (i, n))
            try:
                title, artist = cursor.fetchone()
            except TypeError:
                missing.append([i, n])
    return missing

# genre table for albums
# "featuring" table, primary artist attribute of songs

# artists with hits on top 100 EXCEPT artists where COUNT(artist) > 1
# suggestions :
#   iterate over the search, delete the last letters until you find a match
#   LIKE operator

# Edit distance - the number of characters that one string has different from another
# tree structure used to get "partial match" information
# TRIE - tree-like structure that

def parseTuneBatToDB(outTextFile):
    cursor = db.cursor()
    bpmData = open(outTextFile, mode='w')
    couldnt_get = []
    low_year = 2006
    high_year = 2019
    high_rank = 101
    for i in range(low_year, high_year):
        low_rank = 1
        if i == 2008:
            low_rank = 21
        for n in range(low_rank, 101):
            for attempt in range(10):
                try:
                    q = ("SELECT title, artist FROM Songs WHERE BByear=? AND rank=?;")
                    cursor.execute(q, (i, n))
                    try:
                        cleanSong, cleanArtist = cursor.fetchone()
                    except TypeError:
                        continue
                    if cleanArtist[0] == ' ':
                        cleanArtist = cleanArtist[1:]
                    artist = cleanArtist.lower()
                    artist = artist.replace("'", '')
                    artist = artist.replace("& ", ' ')
                    artist = artist.replace("*", '')
                    artist = artist.replace(", ", " ")
                    artist = artist.replace("featuring ", '')
                    artist = artist.replace("Featuring ", '')
                    artist = artist.replace(".", '')
                    artist = artist.replace(" x ", ' ')
                    artist = artist.replace(" ", "+") + '+'
                    if cleanSong[0] == ' ':
                        cleanSong = cleanSong[1:]
                    song = cleanSong.lower()
                    song = song.replace("'", '')
                    song = song.replace("& ", ' ')
                    song = song.replace(", ", " ")
                    song = song.replace(".", '')
                    song = song.replace(" ", "+")
                    webBase = 'https://tunebat.com'
                    webAddress = webBase + '/Search?q=' + artist + song
                    initial_page = requests.get(webAddress)
                    initial_soup = BeautifulSoup(initial_page.text, 'html.parser')
                    initial_results = initial_soup.find_all('a', attrs={'class':'search-link col-md-11 col-sm-11 col-xs-12'})
                    if initial_results == None or len(initial_results) < 1:
                        bpmData.write('couldn\'t get data for %s by %s' % (cleanSong, cleanArtist))
                        print('couldn\'t get data for %s by %s' % (cleanSong, cleanArtist))
                        couldnt_get.append((cleanSong, cleanArtist))
                        continue
                    songPage = webBase + initial_results[0]['href']
                    r = requests.get(songPage)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    aName = soup.find('h2', attrs={'class':'main-artist-name'}).get_text()[1:-1]
                    aName = aName.lower()
                    #aName = aName.replace("'", '')
                    songName = soup.find('h1', attrs ={'class':'main-track-name'}).get_text()[1:-1]
                    songName = songName.lower()
                    #songName = songName.replace("'", '')
                    major_atts = soup.find_all('div', attrs={'class':'row main-attribute-value'})
                    tonality = major_atts[0].get_text()
                    length = major_atts[2].get_text()
                    bpm = major_atts[3].get_text()
                    if any([tonality.strip() == '???', length.strip() == '???', bpm.strip() == '???']):
                        raise ValueError('bad tunebat! try again >:(')
                    song_atts = soup.find_all('td', attrs={'class':'attribute-table-element'})
                    #if songs_atts != None or len(song_atts) < 1:
                        #ene = song_atts[0].get_text() # energy
                        #dan = song_atts[1].get_text() # danceability
                        #hap = song_atts[2].get_text() # happiness
                        #lou = song_atts[3].get_text() # loudness
                        #aco = song_atts[4].get_text() # acousticness
                        #ins = song_atts[5].get_text() # instrumentalness
                        #liv = song_atts[6].get_text() # liveness
                        #spe = song_atts[7].get_text() # speechiness
                    #bpmData.write('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n' % (aName, songName, rank, year, length, bpm, key, ene, dan, hap, lou, aco, ins, liv, spe))
                    q1 = """
                    UPDATE Songs
                    SET length=?, bpm=?, tonality=?
                    WHERE BByear=? AND rank=?;
                    """
                    cursor.execute(q1, (length, bpm, tonality, i, n))
                    print("%d, %d || length: %s, bpm: %s, tonality: %s updated for %s by %s" % (n, i, length, bpm, tonality, cleanSong, cleanArtist))
                    #print('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s added to file %s' % (aName, songName, rank, year, length, bpm, key, ene, dan, hap, lou, aco, ins, liv, spe, outTextFile))
                    db.commit()
                except ValueError:
                    continue
                else:
                    break
            continue
    bpmData.close()
    #db.commit()
    return couldnt_get

 # loop over the database, populated with billboard files
def parseSongBPM_two(inTextFile, outTextFile):
    year = inTextFile[-4:]
    with open(inTextFile, 'r') as bbData:
        reader = csv.reader(bbData, delimiter=',')
        bpmData = open(outTextFile, mode='w')
        for row in reader:
            rank = row[2].strip()
            cleanArtist = row[0]
            if cleanArtist[0] == ' ':
                cleanArtist = cleanArtist[1:]
            artist = cleanArtist.lower()
            artist = artist.replace("'", '')
            artist = artist.replace("& ", ' ')
            artist = artist.replace("*", '')
            artist = artist.replace(", ", " ")
            artist = artist.replace("featuring ", '')
            artist = artist.replace(" x ", ' ')
            artist = artist.replace(" ", "+") + '+'
            cleanSong = row[1]
            if cleanSong[0] == ' ':
                cleanSong = cleanSong[1:]
            song = cleanSong.lower()
            song = song.replace("'", '')
            song = song.replace("& ", ' ')
            song = song.replace(", ", " ")
            song = song.replace(".", '')
            song = song.replace(" ", "+")
            webBase = 'https://tunebat.com'
            webAddress = webBase + '/Search?q=' + artist + song
            initial_page = requests.get(webAddress)
            initial_soup = BeautifulSoup(initial_page.text, 'html.parser')
            initial_results = initial_soup.find_all('a', attrs={'class':'search-link col-md-11 col-sm-11 col-xs-12'})
            if type(initial_results) == NoneType or initial_results == None:
                bpmData.write('couldn\'t get data for %s by %s' % (cleanSong, cleanArtist))
                print('couldn\'t get data for %s by %s' % (cleanSong, cleanArtist))
                continue
            songPage = webBase + initial_results[0]['href']
            r = requests.get(songPage)
            soup = BeautifulSoup(r.text, 'html.parser')
            aName = soup.find('h2', attrs={'class':'main-artist-name'}).get_text()[1:-1]
            aName = aName.lower()
            #aName = aName.replace("'", '')
            songName = soup.find('h1', attrs ={'class':'main-track-name'}).get_text()[1:-1]
            songName = songName.lower()
            #songName = songName.replace("'", '')
            major_atts = soup.find_all('div', attrs={'class':'row main-attribute-value'})
            key = major_atts[0].get_text()
            length = major_atts[2].get_text()
            bpm = major_atts[3].get_text()
            song_atts = soup.find_all('td', attrs={'class':'attribute-table-element'})
            ene = song_atts[0].get_text() # energy
            dan = song_atts[1].get_text() # danceability
            hap = song_atts[2].get_text() # happiness
            lou = song_atts[3].get_text() # loudness
            aco = song_atts[4].get_text() # acousticness
            ins = song_atts[5].get_text() # instrumentalness
            liv = song_atts[6].get_text() # liveness
            spe = song_atts[7].get_text() # speechiness
            bpmData.write('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n' % (aName, songName, rank, year, length, bpm, key, ene, dan, hap, lou, aco, ins, liv, spe))
            print('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s added to file %s' % (aName, songName, rank, year, length, bpm, key, ene, dan, hap, lou, aco, ins, liv, spe, outTextFile))
        bpmData.close()

def parseSongBPM_three(artist, song, rank, outTextFile):
    bpmData = open(outTextFile, mode='w')
    artist = artist.lower()
    if artist[0] == ' ':
        artist = artist[1:]
    artist = artist.replace("'", '')
    artist = artist.replace("& ", ' ')
    artist = artist.replace("*", '')
    artist = artist.replace(" ", "+") + '+'
    artist = artist.replace(", ", " ")
    artist = artist.replace("featuring ", '')
    artist = artist.replace(" x ", ' ')
    song = song.lower()
    if song[0] == ' ':
        song = song[1:]
    song = song.replace("'", '')
    song = song.replace("& ", ' ')
    song = song.replace(", ", " ")
    song = song.replace(" ", "+")
    song = song.replace(".", '')
    webBase = 'https://tunebat.com'
    webAddress = webBase + '/Search?q=' + artist + song
    initial_page = requests.get(webAddress)
    initial_soup = BeautifulSoup(initial_page.text, 'html.parser')
    initial_results = initial_soup.find_all('a', attrs={'class':'search-link col-md-11 col-sm-11 col-xs-12'})
    songPage = webBase + initial_results[0]['href']
    r = requests.get(songPage)
    soup = BeautifulSoup(r.text, 'html.parser')
    aName = soup.find('h2', attrs={'class':'main-artist-name'}).get_text()[1:-1]
    aName = aName.lower()
    songName = soup.find('h1', attrs ={'class':'main-track-name'}).get_text()[1:-1]
    songName = songName.lower()
    major_atts = soup.find_all('div', attrs={'class':'row main-attribute-value'})
    key = major_atts[0].get_text()
    length = major_atts[2].get_text()
    bpm = major_atts[3].get_text()
    song_atts = soup.find_all('td', attrs={'class':'attribute-table-element'})
    ene = song_atts[0].get_text() # energy
    dan = song_atts[1].get_text() # danceability
    hap = song_atts[2].get_text() # happiness
    lou = song_atts[3].get_text() # loudness
    aco = song_atts[4].get_text() # acousticness
    ins = song_atts[5].get_text() # instrumentalness
    liv = song_atts[6].get_text() # liveness
    spe = song_atts[7].get_text() # speechiness
    bpmData.write('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' % (aName, songName, rank, length, bpm, key, ene, dan, hap, lou, aco, ins, liv, spe))
    print('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s added to file %s' % (aName, songName, rank, length, bpm, key, ene, dan, hap, lou, aco, ins, liv, spe, outTextFile))
    bpmData.close()


def findOneHitWonders():
    question = 'Which of the following artists has only had a song on the Billboard Hot 100 one time?'
    answer_cursor = db.cursor()
    wrong_cursor = db.cursor()
    answer_q = """
    SELECT artiste, song
    FROM (SELECT Albums.artist as artiste, Songs.title as song, COUNT(*) as num_hits
    FROM Songs, Albums
    WHERE Songs.album=Albums.title
    GROUP BY Albums.artist
    ORDER BY num_hits asc)
    WHERE num_hits = 1;
    """
    answer_cursor.execute(answer_q)
    answers_list = answer_cursor.fetchall()
    answer_choice = random.choice(answers_list)
    answer_artist, answer_title = answer_choice
    answer_artist = answer_artist.strip()
    answer_title = answer_title.strip()
    formatted_answer = answer_title + ' by ' + answer_artist.title()
    wrong_answers = []
    for i in range(3):
        x = random.randint(2, 4)
        wrong_q = """
        SELECT artiste, song
        FROM (SELECT Albums.artist as artiste, Songs.title as song, COUNT(*) as num_hits
        FROM Songs, Albums
        WHERE Songs.album=Albums.title
        GROUP BY Albums.artist
        ORDER BY num_hits asc)
        WHERE num_hits = ?;
        """
        wrong_cursor.execute(wrong_q, (x,))
        wrongs_list = wrong_cursor.fetchall()
        wrong_choice = random.choice(wrongs_list)
        wrong_artist, wrong_title = wrong_choice
        wrong_artist = wrong_artist.strip()
        wrong_title = wrong_title.strip()
        formatted_wrong = wrong_title + ' by ' + wrong_artist.title()
        wrong_answers.append(formatted_wrong)
    flaskFormatter(question, formatted_answer, wrong_answers)

def longest_song():
    cursor = db.cursor()
    random_year = random.randint(2006, 2018)
    question = ('Which of the following songs is the longest from %d?' % (random_year))
    selected = []
    for i in range(4):
        random_rank = random.randint(0, 20)
        selection_q = """
        SELECT title, artist, length
        FROM Songs
        WHERE BByear=? AND rank=?;
        """
        cursor.execute(selection_q, (random_year, random_rank))
        try:
            title, artist, length = cursor.fetchone()
        except TypeError:
            continue
        
        

def who_wrote():
    return None

def top_album():
    random_year = random.randint(2006, 2018)
    question = ('Which of the following albums had the most songs on the Hot 100 in %d?' % (random_year))


def long_runs():
    #2 or more years on the top 100
    return None

def most_common_genre():
    random_year = random.randint(2006, 2018)
    question = ('Which of the following genres was the most popular in the year %d?' % (random_year))

def flaskFormatter(question, answer_choice, wrong_answers):
    choices = []
    choices.append(answer_choice)
    choices.extend(wrong_answers)
    random.shuffle(choices)
    print(choices)
    pos = choices.index(answer_choice)
    answer_letter = ''
    if pos == 0:
        answer_letter = 'a'
    elif pos == 1:
        answer_letter = 'b'
    elif pos == 2:
        answer_letter = 'c'
    elif pos == 3:
        answer_letter = 'd'
    formatted_string = question + '|'
    for i in range(4):
        formatted_string += choices[i] + '|'
    formatted_string += answer_letter
    print(formatted_string)
    return formatted_string
    


if __name__ == '__main__':
    db = sqlite3.connect('MusicDB1_6.db')
    initialize(db)


# bpm and
# readme doc: what websites i used, what tools i used, and what's the purpose
# give that and the database, with a repl that allows
# what would make it MORE than satisfactory
# if there's evidence that I've found some interesting results
# Have several interesting queries (more than just a select)
# May require use of Python-specific tools
# 3-4 seriously interesting questions, put into queries


# Maybe scrape wikipedia for artist age, genre


# write a little python script
# 
# different table of song info from billboard week by week

# folder with database, python code, readme doc with what the code is and conclusion


# have the code report that if it can't find anything on tunebat matching the track

# Schema

# CREATE TABLE billboard_rankings (
    # numerical id
    # title
    # artist
    # album
    # billboard year
    # billboard rank
    # weeks on top 100
    # start date top 100
    # end date top 100
# );

# if I can't get every BPM tuple, then make a separate songQuality table

# CREATE TABLE songQualities (
    # title
    # artist # maybe instead of title and artist, a song_id that references billboard_rankings table
    # BPM
    # length
    # tonality
    # energy
    # danceability
    # happiness
    # loudness
    # acousticness
    # instrumentalness
    # liveness
    # speechiness
# );

# CREATE TABLE artists (
    # artist_name
    # artist_genre
    #

# CREATE TABLE songs (
    # artist
    # album
    # track
# );

# CREATE TABLE albums (
    # album name
    # artist
    # year
    # genre
# );




# populating a database
# artists, songs, albums
#

# for next Wednesday:
#   SongBPM fix parser
#   
                                     
    
#<th class="attribute-table-header" title="0 - 100 how intense and active the track is, based
#on general entropy, onset rate, timbre, perceived loudness, and dynamic range"><i></i>
#Energy</th><th class="attribute-table-header" title="0 - 100 how appropriate the track is
#for dancing based on overall regularity, beat strength, rhythm stability, and tempo"><i></i>
#Danceability</th><th class="attribute-table-header" title="0 - 100 how cheerful and positive
#the track is"><i></i> Happiness</th><th class="attribute-table-header" title="-60dB – 0dB the
#average decibel amplitude across the track"><i></i> Loudness</th><th class="attribute-table-header"
#title="0 - 100 how likely the track is acoustic"><i></i> Acousticness</th><th class="attribute-
#table-header" title="0 - 100 how likely the track contains no spoken word vocals"><i></i>
#Instrumentalness</th><th class="attribute-table-header" title="0 - 100 how likely the track
#was recorded with a live audience"><i></i> Liveness</th><th class="attribute-table-header"
#title="0 - 100 how present spoken words are in the track"><i></i> Speechiness</th></tr><tr><td
#class="attribute-table-element" title="0 - 100 how intense and active the track is, based on
#general entropy, onset rate, timbre, perceived loudness, and dynamic range">45</td><td
#class="attribute-table-element" title="0 - 100 how appropriate the track is for dancing based
#on overall regularity, beat strength, rhythm stability, and tempo">75</td><td class="attribute-
#table-element" title="0 - 100 how cheerful and positive the track is">36</td><td class="attribute-
#table-element" title="-60dB – 0dB the average decibel amplitude across the track">-9 dB</td>
#<td class="attribute-table-element" title="0 - 100 how likely the track is acoustic">3</td>
#<td class="attribute-table-element" title="0 - 100 how likely the track contains no spoken word
#vocals">0</td><td class="attribute-table-element" title="0 - 100 how likely the track was
#recorded with a live audience">55</td><td class="attribute-table-element" title="0 - 100
#how present spoken words are in the track">11</td></tr></tbody></table></div><div class="attribute
#Table hidden-md hidden-sm hidden-lg"><table class="col-md-12 col-sm-12 col-xs-12 attribute-
#table"><tbody><tr><th class="attribute-table-header" title="0 - 100 how intense and active
#the track is, based on general entropy, onset rate, timbre, perceived loudness, and dynamic range">
#<i></i> Energy</th><th class="attribute-table-header" title="0 - 100 how appropriate the track
#is for dancing based on overall regularity, beat strength, rhythm stability, and tempo"><i>
#</i> Danceability</th><th class="attribute-table-header" title="0 - 100 how cheerful and positive
#the track is"><i></i> Happiness</th><th class="attribute-table-header" title="-60dB – 0dB the
#average decibel amplitude across the track"><i></i> Loudness</th></tr><tr><td class="attribute-
#table-element" title="0 - 100 how intense and active the track is, based on general entropy,
#onset rate, timbre, perceived loudness, and dynamic range">45</td><td class="attribute-table-
#element" title="0 - 100 how appropriate the track is for dancing based on overall regularity,
#beat strength, rhythm stability, and tempo">75</td><td class="attribute-table-element"
#title="0 - 100 how cheerful and positive the track is">36</td><td class="attribute-table-
#element" title="-60dB – 0dB the average decibel amplitude across the track">-9 dB</td>
#</tr></tbody></table></div><div class="attributeTable hidden-md hidden-sm hidden-lg"><table
#class="col-md-12 col-sm-12 col-xs-12 attribute-table"><tbody><tr><th class="attribute-table-header"
#title="0 - 100 how likely the track is acoustic"><i></i> Acousticness</th><th class="attribute-
#table-header" title="0 - 100 how likely the track contains no spoken word vocals"><i></i>
#Instrumentalness</th><th class="attribute-table-header" title="0 - 100 how likely the track
#was recorded with a live audience"><i></i> Liveness</th><th class="attribute-table-header"
#title="0 - 100 how present spoken words are in the track"><i></i> Speechiness</th></tr><tr>
#<td class="attribute-table-element" title="0 - 100 how likely the track is acoustic">3</td>
#<td class="attribute-table-element" title="0 - 100 how likely the track contains no spoken word vocals">
#0</td><td class="attribute-table-element" title="0 - 100 how likely the track was recorded with a live
#audience">55</td><td class="attribute-table-element" title=
#"0 - 100 how present spoken words are in the track">11</td></tr></tbody></table></div></div></div></div></div></div></div>
