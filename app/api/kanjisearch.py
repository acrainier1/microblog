""" 
    =============================================
    =============================================
    <<<<<<<<<<<<<<<<<< README >>>>>>>>>>>>>>>>>>>
    =============================================
    =============================================

            TABLE OF CONTENTS           Line No.

    - 1 -   PROGRAM STRUCTURE           25
    - 2 -   IMPORTS & SETUP             100
    - 3 -   FLASK ROUTES                125
    - 4 -   SQL QUERIES                 350
    - 5 -   HELPER FUNCTIONS            475










    =============================================
    <<<<<<<<<< - 1 - PROGRAM STRUCTURE >>>>>>>>>>
    =============================================


    (1) MAIN SEARCH FEATURE
        Flask Route:        @bp.route('/getsearch/<search_term>')
                            getsearch(search_term)

        SQL Query:          main_search_query(search_term, columns1)
                            main_search_query(kunyomi, columns2)
                            derivative_kanji_query(search_term)

        Data Structuring:   nest_search_result(result)


    (2) SUGGESTIONS BOX
        Flask Route:        @bp.route('/getsuggestions/<search_term>')
                            getsuggestions(search_term)

        SQL Query:          suggestions_query(search_term, columns1)
                            suggestions_query(kunyomi, columns2)

        Data Structuring:   nest_search_result(result)


    (3) SEARCH BY RADICAL
        Flask Route:        @bp.route('/getbyradicals/<search_term>')
                            getsearch(search_term)

        SQL Query:          derivative_kanji_query(search_term)

        Data Structuring:   nest_search_result(result)


    (4) KANJI DATA CARD
        Flask Route:        @bp.route('/getkanji/<column>/<search_term>')
                            getkanji(column, search_term)

        SQL Query:          First query is defined within getkanji() function
                            add_bushu(radicals)

        Data Structuring:   nest_kanji_result(result)


    (5) KANJI DATA SET
        Flask Route:        @bp.route('/getkanjiset/<column>/<search_term>')
                            getkanjiset(column, search_term)

        SQL Query:          First query is defined within getkanji() function
                            add_bushu(radicals)

        Data Structuring:   nest_kanji_result(result)

"""




















"""
    =============================================
    <<<<<<<<<<< - 2 - IMPORTS & SETUP >>>>>>>>>>>
    =============================================
"""
# General
import copy
import os
import time
import psycopg2
import sqlite3
from config import Config
# Flask
from flask import jsonify, request
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import select
# App
from app import db
from app.models import User, KanjiData
from app.api import bp
from app.api.errors import bad_request




