## BillBored Querying
## Authors:
#### Vilem Boddicker, Rachel Williams, Austin Jones
import sqlite3
import random

''' disabling same thread check allowed these functions
    to be called upon every page refresh in the Flask 
    side of things, but is it the best/safest option?'''
db = sqlite3.connect('MusicDB1_5.db', check_same_thread=False)

cursor = db.cursor()

''' formats quiz questions and answers in the form
    "question|answer_a|answer_b|answer_c|answer_d|correct"
    where correct is a string that is equal to either a, b, c, or d.'''
def flaskFormatter(question, answer_choice, wrong_answers):
    choices = []
    choices.append(answer_choice)
    choices.extend(wrong_answers)
    random.shuffle(choices)
    pos = choices.index(answer_choice)
    print(choices)
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
    return formatted_string


### Queries that are formatted

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
    formatted_answer = answer_artist.title()
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
        formatted_wrong = wrong_artist.title()
        while formatted_wrong in wrong_answers:
        	wrong_choice = random.choice(wrongs_list)
        	wrong_artist, wrong_title = wrong_choice
        	wrong_artist = wrong_artist.strip()
        	formatted_wrong = wrong_artist.title()
        wrong_answers.append(formatted_wrong)
    return flaskFormatter(question, formatted_answer, wrong_answers)

def longest_song():
    question = "Which of the following songs is the longest in length?"
    cursor = db.cursor()
    tups = []
    while len(tups) < 4:
        randyear = random.randint(2006, 2018)
        randrank = random.randint(1, 20)
        q = "SELECT length, title, artist FROM Songs WHERE BByear=? AND rank=?;"
        cursor.execute(q, (randyear, randrank))
        entry = cursor.fetchone()
        while entry in tups:
        	randyear = random.randint(2006, 2018)
        	randrank = random.randint(1, 20)
        	q = "SELECT length, title, artist FROM Songs WHERE BByear=? AND rank=?;"
        	cursor.execute(q, (randyear, randrank))
        	entry = cursor.fetchone()
        tups.append(entry)
    longest = ''
    answer_title = ''
    answer_artist = ''
    for i in range(4):
        length = tups[i][0]
        if length > longest:
            longest = length
            answer_title = tups[i][1]
            answer_artist = tups[i][2]
            answer_artist = answer_artist.strip()
            answer_title = answer_title.strip()
            formatted_answer = answer_title + ' by ' + answer_artist.title()
    wrong_answers = []
    for i in range(4):
        length = tups[i][0]
        if length != longest:
            wrong_choice = tups[i]
            wrong_title, wrong_artist = wrong_choice[1:3]
            wrong_artist = wrong_artist.strip()
            wrong_title = wrong_title.strip()
            formatted_wrong = wrong_title + ' by ' + wrong_artist.title()
            wrong_answers.append(formatted_wrong)
    return flaskFormatter(question, formatted_answer, wrong_answers)

def howManyTopHits():
    cursor = db.cursor()
    q = """
    SELECT artiste, num_hits
    FROM (SELECT Albums.artist as artiste, COUNT(*) as num_hits
    FROM Songs, Albums
    WHERE Songs.album=Albums.title
    GROUP BY Albums.artist
    ORDER BY num_hits asc)
    WHERE num_hits > 4;
    """
    cursor.execute(q)
    popular_artists = cursor.fetchall()
    random_artist, answer_choice = random.choice(popular_artists)
    while random_artist == 'various':
        random_artist, answer_choice = random.choice(popular_artists)
    other_ints = []
    top_int = 0
    low_int = 0
    top_range = 0
    low_range = 0
    while (top_range - low_range) < 4 or (top_range - low_range) > 7:
        top_int = random.randint(0, 5)
        low_int = random.randint(0, 5)
        top_range = answer_choice + top_int
        low_range = answer_choice - low_int
    print(top_range - low_range)
    while len(other_ints) < 3:
        random_int = random.randint(low_range, top_range)
        if not(str(random_int) in other_ints) and random_int != answer_choice:
            other_ints.append(str(random_int))
    random_artist = random_artist.strip()
    if random_artist[0:3] == 'the' or ',' in random_artist:
        verb = 'have'
    else:
        verb = 'has'
    random_artist = random_artist.title()
    question = ("How many Top 100 Hits " + verb + " %s had?" % (random_artist))
    return flaskFormatter(question, str(answer_choice), other_ints)

