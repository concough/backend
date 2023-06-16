import copy

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from main.models_functions import connectToMongo
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.views import ScopedProtectedResourceView


class UserLogViewSet(ViewSet):
    def sync(self, request, **kwargs):
        data =  request.data.get('data', None)
        device_name = request.data.get('device_name', None)
        device_id = request.data.get('device_unique_id', None)

        result = {}
        if data is not None and device_id is not None and device_name is not None:
            db = connectToMongo()

            result["status"] = "OK"
            result["records"] = []
            for item in data:
                try:
                    userId = request.user.id
                    username = request.user.username

                    record = db.appuserlog.find_one({'uniqueId': item['uniqueId'],
                                           'userId': userId,
                                           'deviceName': device_name,
                                            'deviceUniqueId': device_id})

                    if record is None:
                        item["userId"] = userId
                        item['username'] = username
                        item['deviceName'] = device_name
                        item['deviceUniqueId'] = device_id

                        db.appuserlog.insert(item)

                        result["records"].append(item["uniqueId"])


                        log_type = item["logType"]
                        if log_type == "ENTRANCE_QUESTION_STAR" or log_type == "ENTRANCE_QUESTION_UNSTAR":
                            product_unique_id = item["extra"]["uniqueId"]
                            question_no = item["extra"]["questionNo"]

                            product_record = db.appuserlog_product.find_one({'uniqueId': product_unique_id,
                                                                               'userId': userId,
                                                                               'productType': 'Entrance'})

                            if product_record is None:
                                product_record = {
                                    'uniqueId': product_unique_id,
                                    'userId': userId,
                                    'productType': 'Entrance',
                                    'bookmarks': []
                                }


                                if log_type == "ENTRANCE_QUESTION_STAR":
                                    product_record['bookmarks'].appned(question_no)

                                db.appuserlog_product.insert(product_record)

                            else:
                                if 'bookmarks' in product_record:
                                    if log_type == "ENTRANCE_QUESTION_STAR":
                                        db.appuserlog_product.update_one({'uniqueId': product_unique_id,
                                                                               'userId': userId,
                                                                               'productType': 'Entrance'}, {
                                            '$push': {
                                                'bookmarks': question_no
                                            }
                                        })
                                    elif log_type == "ENTRANCE_QUESTION_UNSTAR":
                                        db.appuserlog_product.update_one({'uniqueId': product_unique_id,
                                                                         'userId': userId,
                                                                         'productType': 'Entrance'}, {
                                                                            '$pull': {
                                                                                'bookmarks': question_no
                                                                            }
                                                                        })
                                else:
                                    bookmarks = []
                                    if log_type == "ENTRANCE_QUESTION_STAR":
                                        bookmarks.append(question_no)

                                    db.appuserlog_product.update_one({'uniqueId': product_unique_id,
                                                                     'userId': userId,
                                                                     'productType': 'Entrance'}, {
                                                                        '$set': {
                                                                            'bookmarks': bookmarks
                                                                        }
                                                                    })

                        elif log_type == "ENTRANCE_SHOW_NORMAL":
                            product_unique_id = item["extra"]["uniqueId"]

                            product_record = db.appuserlog_product.find_one({'uniqueId': product_unique_id,
                                                                             'userId': userId,
                                                                             'productType': 'Entrance'})

                            if product_record is None:
                                product_record = {
                                    'uniqueId': product_unique_id,
                                    'userId': userId,
                                    'productType': 'Entrance',
                                    'showNormalCount': 1
                                }
                                db.appuserlog_product.insert(product_record)

                            else:
                                count = 1
                                if 'showNormalCount' in product_record:
                                    count = product_record['showNormalCount'] + 1

                                db.appuserlog_product.update_one({'uniqueId': product_unique_id,
                                                                 'userId': userId,
                                                                 'productType': 'Entrance'}, {
                                                                    '$set': {
                                                                        'showNormalCount': count
                                                                    }
                                                                })

                        elif log_type == "ENTRANCE_SHOW_STARRED":
                            product_unique_id = item["extra"]["uniqueId"]

                            product_record = db.appuserlog_product.find_one({'uniqueId': product_unique_id,
                                                                             'userId': userId,
                                                                             'productType': 'Entrance'})

                            if product_record is None:
                                product_record = {
                                    'uniqueId': product_unique_id,
                                    'userId': userId,
                                    'productType': 'Entrance',
                                    'showStarredCount': 1
                                }
                                db.appuserlog_product.insert(product_record)

                            else:
                                count = 1
                                if 'showStarredCount' in product_record:
                                    count = product_record['showStarredCount'] + 1

                                db.appuserlog_product.update_one({'uniqueId': product_unique_id,
                                                                 'userId': userId,
                                                                 'productType': 'Entrance'}, {
                                                                    '$set': {
                                                                        'showStarredCount': count
                                                                    }
                                                                })

                        elif log_type == "ENTRANCE_LESSON_EXAM_FINISHED":
                            product_unique_id = item["extra"]["uniqueId"]
                            item2 = copy.deepcopy(item['extra'])
                            item2['time'] = item['time']

                            product_record = db.appuserlog_product.find_one({'uniqueId': product_unique_id,
                                                                             'userId': userId,
                                                                             'productType': 'Entrance'})

                            if product_record is None:
                                product_record = {
                                    'uniqueId': product_unique_id,
                                    'userId': userId,
                                    'productType': 'Entrance',
                                    'examFinished': []
                                }
                                product_record['examFinished'].append(item2)
                                db.appuserlog_product.insert(product_record)

                            else:
                                if 'examFinished' in product_record:
                                    db.appuserlog_product.update_one({'uniqueId': product_unique_id,
                                                                     'userId': userId,
                                                                     'productType': 'Entrance'}, {
                                                                        '$push': {
                                                                            'examFinished': item2
                                                                        }
                                                                    })

                                else:
                                    exams = []
                                    exams.append(item2)

                                    db.appuserlog_product.update_one({'uniqueId': product_unique_id,
                                                                     'userId': userId,
                                                                     'productType': 'Entrance'}, {
                                                                        '$set': {
                                                                            'examFinished': exams
                                                                        }
                                                                    })

                        elif log_type == "ENTRANCE_LAST_VISIT_INFO":
                            product_unique_id = item["extra"]["uniqueId"]

                            product_record = db.appuserlog_product.find_one({'uniqueId': product_unique_id,
                                                                             'userId': userId,
                                                                             'productType': 'Entrance'})

                            if product_record is None:
                                product_record = {
                                    'uniqueId': product_unique_id,
                                    'userId': userId,
                                    'productType': 'Entrance',
                                    'lastVisitInfo': item['extra']
                                }
                                db.appuserlog_product.insert(product_record)

                            else:
                                db.appuserlog_product.update_one({'uniqueId': product_unique_id,
                                                                 'userId': userId,
                                                                 'productType': 'Entrance'}, {
                                                                    '$set': {
                                                                        'lastVisitInfo': item['extra']
                                                                    }
                                                                })

                        elif log_type == "ENTRANCE_COMMENT_CREATE":
                            product_unique_id = item["extra"]["uniqueId"]
                            item2 = copy.deepcopy(item['extra'])
                            item2['time'] = item['time']

                            product_record = db.appuserlog_product.find_one({'uniqueId': product_unique_id,
                                                                             'userId': userId,
                                                                             'productType': 'Entrance'})

                            if product_record is None:
                                product_record = {
                                    'uniqueId': product_unique_id,
                                    'userId': userId,
                                    'productType': 'Entrance',
                                    'comments': []
                                }
                                product_record['comments'].append(item2)
                                db.appuserlog_product.insert(product_record)

                            else:
                                if 'comments' in product_record:
                                    db.appuserlog_product.update_one({'uniqueId': product_unique_id,
                                                                     'userId': userId,
                                                                     'productType': 'Entrance'}, {
                                                                        '$push': {
                                                                            'comments': item2
                                                                        }
                                                                    })

                                else:
                                    comments = []
                                    comments.append(item2)

                                    db.appuserlog_product.update_one({'uniqueId': product_unique_id,
                                                                     'userId': userId,
                                                                     'productType': 'Entrance'}, {
                                                                        '$set': {
                                                                            'comments': comments
                                                                        }
                                                                    })

                        elif log_type == "ENTRANCE_COMMENT_DELETE":
                            product_unique_id = item["extra"]["uniqueId"]
                            comment_id = item['extra']['commentId']

                            product_record = db.appuserlog_product.update_one({'uniqueId': product_unique_id,
                                                                             'userId': userId,
                                                                             'productType': 'Entrance'}, {
                                '$pull': {
                                    'comments': {
                                        'commentId': comment_id
                                    }
                                }
                            })


                    else:
                        result["records"].append(item["uniqueId"])
                        pass

                except Exception, exc:
                    print exc
                    pass


        else:
            result["status"] = "Error"
            result["error_type"] = "EmptyArray"

        return Response(result)


class UserLogViewSetOAuth(ScopedProtectedResourceView, UserLogViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["userlog"]


class UserLogViewSetJwt(UserLogViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)
