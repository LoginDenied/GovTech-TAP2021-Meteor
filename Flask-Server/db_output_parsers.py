def parse_household_with_member_information(housesInformation):
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

def parse_household_information(housesInformation):
    output = {"Houses" : []}
    if len(housesInformation) == 0:
        return output
    for houseInformation in housesInformation:
            currentHouse = {
                "HouseID" : houseInformation[0],
                "HousingType" : houseInformation[1]
            }
            output["Houses"].append(currentHouse)
    return output