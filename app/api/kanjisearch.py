""" 
    =============================================
    =============================================
    <<<<<<<<< README: TABLE OF CONTENTS >>>>>>>>>
    =============================================
    =============================================


    - 1 -  PROGRAM STRUCTURE
    - 2 -  IMPORTS & SETUP
    - 3 -  FLASK ROUTES
    - 4 -  SQL QUERIES
    - 5 -  DATA STRUCTURING












    =============================================
    <<<<<<<<<< - 1 - PROGRAM STRUCTURE >>>>>>>>>>
    =============================================


    (1) MAIN SEARCH FEATURE
        Flask Route:        @bp.route('/getsearch/<search_term>')
                            getsearch(search_term)

        SQL Query:          sql_query1(search_term, columns1)
                            sql_query1(kunyomi, columns2)
                            sql_query2(search_term)

        Data Structuring:   nest_search_result(result)


    (2) SUGGESTIONS BOX
        Flask Route:        @bp.route('/getsuggestions/<search_term>')
                            getsuggestions(search_term)

        SQL Query:          sql_query3(search_term, columns1)
                            sql_query3(kunyomi, columns2)

        Data Structuring:   nest_search_result(result)


    (3) SEARCH BY RADICAL
        Flask Route:        @bp.route('/getbyradicals/<search_term>')
                            getsearch(search_term)

        SQL Query:          sql_query2(search_term)

        Data Structuring:   nest_search_result(result)


    (4) KANJI DATA CARD
        Flask Route:        @bp.route('/getkanji/<column>/<search_term>')
                            getkanji(column, search_term)

        SQL Query:          First query is defined within getkanji() function
                            sql_query4(radicals)

        Data Structuring:   nest_kanji_result(result)


    (5) KANJI DATA SET
        Flask Route:        @bp.route('/getkanjiset/<column>/<search_term>')
                            getkanjiset(column, search_term)

        SQL Query:          First query is defined within getkanji() function
                            sql_query4(radicals)

        Data Structuring:   nest_kanji_result(result)


    (6) CONTACT FORM DATA
        Flask Route:        @bp.route('/postcontactform/<subject>/<name>/
                                        <email>/<message>/<section>/<card>')
                            postcontactform(subject, name, email, message, page, card)

        SQL Query:         Query is defined within function

"""












"""
    =============================================
    <<<<<<<<<<< - 2 - IMPORTS & SETUP >>>>>>>>>>>
    =============================================
"""
from flask import jsonify, request
from app import db
from app.models import User, KanjiData
from app.api import bp
from app.api.errors import bad_request




@bp.route('/search/<search_term>', methods=['GET'])
def search(search_term):


    """ Searches only a few columns because special cases and extra
        functionality are taken care of by search queries below 
        In search resutls will display: Match `columns1[i]` of
    """
    columns1 = ["[Order1]",
                "[Type1]",
                "[Onyomi Reading1]", "[Onyomi Reading2]"]
    nested_query_results = sql_query1(search_term, columns1)


    """ Searches for kunyomi with period "." between each letter because 
        Kunyomi Reading1 and Kunyomi Reading2 columns sometimes have
        a "." in the entry string in an unpredictable place. Therefore, 
        checking all possible "." occurences is necessary to get result
    """
    columns2 = ["[Kunyomi Reading1]", "[Kunyomi Reading2]"]
    period_kunyomis = [search_term[:i] + "." + search_term[i:] for i in range(1, len(search_term))]
    period_kunyomis.append(search_term)
    for kunyomi in period_kunyomis:
        nested_query_results.update(sql_query1(kunyomi, columns2))

    """ Searches for all derivative kanji of search term """
    nested_query_results.update(sql_query2(search_term))
    if nested_query_results:
        return jsonify(nested_query_results)
    return jsonify({"NO_KEYS":["", "", ["", "", ""], "NO_DATA"]})


@bp.route('/suggestions/<search_term>', methods=['GET'])
def suggestions(search_term):
    """ Searches all columns except Mnemonic sentence and Notes """
    columns1 = ["0[Order1]", "0[Kanji1]",
                "1[Meaning1]", "1[Meaning2]", "1[Meaning3]",
                "2[Radical1]", "2[Radical2]", "2[Radical3]", "2[Radical4]",
                "3[Onyomi Reading1]", "3[Onyomi Reading2]"]
    nested_query_results = sql_query3(search_term, columns1)

    """ Searches for kunyomi with period "." between each letter because 
        Kunyomi Reading1 and Kunyomi Reading2 columns sometimes have
        a "." in the entry string in an unpredictable place. Therefore, 
        checking all possible "." occurences is necessary to get result """
    columns2 = ["4[Kunyomi Reading1]", "4[Kunyomi Reading2]"]
    period_kunyomis = [search_term[:i] + "." + search_term[i:] for i in range(1, len(search_term))]
    period_kunyomis.append(search_term)
    for kunyomi in period_kunyomis:
        nested_query_results.update(sql_query3(kunyomi, columns2))

    if nested_query_results:
        return jsonify(nested_query_results)
    return jsonify({"NO_KEYS":["", "", ["", "", ""], ""]})


