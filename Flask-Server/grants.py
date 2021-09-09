import pymysql
from db_output_parsers import *
from temp import *

def searchStudentEncouragementBonus(additionalIncomeLimit, householdSize):
    incomeLimit = 150000
    if additionalIncomeLimit != None:
        incomeLimit = min(additionalIncomeLimit, incomeLimit)
    conn = pymysql.connect(
        host=SQL_HOST,
        db=SQL_DB,
        user=SQL_USER,
        password=SQL_PASSWORD
    )
    cursor = conn.cursor()
    if householdSize == None:
        cursor.execute("SELECT H.HouseID, H.HousingType, M.Name, M.Gender, M.MaritalStatus, M.Spouse, M.OccupationType, M.AnnualIncome, M.DOB FROM \
            HouseHold as H, \
            MemberLivesIn AS M, \
            (SELECT DISTINCT (M.HouseID) FROM MemberLivesIn AS M WHERE M.OccupationType = 'Student' AND TIMESTAMPDIFF(YEAR, M.DOB, NOW()) < 16) AS AGE_FILTER, \
            (SELECT M.HouseID FROM MemberLivesIn AS M GROUP BY M.HouseID HAVING SUM(M.AnnualIncome) < %s) AS INCOME_FILTER \
            WHERE H.HouseID = M.HouseID AND H.HouseID = AGE_FILTER.HouseID AND H.HouseID = INCOME_FILTER.HouseID ORDER BY HouseID ASC", 
            (incomeLimit))
    else:
        cursor.execute("SELECT H.HouseID, H.HousingType, M.Name, M.Gender, M.MaritalStatus, M.Spouse, M.OccupationType, M.AnnualIncome, M.DOB FROM \
            HouseHold as H, \
            MemberLivesIn AS M, \
            (SELECT DISTINCT (M.HouseID) FROM MemberLivesIn AS M WHERE M.OccupationType = 'Student' AND TIMESTAMPDIFF(YEAR, M.DOB, NOW()) < 16) AS AGE_FILTER, \
            (SELECT M.HouseID FROM MemberLivesIn AS M GROUP BY M.HouseID HAVING SUM(M.AnnualIncome) < %s) AS INCOME_FILTER, \
            (SELECT M.HouseID FROM MemberLivesIn AS M GROUP BY M.HouseID HAVING COUNT(M.Name) <= %s) AS NUM_MEMBER_FILTER \
            WHERE H.HouseID = M.HouseID AND H.HouseID = AGE_FILTER.HouseID AND H.HouseID = INCOME_FILTER.HouseID AND H.HouseID = NUM_MEMBER_FILTER.HouseID \
            ORDER BY HouseID ASC", 
            (incomeLimit, householdSize))
    housesInformation = cursor.fetchall()
    output = parse_household_with_member_information(housesInformation)
    return output

def searchYOLOGSTGrant(additionalIncomeLimit, householdSize):
    incomeLimit = 100000
    if additionalIncomeLimit != None:
        incomeLimit = min(additionalIncomeLimit, incomeLimit)
    conn = pymysql.connect(
        host=SQL_HOST,
        db=SQL_DB,
        user=SQL_USER,
        password=SQL_PASSWORD
    )
    cursor = conn.cursor()
    if householdSize == None:
        cursor.execute("SELECT H.HouseID, H.HousingType FROM \
            HouseHold as H, \
            (SELECT M.HouseID FROM MemberLivesIn AS M GROUP BY M.HouseID HAVING SUM(M.AnnualIncome) < %s) AS INCOME_FILTER \
            WHERE H.HouseID = INCOME_FILTER.HouseID \
            ORDER BY H.HouseID ASC", 
            (incomeLimit))
    else:
        cursor.execute("SELECT H.HouseID, H.HousingType FROM \
            HouseHold as H, \
            (SELECT M.HouseID FROM MemberLivesIn AS M GROUP BY M.HouseID HAVING SUM(M.AnnualIncome) < %s) AS INCOME_FILTER, \
            (SELECT M.HouseID FROM MemberLivesIn AS M GROUP BY M.HouseID HAVING COUNT(M.Name) <= %s) AS NUM_MEMBER_FILTER \
            WHERE H.HouseID = INCOME_FILTER.HouseID AND H.HouseID = NUM_MEMBER_FILTER.HouseID \
            ORDER BY H.HouseID ASC", 
            (incomeLimit, householdSize))
    housesInformation = cursor.fetchall()
    output = parse_household_information(housesInformation)
    return output

