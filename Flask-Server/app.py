from flask import Flask, json, request, jsonify, abort
import pymysql

from temp import *

app = Flask(__name__)

@app.route("/create-household", methods=["POST"])
def createHousehold():
    json_data = request.json
    if json_data == None or "HousingType" not in json_data or type(json_data["HousingType"]) is not str:
        return jsonify({"Error" : "HousingType must be present in a json format"}) 
    conn = pymysql.connect(
        host=SQL_HOST,
        db=SQL_DB,
        user=SQL_USER,
        password=SQL_PASSWORD
    )
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO HouseHold (HousingType) VALUES (%s)", (json_data["HousingType"]))
        conn.commit()
        houseID = cursor.lastrowid
        conn.close()
        return jsonify({"HouseID" : houseID})
    except pymysql.err.IntegrityError:
        # TODO: amend this error message
        return jsonify({"Error" : "HousingType must be either Landed/Condominium/HDB"}) 
    except:
        abort(400)

@app.route("/add-member", methods=["POST"])
def addMember():
    json_data = request.json
    if json_data == None or "HouseID" not in json_data or "Member" not in json_data:
        return jsonify({"Error" : "HouseID and Member must be present in a json format"}) 
    conn = pymysql.connect(
        host=SQL_HOST,
        db=SQL_DB,
        user=SQL_USER,
        password=SQL_PASSWORD
    )
    cursor = conn.cursor()
    try:
        member_data = json_data["Member"]
        if "Spouse" in json_data["Member"]:
            cursor.execute("INSERT INTO MemberLivesIn (HouseID, Name, Gender, MaritalStatus, Spouse, OccupationType, AnnualIncome, DOB) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (json_data["HouseID"], member_data["Name"], member_data["Gender"], member_data["MaritalStatus"], member_data["Spouse"], member_data["OccupationType"], member_data["AnnualIncome"], member_data["DOB"]))
        else:
            cursor.execute("INSERT INTO MemberLivesIn (HouseID, Name, Gender, MaritalStatus, OccupationType, AnnualIncome, DOB) VALUES (%s, %s, %s, %s, %s, %s, %s)", (json_data["HouseID"], member_data["Name"], member_data["Gender"], member_data["MaritalStatus"], member_data["OccupationType"], member_data["AnnualIncome"], member_data["DOB"]))
        
        conn.commit()
        conn.close()
        return jsonify({"HouseID" : json_data["HouseID"]})
    except pymysql.err.IntegrityError:
        return jsonify({"Error" : "Please check the allowed values"}) 
    except:
        abort(400)

def parse_household_information(housesInformation):
    output = {"Houses" : []}
    if len(housesInformation) == 0:
        return output
    currentHouse = {"HousingType" : housesInformation[0][1], "Members" : []}
    currentHouseID = housesInformation[0][0]
    for houseInformation in housesInformation:
        # If reach new house, save previous house and reset
        if houseInformation[0] != currentHouseID:
            output["Houses"].append(currentHouse)
            currentHouse = {"HousingType" : houseInformation[1], "Members" : []}
            currentHouseID = houseInformation[0]
        member = {}
        member["Name"] = houseInformation[2]
        member["Gender"] = houseInformation[3]
        member["MaritalStatus"] = houseInformation[4]
        member["Spouse"] = houseInformation[5]
        member["OccupationType"] = houseInformation[6]
        member["AnnualIncome"] = houseInformation[7]
        member["DOB"] = houseInformation[8]
        currentHouse["Members"].append(member)
    # Save the last house as there wasnt a houseid change
    output["Houses"].append(currentHouse)
    return output

@app.route("/list-households", methods=["GET"])
def listHouseholds():
    conn = pymysql.connect(
        host=SQL_HOST,
        db=SQL_DB,
        user=SQL_USER,
        password=SQL_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("SELECT H.HouseID, H.HousingType, M.Name, M.Gender, M.MaritalStatus, M.Spouse, M.OccupationType, M.AnnualIncome, M.DOB FROM HouseHold AS H, MemberLivesIn as M WHERE H.HouseID = M.HouseID ORDER BY H.HouseID ASC;")
    housesInformation = cursor.fetchall()
    output = parse_household_information(housesInformation)
    return jsonify(output) 

@app.route("/show-household", methods=["POST"])
def showHousehold():
    json_data = request.json
    if json_data == None or "HouseID" not in json_data:
        return jsonify({"Error" : "HouseID must be present in a json format"}) 
    conn = pymysql.connect(
        host=SQL_HOST,
        db=SQL_DB,
        user=SQL_USER,
        password=SQL_PASSWORD
    )
    cursor = conn.cursor()
    # Performing two queries instead of a merge as not all data is needed
    cursor.execute("SELECT H.HousingType FROM HouseHold AS H WHERE HouseID = %s", json_data["HouseID"])
    housingInformation = cursor.fetchone()
    if housingInformation == None:
        return jsonify({"Error" : "HouseID not in database"}) 
    housingType = housingInformation[0]

    cursor.execute("SELECT M.Name, M.Gender, M.MaritalStatus, M.Spouse, M.OccupationType, M.AnnualIncome, M.DOB FROM MemberLivesIn AS M WHERE M.HouseID = %s", json_data["HouseID"])
    membersInformation = cursor.fetchall()
    output = {"HousingType" : housingType, "Members" : []}
    for memberInformation in membersInformation:
        member = {}
        member["Name"] = memberInformation[0]
        member["Gender"] = memberInformation[1]
        member["MaritalStatus"] = memberInformation[2]
        member["Spouse"] = memberInformation[3]
        member["OccupationType"] = memberInformation[4]
        member["AnnualIncome"] = memberInformation[5]
        member["DOB"] = memberInformation[6]
        output["Members"].append(member)
    return jsonify(output)

def searchStudentEncouragementBonus(additionalIncomeLimit, householdSize):
    incomeLimit = 150000
    if additionalIncomeLimit != None and additionalIncomeLimit < 150000:
        incomeLimit = additionalIncomeLimit
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
    output = parse_household_information(housesInformation)
    return output

# Using GET as the question specified search parameters in URL
@app.route("/search-grants", methods=["GET"])
def searchGrants():
    householdSize = int(request.args.get("householdsize"))
    totalIncome = float(request.args.get("totalincome"))
    output = {}

    grantResult = searchStudentEncouragementBonus(totalIncome, householdSize)
    output["Student Encouragement Bonus"] = grantResult

    return jsonify(output)

if __name__ == "__main__":
    app.run(debug=True)