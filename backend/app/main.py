import os
import re
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db, Application, Staff, Skill, Role, RoleSkill, StaffSkill, AccessControl, Listing, ListingSkill
import re

from datetime import date, datetime
import json
from os import environ
import argparse
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv()

def configure_app(args=None):
    # Configuring the app...
    if args is None:
        parser = argparse.ArgumentParser(description="select env")
        parser.add_argument("--test", action="store_true", help="Enable the test env")
        parser.add_argument("--prod", action="store_true", help="Enable the prod env")
        args = parser.parse_args()

    if args.test:
            print("test env")
            dbURL = os.getenv("testdbURL")
           
    elif args.prod:
            print("prod env")
            dbURL = os.getenv("proddbURL")

    else:
            print("running test environment by default")
            dbURL = os.getenv("testdbURL")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = dbURL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    CORS(app)


#staff.py
@app.route("/staffs", methods=['GET'])
def get_all_staffs():
    staffs = Staff.query.all()
    if staffs:
        return jsonify({
            "code": 200,
            "data": [staff.json() for staff in staffs]
        })
    return jsonify({
        "code": 404,
        "message": "No roles found."
    })

@app.route('/staff_skill', methods=['GET'])
def get_all_staff_skill():
    staff_skills = StaffSkill.query.all()
    staff_skill_map = {}
    
    for ss in staff_skills:
        if ss.staff_id not in staff_skill_map:
            staff_skill_map[ss.staff_id] = []
        staff_skill_map[ss.staff_id].append(ss.skill_id)
    
    return jsonify(
        {
            "code": 201,
            "data": staff_skill_map
        }
    ), 201

@app.route('/staffs/<int:userID>', methods=['GET'])
def get_staff_by_id(userID):
    staff = Staff.query.filter_by(staff_id = userID).first()
    if staff:
        return jsonify({
            "code": 200,
            "data": staff.json()
        }), 200
    return jsonify({
        "code": 404,
        "message": "No staff found for the given ID."
    }), 404

@app.route("/staffs/dept", methods=['GET'])
def get_all_depts():
    # fetch all unique departments from the staff table
    depts = db.session.query(Staff.dept).distinct().all()
    depts_list = []
    if depts:
        depts_list = [dept[0] for dept in depts]
        return jsonify({
            "code": 200,
            "data": depts_list
        })
    return jsonify({
        "code": 404,
        "message": "No departments found.",
        "data": depts_list
    })
    
@app.route("/staffs/skills/<int:staff_id>", methods=['GET'])
def get_staff_skills(staff_id):
    
    staff_skill= StaffSkill.query.filter_by(staff_id=staff_id).all()
    skill_list=[]
    if staff_skill:
        for staff in staff_skill:
            skill_list.append(staff.skill_id)
        return jsonify({
            "code": 200,
            "data": skill_list
        })
    else:
        return jsonify({
            "code": 404,
            "message": "No skills found.",
            "data": skill_list
        })

@app.route("/staffs/display_skills/<int:staff_id>", methods=['GET'])
def get_staff_skilldisplay(staff_id):
    
    staff_skill= StaffSkill.query.filter_by(staff_id=staff_id).all()
    skill_map={}
    if staff_skill:
        skill_list=[]
        for staff in staff_skill:
            skill_list.append(staff.skill_id)
        for skill_id in skill_list:
            skill_map[skill_id]=Skill.query.filter_by(skill_id=skill_id).first().skill_name
            
        return jsonify({
            "code": 200,
            "data": skill_map
        })
    else:
        return jsonify({
            "code": 404,
            "message": "No skills found.",
            "data": skill_map
        })


@app.route("/access_control", methods=['GET'])
def get_all_access_control():
    access_controls = AccessControl.query.all()
    if access_controls:
        return jsonify({
            "code": 200,
            "data": [access_control.json() for access_control in access_controls]
        }), 200
    return jsonify({
        "code": 404,
        "message": "No access control found."
    }), 404
    
