from flask import Flask, request, jsonify, abort
from db_output_parsers import *
from grants import *
from db_conn import *

app = Flask(__name__)
app.config.from_object("config.Config")

@app.route("/create-household", methods=["POST"])
def createHousehold():
    json_data = request.json
    if json_data == None or "HousingType" not in json_data or type(json_data["HousingType"]) is not str:
        return jsonify({"Error" : "HousingType must be present in a json format"}) 
    try:
        conn, cursor = create_connection(app.config)
    except:
        return jsonify({"Error" : "Unable to reach database"}) 
    try:
        cursor.execute("INSERT INTO HouseHold (HousingType) VALUES (%s)", (json_data["HousingType"]))
        conn.commit()
        houseID = cursor.lastrowid
        conn.close()
        return jsonify({"HouseID" : houseID})
    except pymysql.err.IntegrityError:
        # TODO: amend this error message
        conn.close()
        return jsonify({"Error" : "HousingType must be either Landed/Condominium/HDB"}) 
    except:
        conn.close()
        abort(400)

@app.route("/add-member", methods=["POST"])
def addMember():
    json_data = request.json
    if json_data == None or "HouseID" not in json_data or "Member" not in json_data:
        return jsonify({"Error" : "HouseID and Member must be present in a json format"}) 
    try:
        conn, cursor = create_connection(app.config)
    except:
        return jsonify({"Error" : "Unable to reach database"}) 
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
        conn.close()
        return jsonify({"Error" : "Please check the allowed values"}) 
    except:
        conn.close()
        abort(400)

@app.route("/list-households", methods=["GET"])
def listHouseholds():
    try:
        conn, cursor = create_connection(app.config)
    except:
        return jsonify({"Error" : "Unable to reach database"}) 
    cursor.execute("SELECT H.HouseID, H.HousingType, M.Name, M.Gender, M.MaritalStatus, M.Spouse, M.OccupationType, M.AnnualIncome, M.DOB FROM HouseHold AS H, MemberLivesIn as M WHERE H.HouseID = M.HouseID ORDER BY H.HouseID ASC;")
    housesInformation = cursor.fetchall()
    conn.close()
    output = parse_household_with_member_information(housesInformation)
    return jsonify(output) 

@app.route("/show-household", methods=["POST"])
def showHousehold():
    json_data = request.json
    if json_data == None or "HouseID" not in json_data:
        return jsonify({"Error" : "HouseID must be present in a json format"}) 
    try:
        conn, cursor = create_connection(app.config)
    except:
        return jsonify({"Error" : "Unable to reach database"}) 
    # Performing two queries instead of a merge as not all data is needed
    cursor.execute("SELECT H.HousingType FROM HouseHold AS H WHERE HouseID = %s", json_data["HouseID"])
    housingInformation = cursor.fetchone()
    conn.close()
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

# Using GET as the question specified search parameters in URL
@app.route("/search-grants", methods=["GET"])
def searchGrants():
    householdSize = request.args.get("householdsize")
    if householdSize != None:
        householdSize = int(householdSize)
    totalIncome = request.args.get("totalincome")
    if totalIncome != None:
        totalIncome = float(totalIncome)

    try:
        conn, cursor = create_connection(app.config)
    except:
        return jsonify({"Error" : "Unable to reach database"}) 

    output = {}

    grantResult = searchStudentEncouragementBonus(conn, cursor, totalIncome, householdSize)
    output["Student Encouragement Bonus"] = grantResult

    grantResult = searchFamilyTogethernessScheme(conn, cursor, totalIncome, householdSize)
    output["Family Togetherness Scheme"] = grantResult

    grantResult = searchElderBonus(conn, cursor, totalIncome, householdSize)
    output["Elder Bonus"] = grantResult

    grantResult = searchBabySunshineGrant(conn, cursor, totalIncome, householdSize)
    output["Baby Sunshine Grant"] = grantResult

    grantResult = searchYOLOGSTGrant(conn, cursor, totalIncome, householdSize)
    output["YOLO GST Grant"] = grantResult

    conn.close()
    return jsonify(output)

@app.route("/delete-household", methods=["POST"])
def deleteHousehold():
    json_data = request.json
    if json_data == None or "HouseID" not in json_data:
        return jsonify({"Error" : "HouseID must be present in a json format"}) 
    try:
        conn, cursor = create_connection(app.config)
    except:
        return jsonify({"Error" : "Unable to reach database"}) 
    try:
        cursor.execute("DELETE FROM HouseHold WHERE HouseID = %s", json_data["HouseID"])
        conn.commit()
        deletedCount = cursor.rowcount
        conn.close()
        if deletedCount == 1:
            return jsonify({"HouseID" : json_data["HouseID"]})
        else:
            return jsonify({"Error" : "House not present in system"})
    except pymysql.err.IntegrityError:
        conn.close()
        return jsonify({"Error" : "Unable to delete household as there are people still in the household"})
    except:
        conn.close()
        abort(400)

@app.route("/delete-member", methods=["POST"])
def deleteMember():
    json_data = request.json
    if json_data == None or "Name" not in json_data:
        return jsonify({"Error" : "Name must be present in a json format"}) 
    try:
        conn, cursor = create_connection(app.config)
    except:
        return jsonify({"Error" : "Unable to reach database"}) 
    cursor.execute("DELETE FROM MemberLivesIn WHERE Name = %s", json_data["Name"])
    conn.commit()
    deletedCount = cursor.rowcount
    conn.close()
    if deletedCount == 1:
        return jsonify({"Name" : json_data["Name"]})
    else:
        return jsonify({"Error" : "House not present in system"})

if __name__ == "__main__":
    app.run(debug=True)