def numberOneSong():
    cursor = db.cursor()
    randyear = random.randint(2006, 2018)
    question = ("Which of the following songs was the #1 song in %s?" % (randyear))
    q = "SELECT title, artist FROM Songs WHERE rank=1 AND BByear=?"
    cursor.execute(q, (randyear,))
    answer_title, answer_artist = cursor.fetchone()
    answer_title = answer_title.strip()
    answer_artist = answer_artist.strip()
    answer_artist = answer_artist.title()
    formatted_answer = answer_title + ' by ' + answer_artist
    wrongs_list = []
    for i in range(3):
        randrank = random.randint(2, 10)
        q = ("SELECT title, artist FROM Songs WHERE rank=? AND BByear=?")
        cursor.execute(q, (randrank, randyear))
        wrong_title, wrong_artist = cursor.fetchone()
        wrong_title = wrong_title.strip()
        wrong_artist = wrong_artist.strip()
        wrong_artist = wrong_artist.title()
        formatted_wrong = wrong_title + ' by ' + wrong_artist
        while formatted_wrong in wrongs_list:
        	randrank = random.randint(2, 10)
        	q = ("SELECT title, artist FROM Songs WHERE rank=? AND BByear=?")
        	cursor.execute(q, (randrank, randyear))
        	wrong_title, wrong_artist = cursor.fetchone()
        	wrong_title = wrong_title.strip()
        	wrong_artist = wrong_artist.strip()
        	wrong_artist = wrong_artist.title()
        	formatted_wrong = wrong_title + ' by ' + wrong_artist
        wrongs_list.append(formatted_wrong)
    return flaskFormatter(question, formatted_answer, wrongs_list)

def shortest_songs():
    cursor = db.cursor()
    tups = []
    while len(tups) < 4:
        randyear = random.randint(2006, 2018)
        randrank = random.randint(1, 20)
        q = "SELECT length, title, artist FROM Songs WHERE BByear=? AND rank=?;"
        cursor.execute(q, (randyear, randrank))
        entry = cursor.fetchone()
        while entry in tups:
        	randyear = random.randint(2006, 2018)
        	randrank = random.randint(1, 20)
        	q = "SELECT length, title, artist FROM Songs WHERE BByear=? AND rank=?;"
        	cursor.execute(q, (randyear, randrank))
        	entry = cursor.fetchone()
        tups.append(entry)
    shortest = '999999999'
    answer_title = ''
    answer_artist = ''
    for i in range(4):
        length = tups[i][0]
        if length < shortest:
            shortest = length
            answer_title, answer_artist = tups[i][1:3]
            answer_artist = answer_artist.strip()
            answer_title = answer_title.strip()
            formatted_answer = answer_title + ' by ' + answer_artist.title()
    question = ("Which of the following songs is the shortest (%s)?" % (shortest))
    wrong_answers = []
    for i in range(4):
        length = tups[i][0]
        if length != shortest:
            wrong_choice = tups[i]
            wrong_title, wrong_artist = wrong_choice[1:3]
            wrong_artist = wrong_artist.strip()
            wrong_title = wrong_title.strip()
            formatted_wrong = wrong_title + ' by ' + wrong_artist.title()
            wrong_answers.append(formatted_wrong)
    return flaskFormatter(question, formatted_answer, wrong_answers)



# creates final array of questions for quiz, each formatted in a string.
def createQuestions():
    q_list = []

    # if you're lucky, you get the easter egg question
    if random.uniform(0, 1) < 0.2:
        q_list.append(flaskFormatter("What is Mike's favorite song?", "White noise", ["'Creep' by Radiohead", "Silence", "Brown noise"]))
    else:
        q_list.append(numberOneSong())
    q_list.append(numberOneSong())
    q_list.append(findOneHitWonders())
    q_list.append(findOneHitWonders())
    q_list.append(longest_song())
    q_list.append(longest_song())
    q_list.append(howManyTopHits())
    q_list.append(howManyTopHits())
    q_list.append(shortest_songs())
    q_list.append(shortest_songs())

    random.shuffle(q_list)
    return q_list