@bp.route('/byradicals/<delimiter>/<search_term>', methods=['GET'])
def byradicals(delimiter, search_term):
    """ Searches only a few columns because special cases and extra
        functionality are taken care of by search queries below """
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
    intersection_of_results = sql_query2(radicals[0])
    for radical in radicals[1:]:
        nested_query_results1 = copy.deepcopy(intersection_of_results)
        nested_query_results2 = sql_query2(radical)
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
    result = KanjiData.query.filter_by(Order=int(search_term)).first()
    print("=== result ===\n", result.Kanji)
    if result:
        nested = nest_kanji_result(result)
        nested[4] = sql_query4(nested[5])
    print("nested\n",nested)
    if nested:
        return jsonify(nested)
    return jsonify([[0], [], [], ["NO_KANJI_DATA"], [], [], [], [], [], []])


@bp.route('/kanjiset/<search_term>', methods=['GET'])
def kanjiset(search_term):
    search_term = int(search_term)
    with sqlite3.connect(DBPATH) as conn:
        cursor = conn.cursor()
        nested_results_query = {}
        SQL = f""" SELECT * FROM [kanjidata]
                    WHERE [Order1]
                    BETWEEN {search_term} AND {search_term + 99} """
        results = cursor.execute(SQL).fetchall()
        if results:
            for result in results:
                nested = nest_kanji_result(result)
                nested.append(sql_query4(nested[4]))
                nested_results_query[str(result[0])] = nested
        if nested_results_query:
            return jsonify(nested_results_query)
        return Response({"NO_KEYS":["NO_KANJI_DATA"]}, content_type="application/json; charset=utf-8")


@bp.route('/test/<search_term>', methods=['GET'])
def testroute(search_term):
    print(f"== SEARCH API MADE IT! search_term: {search_term} ==")
    test_data = KanjiData.query.filter_by(Order=200).first()
    # test_data = KanjiData.query.all()[55]
    # row = test_data[2]
    print("test_data\n", test_data)
    # test_data = [
    #     [44, '由', ['a','',''], ['bar','field','',''], 2],
    #     [45, '由', ['b','',''], ['bar','field','',''], 3],
    #     [46, '由', ['c','',''], ['bar','field','',''], 3],
    #     [47, '由', ['d','',''], ['bar','field','',''], 3]
    # ]
    # return jsonify(test_data)
    return jsonify({"Kanji" : test_data.Kanji})


"""
    =============================================
    <<<<<<<<<<<< - 4 - SQL QUERIES  >>>>>>>>>>>>>
    =============================================
"""

def sql_query1(search_term, columns):
    """ This query1 searches based on columns below that
        DO NOT require deep searches of kanji derived 
        from search term """
    """ search_term = search_term.encode('iso-8859-1').decode('utf8')
        is to test CJK characters with curl in terminal """
    with sqlite3.connect(DBPATH) as conn:
        cursor = conn.cursor()
        nested_query_results = {}
        for column in columns:
            SQL = f"SELECT * FROM [kanjidata] WHERE {column}=? COLLATE NOCASE "
            results = cursor.execute(SQL, (search_term.strip(),)).fetchall()
            if results:
                for result in results:
                    nested = nest_search_result(result)
                    nested_query_results[str(result[0])+column] = nested
                    nested_query_results[str(result[0])+column].append(column[1:-2])
    return nested_query_results


