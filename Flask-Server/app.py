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
    if len(housesInformation) == 0:
        return jsonify({"Message" : "No houses in database"}) 
    output = {"Houses" : []}
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
    return jsonify(output) 

if __name__ == "__main__":
    app.run(debug=True)