#skill.py
@app.route("/skills", methods=['GET'])
def get_all_skills():
    # fetch all skills from the database
    skills = Skill.query.all()
    if not skills:
        return jsonify({
            "code": 404,
            "message": "No skills found.",
            "data": []
        })
    
    return jsonify({
        "code": 200,
        "data": [skill.json() for skill in skills]
    }), 200

@app.route("/skills/<int:skill_id>", methods=['GET'])
def get_all_name(skill_id):
    skill = Skill.query.filter_by(skill_id=skill_id).first()

    if not skill:
        return jsonify({
            "code": 404,
            "message": f"No skill found for id {skill_id}"
        }), 404
    
    return jsonify({
        "code": 200,
        "data": {
            "skill_id": skill_id,
            "skill_name": skill.skill_name
        }
    }),200

#role.py
@app.route("/roles", methods=['GET'])
def get_all_roles():
    # fetch all roles from the database
    roles = Role.query.all()
    if roles:
        return jsonify({
            "code": 200,
            "data": [role.json() for role in roles]
        }),200
    return jsonify({
        "code": 404,
        "message": "No roles found.",
        "data": []
    }),404

# This is to find all the skills given specific role id
@app.route("/role_skill/<int:role_id>", methods=['GET'])
def get_skills_by_role(role_id):
    try:
        role_skills = RoleSkill.query.filter_by(role_id=role_id).all()
        skills = [role_skill.skill_id for role_skill in role_skills]
        if role_skills:
            return jsonify({
                "code": 200,
                "data": {
                    "role_id": role_id,
                    "skill_ids": skills
                }
            })
        return jsonify({
            "code": 404,
            "message": "No skills found for the given role id."
        }), 404

    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return jsonify({
            "code": 500,
            "message": "Internal Server Error"
        }), 500
    
#listing.py
@app.route("/create_listing", methods=['POST'])
def create_listing():
        
        data = request.get_json()
        # print("Received data: ", data)
        

        listing_name = data.get('listing_name')
        listing_description = data.get('listing_description')
        deadline = data.get('deadline')
        dept = data.get('dept')
        hr_id = data.get('hr_id')
        listing_skill = data.get('listing_skill')

        errors = []

        if not deadline:
            return jsonify({'message': 'No deadline provided'}), 400

        try:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            errors.append("Deadline format should be YYYY-MM-DD")
        
        if not listing_skill:
            return jsonify({'message': 'Please select at least one skill for the listing'}), 400
        
        if not data:
            errors.append("No input data provided")

        if not isinstance(listing_skill, list) or not listing_skill or len(listing_skill) == 0:
            errors.append("Please select at least one skill for the role")
            
        if not deadline:
            errors.append("Please select a deadline for the role")
            
        if deadline and deadline_date < datetime.now():
            errors.append("Deadline should not be in the past")
        
        if not listing_name or len(listing_name) == 0:
            errors.append("Listing name is required")
        
        if not listing_description or len(listing_description) == 0:
            errors.append("Listing decription is required")
        
        if not dept or len(dept) == 0:
            errors.append("Department name is required")
        
        if len(errors) > 0:
            return jsonify({"code": 400, "errors": errors}), 400

        new_listing = Listing(listing_name=listing_name, listing_description=listing_description, dept=dept, deadline=deadline_date, hr_id=hr_id)

        try:
            db.session.add(new_listing)
            db.session.commit()
            
            create_listing_skill(listing_skill, new_listing.listing_id)
        except Exception as e:
            print("Error while adding new listing: ", str(e))
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while adding new listing : " + str(e)
                }
            ), 500

        return jsonify(
            {
                "code": 201,
                "data": new_listing.json()
            }
        ), 201

@app.route("/listings", methods=['GET'])
def get_all_listings():
    # fetch all listings from the database
    listings = Listing.query.all()
    if listings:
        return jsonify({
            "code": 200,
            "data": [listing.json() for listing in listings]
        })
    return jsonify({
        "code": 404,
        "message": "No listings found.",
        "data": []
    })