def sql_query2(search_term):
    """ This sql query2 searches based on columns below 
        that DO require deep searches of kanji derived 
        from search term """
    with sqlite3.connect(DBPATH) as conn:
        cursor = conn.cursor()
        nested_results_query2 = {}
        for column in ["[Kanji1]", "[Meaning1]", "[Meaning2]", "[Meaning3]"]:
            SQL = f"SELECT * FROM [kanjidata] WHERE {column}=? COLLATE NOCASE "
            results = cursor.execute(SQL, (search_term.strip(),)).fetchall()
            if results:
                for result in results:
                    nested = nest_search_result(result)
                    nested_results_query2[str(result[0])] = nested
                """ `depth` variable provides derivation level. Initialize at 0 
                    because the kanji from search_term is at the zeroeth. 
                    From it, while loop below will search for its descendants
                    For example: 一 0 > 三 1 > 王 2 > 玉 3 > 国 4 etc. """
                depth = 0
                deep_copy = copy.deepcopy(nested_results_query2)
                for k,v in nested_results_query2.items():
                    v.append(depth)

                c = 1
                while c > 0 or depth < 25:
                    depth += 1
                    c = 0
                    temp = {}
                    for key, value in deep_copy.items(): # value[2] is list of Meanings
                        for meaning in value[2]:
                            # because if meaning == empty string, infinite while loop
                            if meaning:
                                # Searches all kanji again effectively making this recursive
                                # print("meaning===\n", meaning) # use this to test for infinite loops
                                for radical in ["[Radical1]", "[Radical2]", "[Radical3]", "[Radical4]"]:
                                    SQL = f"""SELECT * FROM [kanjidata] 
                                                WHERE {radical}=? COLLATE NOCASE """
                                    results = cursor.execute(SQL, (meaning.strip(),)).fetchall()
                                    if results:
                                        for result in results:
                                            nested = nest_search_result(result)
                                            temp[str(result[0])] = nested
                                            temp[str(result[0])].append(depth)
                                        c += 1 # c == 0 is break condition for loop or recursion
                    deep_copy = copy.deepcopy(temp)
                    nested_results_query2.update(temp)
    return nested_results_query2


def sql_query3(search_term, columns):
    with sqlite3.connect(DBPATH) as conn:
        cursor = conn.cursor()
        nested_query_results = {}
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
                    nested_query_results[str(result[0])+column] = nested
                    nested_query_results[str(result[0])+column].append(column[1:-2])
                    COLUMN_SQL = f""" SELECT {column} FROM [kanjidata] 
                                      WHERE {column} 
                                      LIKE ? COLLATE NOCASE 
                                      AND [Order1]={result[0]} COLLATE NOCASE """
                    """ partial_match is needed because """
                    partial_match = cursor.execute(COLUMN_SQL, (search_term_wildcard,)).fetchall()
                    print("result[4]", result[4], "\n")
                    print("partial_match", partial_match, "\n")
                    nested_query_results[str(result[0])+column].append(partial_match[0][0])
                    nested_query_results[str(result[0])+column].append(numbered_column[0])
    print("NQR", nested_query_results, "\n")
    return nested_query_results


def sql_query4(radicals):
    """ This extracts kanji version of radical.
        For example, "tree" it finds the kanji for its 
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
    <<<<<<<<<< - 5 - DATA STRUCTURING  >>>>>>>>>>
    =============================================
"""

def nest_search_result(result):
    """ This is the search display data. nest_search_result appends 
        the "columns" of json response as list within a larger list. """
    nested_result = []
    # Appends ORDER, KANJI, and MEANING1
    nested_result.append(result[0])
    nested_result.append(result[2])
    nested_result.append([result[4], result[5], result[6]])

    return nested_result


def nest_kanji_result(result):
    """ This is the kanji card's data. nest_kanji_result appends the
        "columns" of json response as list within a larger list. 
        Some responses are semantically related so multiple columns 
        will be further nested into a list
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



    # # row[0:2] - Appends ORDER, KANJI, and TYPE
    # nested_result.append([result[0]])
    # nested_result.append([result[2]])
    # nested_result.append([result[3]])

    # # row[3] - Appends nested list of MEANINGS and checks for empty columns
    # meanings = list(filter(None, result[4:7]))
    # nested_result.append(meanings)

    # # row[4] - Empty list for BUSHU added in calling function
    # nested_result.append([])

    # # row[5] - nested list of RADICALS and checks for empty columns
    # radicals = list(filter(None, result[7:11]))
    # nested_result.append(radicals)

    # # row[6] - Appends nested list of ONYOMI and checks for empty columns
    # onyomi = list(filter(None, result[11:13]))
    # nested_result.append(onyomi)

    # # row[7] - Appends nested list of KUNYOMI and checks for empty columns
    # kunyomi = list(filter(None, result[13:15]))
    # nested_result.append(kunyomi)

    # # row[8:9] - Appends MNEMONIC and NOTES
    # nested_result.append([result[15]])
    # nested_result.append([result[16]])

    # return nested_result



if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True)
    # app.run(host='192.168.1.3',debug=True)