### Queries yet to be formatted

def Rank(x, year):
    global db
    cursor = db.cursor()
    q = "SELECT title , BByear, artist From Songs WHERE rank =? AND BByear =?"
    group = []
    cursor.execute(q, (x,year))
    for tup in cursor:
        group.append(tup)

    return group

def wrong_rank():
    wrong =[]
    while len(wrong) < 3:
        x = random.randint(1,20)
        y =random.randint(2006,2018)
        z = Rank(x,y)
        wrong.append(z)
    
    return wrong

def numberonesong(x):
    global db
    cursor = db.cursor()
    q = "SELECT title, artist FROM Songs WHERE rank = 1 AND BByear =?"
    numberone= []
    cursor.execute(q, (x, ))
    for tup in cursor:
        numberone.append(tup)

    return numberone
    
def song(x):
    global db
    cursor = db.cursor()
    q= "SELECT rank, BByear FROM Songs Where title =?"
    rank = []
    cursor.execute(q, (x,))
    for tup in cursor:
        rank.append(tup)

    return rank

def billboard_rank(year):
    global db
    cursor = db.cursor()
    q = "SELECT  title, artist, rank FROM Songs Where  BByear =?"
    billboard_rank = []
    cursor.execute(q, (year,))
    for tup in cursor:
        billboard_rank.append(tup)
    for i in billboard_rank:
        print(i)

def billboard_leaders_peryear(x):
    global db
    cursor = db.cursor()
    Board = []
    q = "SELECT  artist, Count(artist) as numberofapperances ,sum(rank) as tiebreaker FROM Songs  WHERE BByear =? GROUP by artist Order by numberofapperances DESC, tiebreaker"
    cursor.execute(q, (x, ))
    for tup in cursor:
        Board.append(tup)
    for i in Board:
        print(i)

def number_appearances():
    global db
    cursor = db.cursor()
    q = "SELECT  artist, Count(artist) as numberofapperances ,sum(rank) as tiebreaker FROM Songs GROUP by artist Order by numberofapperances DESC, tiebreaker"
    cursor.execute(q)
    top50= []
    for tup in cursor:
        if len(top50) < 50:
            top50.append(tup)
    for i in top50:
        print(i)

def fastest_song():
    global db
    cursor = db.cursor()
    q = "SELECT bpm as fast, title FROM Songs GROUP by title Order by fast DESC"
    cursor.execute(q)
    top5 = []
    for tup in cursor:
        if len(top5) < 1:
            top5.append(tup)

    return top5

def slowest_songs():
    global db
    cursor = db.cursor()
    q = "SELECT bpm as slow, title FROM Songs GROUP by title Order by slow"
    cursor.execute(q)
    slowsong = []
    for tup in cursor:
        if len(slowsong) < 1:
            slowsong.append(tup)

    return slowsong

# def longest_song():
#     global db
#     cursor = db.cursor()
#     q = "SELECT length, title FROM songs GROUP By title ORDER BY length DESC"
#     cursor.execute(q)
#     long = []
#     for tup in cursor:
#         if len(long) < 1:
#             long.append(tup)

#     return long

def random_long_query():
    global db
    cursor = db.cursor()
    q = "SELECT length, title FROM songs GROUP By title ORDER BY length DESC"
    cursor.execute(q)
    random = []
    for tup in cursor:
        if len(random) < 20:
            random.append(tup)

    return random
    
def quickest_song ():
    global db
    cursor = db. cursor()
    q = "SELECT length, title FROM songs GROUP By title ORDER BY length "
    cursor.execute(q)
    quick = []
    for tup in cursor:
        if len(quick) < 1:
            quick.append(tup)


    return quick

# def find_rank():
#     x = random.randint(1,20)
#     year =random.randint(2006,2018)
#     xstring = str(x)
#     yearstring = str(year)
#     Question = "What song was ranked " + xstring + " in the year " + yearstring
#     right_title = Rank(x,year)[0][0]
#     right_artist= Rank(x,year)[0[1]
#     formatted_answer = right_title + " by " + right_artist 
    
#     wrong = wrong_rank()


#     return flaskFormatter(Question, right, wrong)



    

    
    