@app.route("/listings/<int:listing_id>", methods=['GET'])
def get_listing(listing_id):
    # fetch listing by id
    listing = Listing.query.filter_by(listing_id=listing_id).first()
    print(listing)
    skill_ids = get_skill_ids_by_listing(listing_id)
    print(skill_ids)
    if listing:
        return jsonify({
            "code": 200,
            "data": {
                **listing.json(),
                "skill_ids": skill_ids
            }
        })
    return jsonify({
        "code": 404,
        "message": "No listing with id " + listing_id +  "found."
    })

@app.route("/update_listing/<int:listing_id>", methods=['PUT'])
def update_listing(listing_id):
    listing = Listing.query.filter_by(listing_id=listing_id).first()
    if not listing:
        return jsonify(
            {
                "code": 404,
                "data": {"listing_id": listing_id},
                "message": "listing not found."
            }
        ), 404

    data = request.get_json()
    if not data:
        return jsonify(
            {
                "code": 400,
                "data": {"listing_id": listing_id},
                "message": "No input data provided"
            }
        ), 400
    
    listing_name = data.get('listing_name')
    listing_description = data.get('listing_description')
    dept = data.get('dept')
    listing_skill = data.get('listing_skill')
    deadline = data.get('deadline')
    errors = []

    try: 
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
    except ValueError:
        errors.append("Deadline format should be YYYY-MM-DD")

    if deadline_date < datetime.now():
        errors.append("Deadline should not be in the past")

    if not data:
        errors.append("No input data provided")

    if not isinstance(listing_skill, list) or not listing_skill or len(listing_skill) == 0:
        errors.append("Please select at least one skill for the role")
        
    if not deadline:
        errors.append("Please select a deadline for the role")
    
    if not listing_name or len(listing_name) == 0:
        errors.append("Listing name is required")
    
    if not listing_description or len(listing_description) == 0:
        errors.append("Listing decription is required")
    
    if not dept or len(dept) == 0:
        errors.append("Department name is required")
    
    if len(errors) > 0:
        return jsonify({"code": 400, "errors": errors}), 400
    
    listing.listing_name = listing_name
    listing.listing_description = listing_description
    listing.dept = dept
    listing.deadline = deadline_date

    try:
        ListingSkill.query.filter_by(listing_id=listing_id).delete()

        new_listing_skills = [ListingSkill(listing_id=listing_id, skill_id=skill_id) for skill_id in listing_skill]
        db.session.bulk_save_objects(new_listing_skills)
        
        db.session.commit()

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while updating the listing and its skills: " + str(e)
            }
        ), 500

    return jsonify(
        {
            "code": 200,
            "data": listing.json()
        }
    )

# This is to find all the skills given specific listing id
@app.route("/listing_skill/<int:listing_id>", methods=['GET'])
def get_skills_by_listing(listing_id):
    try:
        listing_skills = ListingSkill.query.filter_by(listing_id=listing_id).all()
        skills = [listing_skill.skill_id for listing_skill in listing_skills]
        if listing_skills:
            return jsonify({
                "code": 200,
                "data": {
                    "listing_id": listing_id,
                    "skill_ids": skills
                }
            })
        return jsonify({
            "code": 404,
            "message": "No skills found for the given listing id."
        }), 404

    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return jsonify({
            "code": 500,
            "message": "Internal Server Error"
        }), 500

@app.route('/listing_skill', methods =['GET'])
def get_all_listing_skill():
    listing_skills = ListingSkill.query.all()
    listing_skill_map = {}
    
    for ls in listing_skills:
        if ls.listing_id not in listing_skill_map:
            listing_skill_map[ls.listing_id] = []
        listing_skill_map[ls.listing_id].append(ls.skill_id)

    return jsonify(
        {
            "code": 201,
            "data": listing_skill_map
        }
    ), 201

def get_skill_ids_by_listing(listing_id):
    try:
        listing_skills = ListingSkill.query.filter_by(listing_id=listing_id).all()
        skills = [listing_skill.skill_id for listing_skill in listing_skills]
        if listing_skills:
            return skills
        return []

    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return jsonify({
            "code": 500,
            "message": "Internal Server Error"
        }), 500

