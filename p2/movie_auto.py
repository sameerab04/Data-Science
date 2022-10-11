import sqlite3 as lite
import csv
import re
import pandas as pd
import argparse
import collections
import json
import glob
import math
import os
import requests
import string
import sqlite3
import sys
import time
import xml


class Movie_auto(object):
    def __init__(self, db_name):
        #db_name: "cs1656-public.db"
        self.con = lite.connect(db_name)
        self.cur = self.con.cursor()

    #q0 is an example
    def q0(self):
        query = '''SELECT COUNT(*) FROM Actors'''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q1(self):
        query = '''
        SELECT fname, lname
        FROM Actors a, Cast cast1, Cast cast2, Movies movie1, Movies movie2
        WHERE a.aid = cast1.aid
        AND cast1.mid = movie1.mid
        AND (movie1.year >= 1980 AND movie1.year <=1990)
        AND a.aid = cast2.aid
        AND cast2.mid = movie2.mid
        AND movie2.year >= 2000
        ORDER BY lname ASC, fname ASC
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows


    def q2(self):
        query = '''

        SELECT title, year
        FROM Movies
        WHERE year = (SELECT year FROM Movies where title = 'Rogue One: A Star Wars Story')
        AND rank > (SELECT rank from Movies where title = 'Rogue One: A Star Wars Story')
        ORDER BY title ASC
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q3(self):
        query = '''
            SELECT a.fname, a.lname, COUNT(m.title) as num
            FROM Actors a
            INNER JOIN Cast c ON a.aid = c.aid
            INNER JOIN Movies m ON c.mid = m.mid
            WHERE m.title LIKE '%Star Wars%'
            GROUP BY a.fname, a.lname
            ORDER BY num DESC, a.lname ASC, a.fname ASC
        '''

        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows


    def q4(self):

        query = '''
            SELECT a.fname, a.lname
            FROM Actors a
            INNER JOIN Cast c ON a.aid = c.aid
            INNER JOIN Movies m on c.mid = m.mid
            WHERE a.aid NOT IN (SELECT a2.aid
                                FROM Actors a2
                                INNER JOIN Cast c2 ON a2.aid = c2.aid
                                INNER JOIN Movies m2 ON m2.mid = c2.mid
                                WHERE m2.year >= 1980)
            GROUP BY a.aid
            HAVING COUNT (m.title) >= 1
            ORDER BY a.lname ASC, a.fname ASC

        '''

        self.cur.execute(query)

        all_rows = self.cur.fetchall()
        return all_rows

    def q5(self):
        query0 = ''' DROP VIEW IF EXISTS dir_count
        '''
        query1 = '''
        create view dir_count as
            SELECT DISTINCT md.did, count(md.mid) as num
            FROM Movie_Director md
            GROUP BY md.did

        '''
        query2 = '''
        SELECT d.fname, d.lname, dc.num
        FROM Directors d, dir_count dc
        WHERE d.did = dc.did
        ORDER BY dc.num DESC, d.lname ASC
        LIMIT 10
        '''
        self.cur.execute(query0)
        self.cur.execute(query1)
        self.cur.execute(query2)
        all_rows = self.cur.fetchall()
        return all_rows

    def q6(self):
        query = ''' DROP VIEW IF EXISTS cast_count
        '''
        query1 = '''
            create view cast_count as
                SELECT DISTINCT m.mid, count(c.aid) as num_actors
                FROM Cast c, Movies m
                WHERE c.mid = m.mid
                GROUP BY title
                HAVING num_actors >= 1
        '''
        query2 = '''
            SELECT title, num_actors
            FROM Movies m, cast_count cc
            WHERE m.mid = cc.mid
            AND cc.num_actors >= (
                SELECT min(num_actors)
                FROM (SELECT num_actors
                        FROM cast_count
                        ORDER BY num_actors DESC
                        LIMIT 10))
            ORDER BY num_actors DESC

        '''
        self.cur.execute(query)
        self.cur.execute(query1)
        self.cur.execute(query2)
        all_rows = self.cur.fetchall()
        return all_rows

    def q7(self):
        query0 = 'DROP VIEW IF EXISTS gender'

        query1 = '''
            CREATE VIEW gender as
                SELECT a.aid, a.gender, m.mid, m.title, c.aid, c.mid
                FROM actors a, movies m, cast c
                WHERE a.aid = c.aid
                AND m.mid = c.mid
        '''


        query2 = '''
            SELECT title, sum(gender = 'Female')  f, sum(gender = 'Male')  m
            FROM gender
            GROUP BY title
            HAVING sum(gender = 'Female') > sum(gender = 'Male')
            ORDER BY title ASC
        '''
        self.cur.execute(query0)
        self.cur.execute(query1)
        self.cur.execute(query2)
        all_rows = self.cur.fetchall()
        return all_rows

    def q8(self):
        query = '''
    	SELECT a.fname, a.lname, COUNT(DISTINCT md.did) AS num_directors
    	FROM Actors AS a
    	INNER JOIN Cast AS c ON a.aid = c.aid
    	INNER JOIN Movie_Director AS md ON c.mid = md.mid
    	GROUP BY a.aid
    	HAVING num_directors >= 7
    	AND a.aid IN (SELECT a2.aid
    	              FROM Actors AS a2
    	              INNER JOIN Cast AS c2 ON c2.aid = a2.aid
    	              INNER JOIN Movies AS m2 ON m2.mid = c2.mid
    	              GROUP BY a2.aid
                      HAVING COUNT(DISTINCT m2.mid) >=7 )
        '''
        self.cur.execute(query)

        all_rows = self.cur.fetchall()
        return all_rows


    def q9(self):

        query1 = '''
        	SELECT a.fname, a.lname, COUNT(m.mid) AS num_movies
        	FROM Actors AS a
        	INNER JOIN Cast AS c ON a.aid = c.aid
        	INNER JOIN Movies AS m ON c.mid = m.mid
        	WHERE a.fname LIKE 'D%'
        	    AND m.mid IN (SELECT m2.mid
        	                  FROM Actors AS a2
        	                  INNER JOIN Cast AS c2 ON a2.aid = c2.aid
        	                  INNER JOIN Movies AS m2 ON c2.mid = m2.mid
        	                  WHERE m.year = (SELECT MIN(m3.year)
        	                                  FROM Actors AS a3
        	                                  INNER JOIN Cast AS c3 ON a3.aid = c3.aid
        	                                  INNER JOIN Movies AS m3 ON c3.mid = m3.mid
        	                                  WHERE a3.aid = a.aid))
        	GROUP BY a.aid
        	ORDER BY num_movies DESC
        '''

        self.cur.execute(query1)
        all_rows = self.cur.fetchall()
        return all_rows

    def q10(self):
        query = '''
        SELECT a.lname, m.title
        FROM Actors a
        INNER JOIN CAST c ON a.aid = c.aid
        INNER JOIN MOVIES m ON c.mid = m.mid
        INNER JOIN Movie_Director md ON c.mid = md.mid
        INNER JOIN Directors d ON md.did = d.did
        WHERE a.lname = d.lname
        AND a.fname != d.fname
        ORDER BY a.lname

        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q11(self):
        query0 = ''' DROP VIEW IF EXISTS kb '''
        query1 = '''
        CREATE VIEW kb as
        SELECT aid
        FROM Cast
        NATURAL JOIN Actors
        WHERE mid in (SELECT m.mid
                       FROM Actors a, Cast c, Movies m
                       WHERE a.aid = c.aid
                       AND c.mid = m.mid
                       AND a.fname = "Kevin"
                       AND a.lname = "Bacon")
        '''
        query2 = '''
        SELECT fname, lname
        FROM Actors
        NATURAL JOIN Cast
        WHERE aid NOT IN kb and mid in (SELECT mid
                                        FROM Cast
                                        WHERE aid in kb)
        ORDER BY lname, fname
        '''
        self.cur.execute(query0)
        self.cur.execute(query1)
        self.cur.execute(query2)
        all_rows = self.cur.fetchall()
        return all_rows

    def q12(self):
        query = '''
        SELECT fname, lname, COUNT(*) as c, AVG(rank) as avgrank
        FROM Actors a, Cast c, Movies m
        WHERE a.aid = c.aid
        AND c.mid = m.mid
        GROUP BY fname, lname
        ORDER BY avgrank DESC
        LIMIT 20

        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

if __name__ == "__main__":
    task = Movie_auto("cs1656-public.db")
    rows = task.q0()
    print(rows)
    print()
    rows = task.q1()
    print(rows)
    print()
    rows = task.q2()
    print(rows)
    print()
    rows = task.q3()
    print(rows)
    print()
    rows = task.q4()
    print(rows)
    print()
    rows = task.q5()
    print(rows)
    print()
    rows = task.q6()
    print(rows)
    print()
    rows = task.q7()
    print(rows)
    print()
    rows = task.q8()
    print(rows)
    print()
    rows = task.q9()
    print(rows)
    print()
    rows = task.q10()
    print(rows)
    print()
    rows = task.q11()
    print(rows)
    print()
    rows = task.q12()
    print(rows)
    print()