@bp.route('/search/<search_term>', methods=['GET'])
def search(search_term):
    """ DESCRIPTION
        Main search feature from search bar input. It finds the searchTerm kanji 
        and returns list of all derivatives broken down by derivation depth level.
        The string search term term can be one of many things: an order number, 
        a kanji, a meaning, a radical, or a reading.
        The search function has three parts: (1) ORDER # and ONYOMI SEARCH, 
        (2) KUNYOMI SEARCH, (3) KANJI AND DERIVATIVES SEARCH.

        PARAMETERS searchTerm: string

        RETURNS search_data: array
        DATA STRUCTURE of search_data:
            Initialized as an object to prevent duplicates when new entries are
            added. Ultimately, returned as an array.

        KEY: integer : VALUE: array
            { 
                Order: [Order #, Kanji, [...meanings], [...radicals], Heading/Depth], 
                Order: [...], 
                ...
            }
        Example:
            { 
                57Onyomi_Reading1: [[51], ['大'], ['big', '', ''], 'Onyomi']
                43: [43, '由', ['reason','',''], ['bar','field','',''], 3]
            }

        If there is data found, returned as an array or arrays
            [
                [Order #, Kanji, [...meanings], [...radicals], Heading/Depth], 
                [...],
                ...
            ]
        Example:
            [
                [[51], ['大'], ['big', '', ''], 'Onyomi']
                [43, '由', ['reason','',''], ['bar','field','',''], 3]
            ]

        If there is no data found, returned as an array with boiler plate
    """
    print("search_term:", search_term, "@bp.route('/search/<search_term>', methods=['GET'])")

    NO_DATA = jsonify([ ['', '', [], [], 'NO_DATA'] ])
    search_term = scrub_chars(search_term)
    # search_term = search_term.strip()
    

    """ (1) ORDER NUMBER & ONYOMI SEARCH
        Searches only a few columns because special cases and extra
        functionality are taken care of by search queries below 
    """
    columns1 = ["Onyomi_Reading1", "Onyomi_Reading2"]
    search_data = main_search_query(search_term, columns1)


    # """ (2) KUNYOMI SEARCH
    #     Searches for kunyomi with period "." between each letter because 
    #     Kunyomi_Reading1 and Kunyomi_Reading2 columns sometimes have a
    #     "." in the entry string in an unpredictable place. Thus, checking 
    #     all possible occurences of "." and without it is necessary to get
    #     result.
    # """
    # columns2 = ["Kunyomi_Reading1", "Kunyomi_Reading2"]
    # kunyomis = punctuate_kunyomi(search_term)
    # for kunyomi in kunyomis:
    #     search_data.update(main_search_query(kunyomi, columns2))


    """ (3) KANJI AND DERIVATIVES SEARCH
        Searches for all derivative kanji of search term 
    """
    search_data.update(derivative_kanji_query(search_term))

    if search_data:
        return jsonify(list(search_data.values()))
    return NO_DATA


@bp.route('/byradicals/<delimiter>/<search_term>', methods=['GET'])
def byradicals(delimiter, search_term):
    """ DESCRIPTION
        Searches only a few columns because special cases and extra
        functionality are taken care of by search queries below
    """

    print(search_term, "@bp.route('/byradicals/<delimiter>/<search_term>', methods=['GET'])")
    # columns = ["[Order1]",
    #            "[Type1]",
    #            "[Radical1]", "[Radical2]", "[Radical3]", "[Radical4]",
    #            "[Onyomi Reading1]", "[Onyomi Reading2]",
    #            "[Kunyomi Reading1]", "[Kunyomi Reading2]"]

    previous_delimiter = -1
    radicals = []
    for idx, char in enumerate(search_term):
        if char == delimiter:
            radicals.append(search_term[previous_delimiter + 1:idx])
            previous_delimiter = idx

    """ Searches for all derivative Kanji of search term 
        and finds the INTERSECTION of query results """
    intersection_of_results = derivative_kanji_query(radicals[0])
    for radical in radicals[1:]:
        nested_query_results1 = copy.deepcopy(intersection_of_results)
        nested_query_results2 = derivative_kanji_query(radical)
        intersection_of_results = {}
        for k,v in nested_query_results2.items():
            if k in nested_query_results1.keys():
                intersection_of_results[k] = v

    if intersection_of_results:
        return jsonify(intersection_of_results)
    return jsonify({"NO_KEYS":["", "", ["", "", ""], "NO_DATA"]})


@bp.route('/kanji/<search_term>', methods=['GET'])
def kanji(search_term):
    """ DESCRIPTION
        Primary search function. getKanjiData takes a search term 
        and returns the flashcard data

        PARAMETERS: search_term: string

        RETURNS kanjiData: array
        DATA STRUCTURE of kanjiData:
            [
                [Order], 
                [Kanji],
                [Meanings], 
                [Bushu],
                [Radicals], 
                [Onyomi],
                [Kunyomi], 
                [Mnemonic],
                [Notes]
            ]
        Example:
            [
                [1], 
                ["\u4e00"], 
                ["Kanji"], 
                ["one"], 
                [], 
                ["horizontal line"], 
                ["ICHI","ITSU"], 
                ["hito.tsu"],
                ["One.m is just a line.r..."], 
                [""] 
            ]
    """
    """ 
        To test CJK characters with curl in terminal use:
        search_term = search_term.encode('iso-8859-1').decode('utf8')
    """

    print("search_term:", search_term, "@bp.route('/kanji/<search_term>', methods=['GET'])")
    result = KanjiData.query.filter_by(Order=int(search_term)).first()
    if result:
        nested = nest_kanji_result(result)
        nested[4] = add_bushu(nested[5])
    if nested:
        return jsonify(nested)
    return jsonify([[0], [], [], ["NO_KANJI_DATA"], [], [], [], [], [], []])


