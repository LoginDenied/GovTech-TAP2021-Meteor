from db_output_parsers import *
from db_conn import *

def searchStudentEncouragementBonus(conn, cursor, additionalIncomeLimit, householdSize):
    incomeLimit = 150000
    if additionalIncomeLimit != None:
        incomeLimit = min(additionalIncomeLimit, incomeLimit)
    if householdSize == None:
        cursor.execute("SELECT H.HouseID, H.HousingType, M.Name, M.Gender, M.MaritalStatus, M.Spouse, M.OccupationType, M.AnnualIncome, M.DOB FROM \
            HouseHold as H, \
            MemberLivesIn AS M, \
            (SELECT M.Name FROM MemberLivesIn AS M WHERE M.OccupationType = 'Student' AND TIMESTAMPDIFF(YEAR, M.DOB, NOW()) < 16) AS AGE_FILTER, \
            (SELECT M.HouseID FROM MemberLivesIn AS M GROUP BY M.HouseID HAVING SUM(M.AnnualIncome) < %s) AS INCOME_FILTER \
            WHERE H.HouseID = M.HouseID AND M.Name = AGE_FILTER.Name AND H.HouseID = INCOME_FILTER.HouseID ORDER BY HouseID ASC", 
            (incomeLimit))
    else:
        cursor.execute("SELECT H.HouseID, H.HousingType, M.Name, M.Gender, M.MaritalStatus, M.Spouse, M.OccupationType, M.AnnualIncome, M.DOB FROM \
            HouseHold as H, \
            MemberLivesIn AS M, \
            (SELECT M.Name FROM MemberLivesIn AS M WHERE M.OccupationType = 'Student' AND TIMESTAMPDIFF(YEAR, M.DOB, NOW()) < 16) AS AGE_FILTER, \
            (SELECT M.HouseID FROM MemberLivesIn AS M GROUP BY M.HouseID HAVING SUM(M.AnnualIncome) < %s) AS INCOME_FILTER, \
            (SELECT M.HouseID FROM MemberLivesIn AS M GROUP BY M.HouseID HAVING COUNT(M.Name) <= %s) AS NUM_MEMBER_FILTER \
            WHERE H.HouseID = M.HouseID AND M.Name = AGE_FILTER.Name AND H.HouseID = INCOME_FILTER.HouseID AND H.HouseID = NUM_MEMBER_FILTER.HouseID \
            ORDER BY HouseID ASC", 
            (incomeLimit, householdSize))
    housesInformation = cursor.fetchall()
    output = parse_household_with_member_information(housesInformation)
    return output

def searchYOLOGSTGrant(conn, cursor, additionalIncomeLimit, householdSize):
    incomeLimit = 100000
    if additionalIncomeLimit != None:
        incomeLimit = min(additionalIncomeLimit, incomeLimit)
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

def searchFamilyTogethernessScheme(conn, cursor, incomeLimit, householdSize):
    nested_queries, equality_matching, parameters = processSearchGrantsParams(incomeLimit, householdSize)
    cursor.execute("SELECT H.HouseID, H.HousingType, M.Name, M.Gender, M.MaritalStatus, M.Spouse, M.OccupationType, M.AnnualIncome, M.DOB FROM \
            HouseHold as H, \
            MemberLivesIn AS M, \
            ( \
                (SELECT P1.HouseID, P1.Name FROM MemberLivesIn AS P1, MemberLivesIn AS P2 WHERE P1.Spouse = P2.Name AND P2.Spouse = P1.Name AND P1.HouseID = P2.HouseID) \
                UNION \
                (SELECT M.HouseID, M.Name From MemberLivesIn AS M WHERE TIMESTAMPDIFF(YEAR, M.DOB, NOW()) < 16) \
            ) AS NAME_FILTER"
            + nested_queries
            + "WHERE H.HouseID = M.HouseID AND M.Name = NAME_FILTER.Name AND H.HouseID = NAME_FILTER.HouseID"
            + equality_matching
            + "ORDER BY HouseID ASC",
            (parameters))
    housesInformation = cursor.fetchall()
    output = parse_household_with_member_information(housesInformation)
    return output

def searchElderBonus(conn, cursor, incomeLimit, householdSize):
    nested_queries, equality_matching, parameters = processSearchGrantsParams(incomeLimit, householdSize)
    cursor.execute("SELECT H.HouseID, H.HousingType, M.Name, M.Gender, M.MaritalStatus, M.Spouse, M.OccupationType, M.AnnualIncome, M.DOB FROM \
            HouseHold as H, \
            MemberLivesIn AS M, \
            (SELECT M.Name FROM MemberLivesIn AS M WHERE TIMESTAMPDIFF(YEAR, M.DOB, NOW()) > 50) AS ELDER_FILTER"
            + nested_queries
            + "WHERE H.HouseID = M.HouseID AND M.Name = ELDER_FILTER.Name"
            + equality_matching
            + "ORDER BY HouseID ASC",
            (parameters))
    housesInformation = cursor.fetchall()
    output = parse_household_with_member_information(housesInformation)
    return output

def searchBabySunshineGrant(conn, cursor, incomeLimit, householdSize):
    nested_queries, equality_matching, parameters = processSearchGrantsParams(incomeLimit, householdSize)
    cursor.execute("SELECT H.HouseID, H.HousingType, M.Name, M.Gender, M.MaritalStatus, M.Spouse, M.OccupationType, M.AnnualIncome, M.DOB FROM \
            HouseHold as H, \
            MemberLivesIn AS M, \
            (SELECT M.Name FROM MemberLivesIn AS M WHERE TIMESTAMPDIFF(YEAR, M.DOB, NOW()) < 5) AS BABY_FILTER"
            + nested_queries
            + "WHERE H.HouseID = M.HouseID AND M.Name = BABY_FILTER.Name"
            + equality_matching
            + "ORDER BY HouseID ASC",
            (parameters))
    housesInformation = cursor.fetchall()
    output = parse_household_with_member_information(housesInformation)
    return output