def create_listing_skill(skill_ids, listing_id):
    listing_skills = []
    for skill_id in skill_ids:
        new_listing_skill = ListingSkill(listing_id=listing_id, skill_id=skill_id)
        listing_skills.append(new_listing_skill)

    try:
        db.session.bulk_save_objects(listing_skills)
        db.session.commit()
    except Exception as e:
        print(e)
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while adding new listing skills: " + str(e)
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": {
                "listing_id": listing_id,
                "skill_ids": skill_ids 
            }
        }
    ), 201

def update_listing_skill(skill_ids, listing_id):
    # Delete all existing listing-skill mappings for the given listing
    try:
        ListingSkill.query.filter_by(listing_id=listing_id).delete()
        db.session.commit()
    except Exception as e:
        return jsonify({"code": 500, "message": f"An error occurred while deleting old listing skills: {str(e)}"}), 500

    # Add new listing-skill mappings
    for skill_id in skill_ids:
        new_listing_skill = ListingSkill(listing_id = listing_id, skill_id = skill_id)
        try:
            db.session.add(new_listing_skill)
            db.session.commit()
            print('new entry commited')
        except Exception as e:
            print(e)
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while adding new listing skill" + str(e)
                }
            ), 500
        
        print(json.dumps(new_listing_skill.json(), default=str)) # convert a JSON object to a string and print
        print()

    return jsonify(
        {
            "code": 201,
            "data": {
                "listing_id": listing_id,
                "skill_ids": skill_ids 
            }
        }
    ), 201

#application.py

@app.route('/apply', methods=['POST'])
def apply_for_listing():
    data = request.json
    staff_id = data.get('staff_id')
    listing_id = data.get('listing_id')
    staff_name = data.get('staff_name')

    # Check if an application with the same staff_id and listing_id already exist
    existing_application = Application.query.filter_by(staff_id=staff_id, listing_id=listing_id, staff_name=staff_name).first()
    if existing_application:
        return jsonify({"message": "You've already applied for this listing.", "error": True}), 400  # Directly return the error message

    # If not, proceed to add the application
    application = Application(staff_id=staff_id, listing_id=listing_id,staff_name=staff_name,date_applied=date.today())
    db.session.add(application)
    db.session.commit()

    return jsonify(application.json()), 201

@app.route("/listings/<int:listing_id>/applications", methods=['GET'])
def get_applications_by_listing(listing_id):
    # fetch all applications for a specific listing from the database
    applications = Application.query.filter_by(listing_id=listing_id).all()
    if applications:
        return jsonify({
            "code": 200,
            "data": [application.json() for application in applications]
        })
    return jsonify({
        "code": 404,
        "message": "No applications found for this listing.",
        "data": []
    })

@app.route("/applications/<int:application_id>", methods=['GET'])
def get_application_by_id(application_id):
    application = Application.query.filter_by(application_id=application_id).first()
    if application:
        return jsonify({
            "code": 200,
            "data": application.json(),
        })
    return jsonify({
        "code": 404,
        "message": "Application not found.",
        "data": []
    })


def SkillMatchPercentage(skillsForListing, employee_skills):
    matchCount = len([skill for skill in skillsForListing if skill in employee_skills])
    percentage = (matchCount / len(skillsForListing)) * 100
    return round(percentage)

def isListingExpired(deadline):
    today = date.today()
    listingDeadline = datetime.strptime(deadline, "%Y-%m-%d").date()
    return today > listingDeadline

def userHasSkill(skill, user_skills):
    return skill in user_skills

def truncateDescription(description):
    words = description.split(' ')
    if len(words) > 100:
        return ' '.join(words[:100]) + '...'
    return description

def sort_by_ID(skills):
    return sorted(skills, key=lambda x: x["id"])

def sort_alphabetically(skills):
    return sorted(skills, key=lambda x: x["skill_name"])

def process_listing_name(listing_name):
    cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', '', listing_name)
    cleaned_name = cleaned_name.replace(' ', '_')
    return cleaned_name

if __name__ == '__main__':
    configure_app()
    with app.app_context():
        db.create_all()
    print("This is flask for " + os.path.basename(__file__) + "spm team 6")
    app.run(host='0.0.0.0', port=5005, debug=True)