@bp.route('/kanjiset/<int:search_term>', methods=['GET'])
def kanjiset(search_term):
    print("search_term:", search_term, "@bp.route('/kanjiset/<int:search_term>', methods=['GET'])")

    results = KanjiData.query.filter(
        KanjiData.Order.between(search_term, search_term+99))
    nested_results = []
    if results:
        for result in results:
            nested = nest_kanji_result(result)
            nested[4] = add_bushu(nested[5])
            nested_results.append(nested)
    if nested_results:
        return jsonify(nested_results)
    return jsonify([])


@bp.route('/test/<search_term>', methods=['GET'])
def testroute(search_term):
    print("search_term:", search_term, "@bp.route('/test/<search_term>', methods=['GET'])")
    test_data = [
        [1, '由', ['a','',''], ['bar','field','',''], 2],
        [2, '由', ['b','',''], ['bar','field','',''], 3],
        [3, '由', ['c','',''], ['bar','field','',''], 3],
        [4, '由', ['d','',''], ['bar','field','',''], 3]
    ]
    print("test_data\n", test_data)
    return jsonify(test_data)
    return jsonify({"Kanji" : test_data.Kanji})






"""
    =============================================
    <<<<<<<<<<<< - 4 - SQL QUERIES  >>>>>>>>>>>>>
    =============================================
"""
def main_search_query(search_term, columns):
    """ This query searches based on columns below that DO NOT
        require deep searches of kanji derived from search term.
    """
    # results = KanjiData.query.filter(getattr(KanjiData, column) == search_term)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        collocation = "case_insensitive"
    else:
        conn = sqlite3.connect( "/home/acanizales1/microblog/app.db")
        collocation = "NOCASE"
    cursor = conn.cursor()

    search_data = {}
    if search_term.isnumeric():
        query_order = f"""
            SELECT *
                FROM kanji_data
                WHERE "Order"={search_term}
        """
        res = cursor.execute(query_order)
        result = cursor.fetchone()
        if result:
            nested = nest_query_result(result)
            nested.append("Order")
            search_data[str(result[0]) + "Order"] = nested
            # concatenating Order # and column preserves this result if
            # a duplicate is found later in the derivative search
            # search results should display it twice if found as both 
            # an On/Kunyomi reading and a derivative kanji
    else:
        for column in columns:
            query_columns = f"""
                SELECT *
                    FROM kanji_data
                    WHERE "{column}"='{search_term}'
                    COLLATE {collocation}
            """
            print(query_columns)
            res = cursor.execute(query_columns)
            results = cursor.fetchall()
            if results:
                for result in results:
                    nested = nest_query_result(result)
                    nested.append(column[:-9]) # only 'Onyomi' or 'Kunyomi' part of column name
                    search_data[str(result[0]) + column] = nested
    cursor.close()
    return search_data


