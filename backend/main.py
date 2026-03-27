from database.connection import get_connection
from database.organization_queries import create_org
from database.user_queries import create_user
from database.membership_queries import create_membership
from services.organization_service import join_organization, get_organizations
from services.auth_service import login_user, signup_user
import bcrypt
from Utils.security import hash_password
conn = get_connection()
# email = "2024BTECHCS@pdeu.ac.in"
# org_name = "PDE UNIVERSITY"
# org_id, org_key = create_org(org_name)
# print(f"Organization created! Here's your 3-day org key: {org_key}")
# user_id = create_user(email, "PdeuStudent@2006")
# print(f"Welcome to Gradwise! Your user-id is {user_id}")
# role = "Student"
# membership_id = create_membership(user_id, org_id, role)
# print(f"Congrats dear {role}! You have been enlisted in {org_name}!")
# join_organization(3, "8VRsUTmMsmlsFo19e3a8ap7OxJpLFHE43SCnW9qU7y1fGXIJl3", "Student")
# conn.close()
email = "202401083@dau.ac.in"
password = "RK@2007"
# message1, user_id = signup_user(email, password)
# print(f"{message1}. Your user id is {user_id}")
#result = login_user(email, password)
#print(result["message"])
# print("HASH:", h, len(h))
# print("VERIFY:", bcrypt.checkpw(pw.encode(), h.encode()))
# join_organization(13, "2a32ax135tROzD3H3cJVsgSR8RP9kPKHHx3yRYAAm6tfZ24cab", "Student")
org_id, org_key = create_org("IIIT DELHI")
print(f"Organization created! Here's your org key: {org_key}")
signup_user("hello@bye.com", "Hello@bye")