def processSearchGrantsParams(incomeLimit, householdSize):
    nested_queries = " "
    equality_matching = " "
    parameters = []
    if incomeLimit != None:
        nested_queries += ", (SELECT M.HouseID FROM MemberLivesIn AS M GROUP BY (M.HouseID) HAVING SUM(M.AnnualIncome) <= %s) AS INCOME_FILTER "
        equality_matching += "AND M.HouseID = INCOME_FILTER.HouseID "
        parameters.append(incomeLimit)
    if householdSize != None: 
        nested_queries += ", (SELECT M.HouseID FROM MemberLivesIn AS M GROUP BY (M.HouseID) HAVING COUNT(M.Name) <= %s) AS SIZE_FILTER "
        equality_matching += "AND M.HouseID = SIZE_FILTER.HouseID "
        parameters.append(householdSize)
    return nested_queries, equality_matching, parameters

def searchFamilyTogethernessScheme(incomeLimit, householdSize):
    nested_queries, equality_matching, parameters = processSearchGrantsParams(incomeLimit, householdSize)
    conn = pymysql.connect(
        host=SQL_HOST,
        db=SQL_DB,
        user=SQL_USER,
        password=SQL_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("SELECT H.HouseID, H.HousingType, M.Name, M.Gender, M.MaritalStatus, M.Spouse, M.OccupationType, M.AnnualIncome, M.DOB FROM \
            HouseHold as H, \
            MemberLivesIn AS M, \
            (SELECT DISTINCT (P1.HouseID) FROM MemberLivesIn AS P1, MemberLivesIn AS P2 WHERE P1.Gender = 'Male' AND P2.Gender = 'Female' AND P1.Spouse = P2.Name and P2.Spouse = P1.Name) AS PARTNER_FILTER, \
            (SELECT DISTINCT (M.HouseID) From MemberLivesIn AS M WHERE TIMESTAMPDIFF(YEAR, M.DOB, NOW()) < 16) AS CHILD_AGE_FILTER"
            + nested_queries
            + "WHERE H.HouseID = M.HouseID AND H.HouseID = PARTNER_FILTER.HouseID AND H.HouseID = CHILD_AGE_FILTER.HouseID"
            + equality_matching
            + "ORDER BY HouseID ASC",
            (parameters))
    housesInformation = cursor.fetchall()
    output = parse_household_with_member_information(housesInformation)
    return output

def searchElderBonus(incomeLimit, householdSize):
    nested_queries, equality_matching, parameters = processSearchGrantsParams(incomeLimit, householdSize)
    conn = pymysql.connect(
        host=SQL_HOST,
        db=SQL_DB,
        user=SQL_USER,
        password=SQL_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("SELECT H.HouseID, H.HousingType, M.Name, M.Gender, M.MaritalStatus, M.Spouse, M.OccupationType, M.AnnualIncome, M.DOB FROM \
            HouseHold as H, \
            MemberLivesIn AS M, \
            (SELECT DISTINCT (M.HouseID) FROM MemberLivesIn AS M WHERE TIMESTAMPDIFF(YEAR, M.DOB, NOW()) > 50) AS ELDER_FILTER"
            + nested_queries
            + "WHERE H.HouseID = M.HouseID AND H.HouseID = ELDER_FILTER.HouseID"
            + equality_matching
            + "ORDER BY HouseID ASC",
            (parameters))
    housesInformation = cursor.fetchall()
    output = parse_household_with_member_information(housesInformation)
    return output

def searchBabySunshineGrant(incomeLimit, householdSize):
    nested_queries, equality_matching, parameters = processSearchGrantsParams(incomeLimit, householdSize)
    conn = pymysql.connect(
        host=SQL_HOST,
        db=SQL_DB,
        user=SQL_USER,
        password=SQL_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("SELECT H.HouseID, H.HousingType, M.Name, M.Gender, M.MaritalStatus, M.Spouse, M.OccupationType, M.AnnualIncome, M.DOB FROM \
            HouseHold as H, \
            MemberLivesIn AS M, \
            (SELECT DISTINCT (M.Name) FROM MemberLivesIn AS M WHERE TIMESTAMPDIFF(YEAR, M.DOB, NOW()) < 5) AS BABY_FILTER"
            + nested_queries
            + "WHERE H.HouseID = M.HouseID AND M.Name = BABY_FILTER.Name"
            + equality_matching
            + "ORDER BY HouseID ASC",
            (parameters))
    housesInformation = cursor.fetchall()
    output = parse_household_with_member_information(housesInformation)
    return output