def derivative_kanji_query(search_term):

    # start = time.time()
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        print("===== YES POSTGRES DATABASE_URL:", DATABASE_URL)
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        collocation = "case_insensitive"
    else:
        print("===== NO POSTGRES DATABASE_URL:", DATABASE_URL)
        conn = sqlite3.connect( "/home/acanizales1/microblog/app.db")
        collocation = "NOCASE"
    cursor = conn.cursor()
    
    """ This searches based on columns below that DO require 
        deep searches of kanji derived from search term
    """
    nested_results = {}
    for column in ["Kanji", "Meaning1", "Meaning2", "Meaning3"]:
        kanji_meaning_query = select([KanjiData]).where(getattr(KanjiData, column) == search_term)
        result = db.session.execute(kanji_meaning_query).fetchone()
        if result:
            nested = nest_search_result(result)
            nested_results[result.Order] = nested

            """ `depth` variable provides derivation level. Initialize at 0 
                because the kanji from search_term is at the zeroeth. 
                From it, the while loop below will search for its descendants
                For example: 一 0 > 三 1 > 王 2 > 玉 3 > 国 4 etc.
                Append `depth` after deep copy so deep copy does not have a
                depth in case duplicates are found later.
            """
            depth = 0
            deep_copy = copy.deepcopy(nested_results)
            for k,v in nested_results.items():
                v.append(depth)
            
            loop = True
            while loop:
                depth += 1
                loop = False # if loop doesn't update to True, while loop stops
                temp = {}
                for key, value in deep_copy.items():
                    # value[2] is list of Meanings
                    for meaning in value[2]:
                        # because if meaning == empty string, infinite while loop
                        if meaning:
                            # Searches all kanji again effectively making this recursive
                            # print("meaning===\n", meaning) # to test for infinite loops
                            for radical in ["Radical1", "Radical2", "Radical3", "Radical4"]:                                                               
                                query_derivatives = f"""
                                    SELECT * 
                                        FROM kanji_data 
                                        WHERE "{radical}"='{meaning.strip()}'
                                        COLLATE {collocation}
                                """
                                res = cursor.execute(query_derivatives)
                                result = cursor.fetchall()
                                if results:
                                    for result in results:
                                        nested = nest_query_result(result)
                                        temp[result[0]] = nested
                                        temp[result[0]].append(depth)
                                    loop = True
                deep_copy = copy.deepcopy(temp)
                nested_results.update(temp)
            break # if column match found
    cursor.close()
    # end = time.time()
    # print("TIME TO EXCECUTE:", str(end - start))
    return nested_results


def suggestions_query(search_term, columns):
    with sqlite3.connect(DBPATH) as conn:
        cursor = conn.cursor()
        nested_results = {}
        search_term_wildcard = "%" + search_term.strip() + "%"
        for numbered_column in columns:
            column = numbered_column[1:]
            SQL = f""" SELECT * FROM [kanjidata] 
                       WHERE {column} 
                       LIKE ? COLLATE NOCASE """
            results = cursor.execute(SQL, (search_term_wildcard,)).fetchall()
            if results:
                for result in results:
                    nested = nest_search_result(result)
                    nested_results[str(result[0])+column] = nested
                    nested_results[str(result[0])+column].append(column[1:-2])
                    COLUMN_SQL = f""" SELECT {column} FROM [kanjidata] 
                                      WHERE {column} 
                                      LIKE ? COLLATE NOCASE 
                                      AND [Order1]={result[0]} COLLATE NOCASE """
                    """ partial_match is needed because """
                    partial_match = cursor.execute(COLUMN_SQL, (search_term_wildcard,)).fetchall()
                    print("result[4]", result[4], "\n")
                    print("partial_match", partial_match, "\n")
                    nested_results[str(result[0])+column].append(partial_match[0][0])
                    nested_results[str(result[0])+column].append(numbered_column[0])
    print("NQR", nested_results, "\n")
    return nested_results


def add_bushu(radicals):
    """ This extracts kanji version of a radical.
        For example, for "tree" it finds the kanji for its 
        radicals, "big" and "bar", and returns ["大", "|"]
    """
    bushus = []
    for radical in radicals:
        bushu1 = KanjiData.query.filter_by(Meaning1=radical).first()
        bushu2 = KanjiData.query.filter_by(Meaning2=radical).first()
        bushu3 = KanjiData.query.filter_by(Meaning3=radical).first()
        for bushu in [bushu1, bushu2, bushu3]:
            if bushu:
                bushus.append(bushu.Kanji)
    return bushus






