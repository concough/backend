from main.models import EntranceLogType

# added 2019-05-31
logtype = EntranceLogType(title="tag_add")
logtype.save()

logtype = EntranceLogType(title="tag_remove")
logtype.save()