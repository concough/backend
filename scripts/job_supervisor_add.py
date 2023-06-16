from django.contrib.auth.models import User

from main.models_functions import connectToMongo

username = "****"
db = connectToMongo()

user = User.objects.get(username=username)
owner_obj = {
    "user_id": user.id,
    "username": user.username,
    "fullname": user.get_full_name(),
    "joined": user.date_joined
}

db.job.update_many({'job_type': "ENTRANCE"}, {
    '$set': {
        'job_owner_id': user.id,
        'job_owner': owner_obj,
        'job_main_file': None,
    }
})

# create checkers and check_state
jobs = db.job.find({'job_type': "ENTRANCE", 'status': {'$in': ['CREATED', 'STARTED']}})
for j in jobs:
    for task in j["data"]["tasks"]:
        db.job.update_one({'job_relate_uniqueid': j["job_relate_uniqueid"], 'data.tasks.task_unique_id': task['task_unique_id']}, { "$set": { 'data.tasks.$.checkers': [], 'data.tasks.$.main_term_file': None, 'data.tasks.$.rejected_count': 0}})

        if task["state"] != "CREATED" and task["state"] != "WAIT_FOR_TYPE" and task["state"] != "TYPE_STARTED" and task["state"] != "TYPE_DONE":
            db.job.update_one({'job_relate_uniqueid': j["job_relate_uniqueid"], 'data.tasks.task_unique_id': task['task_unique_id']}, {"$set": {'data.tasks.$.main_term_file': task["term_file"]}})

        if task["state"] == "CHECK_STARTED" or task["state"] == "CHECK_DONE":
            db.job.update_one({'job_relate_uniqueid': j["job_relate_uniqueid"],'data.tasks.task_unique_id': task['task_unique_id']}, {"$set": {'data.tasks.$.checkers.0': task['holding_editor'],'data.tasks.$.check_state': 1}})