"""
    =============================================
    <<<<<<<<<< - 5 - HELPER FUNCTIONS  >>>>>>>>>>
    =============================================
"""
def nest_query_result(result):
    """ DESCRIPTION
        This is the search display data. nest_search_result appends 
        the "columns" of json response as list within a larger list.
        This is for use with RAW SQL queries returned as tuples.
    """
    nested_result = [
        result[0],                          # ORDER
        result[2],                          # KANJI
        [result[4], result[5], result[6]]   # MEANINGS
    ]
    return nested_result


def nest_search_result(result):
    """ DESCRIPTION
        This is the search display data. nest_search_result appends 
        the "columns" of json response as list within a larger list.
        This for use with ORM queries returned as objects.
    """
    r = result
    nested_result = []
    nested_result.append(r.Order)
    nested_result.append(r.Kanji)
    nested_result.append([r.Meaning1, r.Meaning2, r.Meaning3])
    return nested_result


def nest_kanji_result(result):
    """ This is the kanji card's data. nest_kanji_result appends the
        "columns" of json response as list within a larger list. 
        Some responses are semantically related so multiple columns 
        will be further nested into a list.
    """
    r = result
    nested_result = []
    # row[0:2] - Appends ORDER, KANJI, and TYPE
    nested_result.append([r.Order])
    nested_result.append([r.Kanji])
    nested_result.append([r.Type])

    # row[3] - Appends nested list of MEANINGS and checks for empty columns
    meanings = list(filter(None, [r.Meaning1, r.Meaning2, r.Meaning3]))
    nested_result.append(meanings)

    # row[4] - Empty list for BUSHU added in calling function
    nested_result.append([])

    # row[5] - nested list of RADICALS and checks for empty columns
    radicals = list(filter(None, [r.Radical1, r.Radical2, r.Radical3, r.Radical4]))
    nested_result.append(radicals)

    # row[6] - Appends nested list of ONYOMI and checks for empty columns
    onyomi = list(filter(None, [r.Onyomi_Reading1, r.Onyomi_Reading2]))
    nested_result.append(onyomi)

    # row[7] - Appends nested list of KUNYOMI and checks for empty columns
    kunyomi = list(filter(None, [r.Kunyomi_Reading1, r.Kunyomi_Reading2]))
    nested_result.append(kunyomi)

    # row[8:9] - Appends MNEMONIC and NOTES
    nested_result.append([r.Mnemonic])
    nested_result.append([r.Notes])

    return nested_result


def punctuate_kunyomi(search_term):
    """ DESCRIPTION
        Searches for kunyomi with period "." between each letter because 
        Kunyomi_Reading1 and Kunyomi_Reading2 columns sometimes have a
        "." in the entry string in an unpredictable place. Thus, checking 
        all possible occurences of "." and without it is necessary to get
        result.
    """
    if '.' in search_term:
        # strip out "."
        index = search_term.find(".")
        search_term = search_term[:index] + search_term[index + 1:]
    kunyomis = [search_term[:i] + "." + search_term[i:] for i in range(1, len(search_term))]
    kunyomis.append(search_term)
    return kunyomis


def scrub_chars(search_term):
    search_term = search_term.strip()
    disallowed_chars = [
        # '"', "'", "\",
        "`", "~", "!", "@", "%", "%", "^", "&", "(", ")", "_", "+", "=", 
        "{", "}", "[", "]", "|", "/", ":", ";", "<", ">", ",", "?"
    ]
    for char in disallowed_chars:
        if char in search_term:
            return "DUMMY_SEARCH_TEXT"
    return search_term
























"""
    =============================================
    <<<<<<<<<< - 6 - DEPRECATED CODE  >>>>>>>>>>>
    =============================================
"""

# from main_search_query
# if column[-1].isnumeric():
#     nested.append(column[:-9])
# else:
#     nested.append(column)