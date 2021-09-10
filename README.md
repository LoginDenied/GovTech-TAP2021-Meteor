# GovTech-TAP2021-Meteor
## Assumptions
### Database
- Name is assumed to be unique and used as a PK due to the lack of a unique identifier such as NRIC
- Gender is assumed to be binary (male/female) and thus contrained to those values
- Marriage is assumed to be monogamy (a family member can have only one assigned spouse)
- AnnualIncome is assumed to potentially contain decimals and thus accounted for by using a FLOAT
- A house is assumed to can have no residents (a household can exist without a linked family member)
- Security of the HouseID is not a concern and can thus be a running number to identify the Household
    - If security was a concern, a CSRNG should be used to generate a UID instead
### Flask
- Assumed that a generic 400 reply is sufficient for non-specific errors
- Assumed that POST can be used with a json body unless specified (Q2.5)
- Assumed that malicious parameters are not a concerened for security issues such as SQL Injection / XSS / etc.
    - If security was a concerned, received parameters should be checked and sanitized before execution and storage in the database (such as through utlization of bleach)
### Endpoints
- Q2.5 Additional parameters of HousholdSize and TotalIncome are assumed to be additional upper limits in the search and of a higher priority than the grant criterias
- Q2.5 For the Student Encouragement Scheme, it was assumed that the OccupationType needs to be Student
- Q2.5 As parent-child relations are not stored, it is assumed that a person is a children as long as the Household is the same and age accurate to the criterias
## Considerations
### Database
- VARCHAR(255) was used even for field that have known values although it could be lower such as being VARCHAR(10) for OccupationType for purposes of adding in future values
- Foreign Key (FK) constraints and their correponding lookup tables were used to constraint columns to certain values instead of a CONSTRAINT check for expandability concerns as well
### Endpoints
- Certain items were considered but not included in the current iteration due to certain uncertainties
- Requirement of the Spouse field to be present if MaritalStatus is set to be "Married" was not enforced to be uncertainty any intermediate states if any
- Requirement of setting person A's spouse to person B should set person B's spouse to be person A was not enforced for consideration of a lack of understanding of updating procedures
    - For example, if A & B divorced and B remarried, inserting person C, should person B's status be immediately modified from this?
- Due to enforecement of Foreign Key constraints (FK) for Spouse, it is noted that the workflow would be more user-friendy if there is an Update Particulars endpoint but not included as it was not requested
    - Alternatively, while less ideal, the Add Member could be modified to be Add Member**s** with a deffered check (this depends on DB support)
### Architecture
- While the DB is currently ran as part of Docker Compose with a volume, this was done to increase deployment ease but is noted to be non-ideal
    - Scalability: The DB should scale vertically with horizontal read-replicas instead (at least for the current choice of a relational DB) for read-write consistency
## Instructions To Run
- Windows
    - Running:
        - Ensure that docker-compose, which is included as part of Docker Desktop for windows, is installed
        - Clone the repository into a location of choice
        - Open a command prompt and navigate to the base directory of the project
        - Run ```docker-compose build```
        - Run ```docker-compose up```
    - Cleaning Up
        - Run ```docker-compose down```
        - Run ```docker volume ls```
        - Run ```docker volume rm <name of dbdata volume shown in ls>```