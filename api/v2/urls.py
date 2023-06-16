from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from api.v2.views import activity_views, media_views, auth_views, profile_views,\
    archive_views, entrance_views, purchase_views, product_views, basket_views, settings_views, wallet_views, userlog_views

__author__ = 'abolfazl'

urlpatterns = (url(r'^activities/next/(?P<last>[-TZ:.\d]+)/?$',
                   activity_views.ActivityViewSetOauth.as_view({'get': "next_page"})),
               url(r'^activities/?$', activity_views.ActivityViewSetOauth.as_view({'get': "list"})),
               url(r'^media/eset/(?P<pk>\d+)/?$', media_views.MediaEsetViewSetOauth.as_view()),
               url(r'^media/org/(?P<pk>\d+)/?$', media_views.MediaOrgViewSetOauth.as_view()),

               # Authentication
               url(r'^auth/check_username/$', auth_views.AuthPreCheckUsernameViewSet.as_view({'post': 'post'})),
               url(r'^auth/signup/$', auth_views.AuthPreSignupCodeViewSet.as_view({'post': 'post'})),
               url(r'^auth/pre_signup/$', auth_views.AuthPreSignupViewSet.as_view({'post': 'post'})),
               url(r'^auth/reset_password/$', auth_views.AuthForgotPasswordResetViewSet.as_view({'post': 'post'})),
               url(r'^auth/forgot_password/$', auth_views.AuthForgotPasswordViewSet.as_view({'post': 'post'})),
               url(r'^auth/change_password/$', auth_views.AuthChangePasswordViewSetOAuth.as_view({'post': 'post'})),

               # Profile
               url(r'^profile/grade/list/?$', profile_views.AuthProfileViewSetOAuth.as_view({"get": "list_grade"})),
               url(r'^profile/edit/grade/$', profile_views.AuthProfileViewSetOAuth.as_view({"put": "update_grade"})),
               url(r'^profile/$', profile_views.AuthProfileViewSetOAuth.as_view({"get": "get",
                                                                               "post": "post",
                                                                               "put": "update"})),

               # Archive urls
               url(r'^archive/entrance/types', archive_views.EntranceTypeViewSetOAuth.as_view({"get": "list"})),
               url(r'^archive/entrance/groups/(?P<etype>\d+)/$', archive_views.ExaminationGroupViewSetOAuth.as_view({"get": "list"})),
               url(r'^archive/entrance/sets/(?P<egroup>\d+)/$', archive_views.EntranceSetViewSetOAuth.as_view({"get": "list"})),
               url(r'^archive/entrance/(?P<eset>\d+)/$', archive_views.EntrancesViewSetOAuth.as_view({"get": "list"})),

               # Entrance
               url(r'^entrance/tags/(?P<unique_id>[0-9a-fA-F]{32})/?$',
                   entrance_views.EntranceLessonTagsViewSetOAuth.as_view({"get": "get"})),
               url(r'^entrance/tags/(?P<unique_id>[0-9a-fA-F]*)/data/?$',
                   entrance_views.EntranceLessonTagsViewSetOAuth.as_view({"get": "getPackage"})),
               url(r'^entrance/(?P<unique_id>[0-9a-fA-F]{32})/$',
                   entrance_views.EntranceViewSetOAuth.as_view({"get": "get"})),
               url(r'^entrance/(?P<unique_id>[0-9a-fA-F]*)/data/init/$',
                   entrance_views.EntranceViewSetOAuth.as_view({"get": "getPackageInit"})),

               # Purchase Urls
               url(r'^purchased/entrance/tags/(?P<unique_id>[0-9a-fA-F]{32})/?$',
                   purchase_views.UserPurchaseViewSetOAuth.as_view({"get": "getEntranceLessonTags"})),
               url(r'^purchased/entrance/(?P<unique_id>[0-9a-fA-F]{32})/$',
                   purchase_views.UserPurchaseViewSetOAuth.as_view({"get": "getEntrance"})),
               url(r'^purchased/entrance/(?P<unique_id>[0-9a-fA-F]{32})/update/$',
                   purchase_views.UserPurchaseViewSetOAuth.as_view({"put": "putDownloadPlus"})),
               url(r'^purchased/list/$',
                   purchase_views.UserPurchaseViewSetOAuth.as_view({"get": "getAllPurhases"})),

               # Product Urls
               url(r'^product/entrance/(?P<unique_id>[0-9a-fA-F]{32})/tags/(?P<bid>\d+)/?$',
                   product_views.ProductDataViewSetOAuth.as_view({"get": "getEntranceTagsData"})),
               url(r'^product/entrance_multi/(?P<unique_id>[0-9a-fA-F]{32})/sale/?$',
                   product_views.ProductDataViewSetOAuth.as_view({"get": "getEntranceMultiSale"})),
               url(r'^product/entrance/(?P<unique_id>[0-9a-fA-F]{32})/stat_and_sale/$',
                   product_views.ProductDataViewSetOAuth.as_view({"get": "getEntranceSaleAndStat"})),
               url(r'^product/entrance/(?P<unique_id>[0-9a-fA-F]{32})/sale/$',
                   product_views.ProductDataViewSetOAuth.as_view({"get": "getEntranceSale"})),
               url(r'^product/entrance/(?P<unique_id>[0-9a-fA-F]{32})/stat/$',
                   product_views.ProductDataViewSetOAuth.as_view({"get": "getEntranceStat"})),
               url(r'^product/entrance_multi/(?P<unique_id>[0-9a-fA-F]{32})/sale/$',
                   product_views.ProductDataViewSetOAuth.as_view({"get": "getEntranceMultiSale"})),
               url(r'^product/add_to_lib/$',
                   product_views.ProductPurchaseViewSetOAuth.as_view({"post": "addToLibrary"})),

               url(r'^media/entrance/(?P<uid>[0-9a-fA-F]{32})/q/bulk/?$',
                   media_views.MediaQuestionBulkViewSetOauth.as_view()),
               url(r'^media/entrance/(?P<uid>[0-9a-fA-F]{32})/q/(?P<qid>[0-9a-fA-F]{32})/$',
                   media_views.MediaQuestionViewSetOauth.as_view()),

               # wallet Urls
               url(r'^wallet/info/$',
                   wallet_views.WalletViewSetOAuth.as_view({"get": "create"})),

               # Basket Urls
               url(r'^basket/list/$',
                   basket_views.BasketViewSetOAuth.as_view({"get": "listSales"})),
               url(r'^basket/create/$',
                   basket_views.BasketViewSetOAuth.as_view({"post": "createBasket"})),
               url(r'^basket/add/$',
                   basket_views.BasketViewSetOAuth.as_view({"post": "postProductInBasket"})),
               url(r'^basket/checkout/verify/?$',
                   basket_views.BasketViewSetOAuth.as_view({"post": "verifyCheckout"})),
               url(r'^basket/(?P<basket_uid>[0-9a-fA-F]{32})/add/$',
                   basket_views.BasketViewSetOAuth.as_view({"put": "putProductInBasket"})),
               url(r'^basket/(?P<basket_uid>[0-9a-fA-F]{32})/sale/(?P<sale_id>\d+)/$',
                   basket_views.BasketViewSetOAuth.as_view({"delete": "removeProductFormBasket"})),
               url(r'^basket/(?P<basket_uid>[0-9a-fA-F]{32})/checkout/$',
                   basket_views.BasketViewSetOAuth.as_view({"post": "checkoutBasket"})),

               # Settings Urls
               url(r'^invite/$',
                   settings_views.InviteFriendsViewSetOAuth.as_view({"post": "post"})),
               url(r'^report_bug/$', settings_views.ReportBugsViewSetOAuth.as_view({'post': 'post'})),
               url(r'^app_version/(?P<device>\w+)/?$', settings_views.CheckVersionViewSetOAuth.as_view({'get': 'get'})),

               # Devices Urls
               url(r'^device/create/?$', auth_views.AuthUserRegisteredDevicesViewSetOAuth.as_view({'post': 'create'})),
               url(r'^device/lock/?$', auth_views.AuthUserRegisteredDevicesViewSetOAuth.as_view({'post': 'lock'})),
               url(r'^device/acquire/?$', auth_views.AuthUserRegisteredDevicesViewSetOAuth.as_view({'post': 'acquire'})),
               url(r'^device/state/?$',
                   auth_views.AuthUserRegisteredDevicesViewSetOAuth.as_view({'post': 'state'})),

               url(r'^userlog/?$', userlog_views.UserLogViewSetOAuth.as_view({'post': 'sync'})),


               # JWT SECTION ===============================================
               # jwt authentications
               url(r'jauth/token/?$', obtain_jwt_token),
               url(r'jauth/refresh_token/?$', refresh_jwt_token),
               url(r'jauth/verify/?$', verify_jwt_token),

               # Authentication
               url(r'^j/auth/check_username/$', auth_views.AuthPreCheckUsernameViewSet.as_view({'post': 'post'})),
               url(r'^j/auth/signup/$', auth_views.AuthPreSignupCodeViewSet.as_view({'post': 'post'})),
               url(r'^j/auth/pre_signup/$', auth_views.AuthPreSignupViewSet.as_view({'post': 'post'})),
               url(r'^j/auth/reset_password/$', auth_views.AuthForgotPasswordResetViewSet.as_view({'post': 'post'})),
               url(r'^j/auth/forgot_password/$', auth_views.AuthForgotPasswordViewSet.as_view({'post': 'post'})),
               url(r'^j/auth/change_password/$', auth_views.AuthChangePasswordViewSetJwt.as_view({'post': 'post'})),

               # Profile
               url(r'^j/profile/grade/list/?$', profile_views.AuthProfileViewSetJwt.as_view({"get": "list_grade"})),
               url(r'^j/profile/edit/grade/$', profile_views.AuthProfileViewSetJwt.as_view({"put": "update_grade"})),
               url(r'^j/profile/$', profile_views.AuthProfileViewSetJwt.as_view({"get": "get",
                                                                                    "post": "post",
                                                                                    "put": "update"})),
               # data and media
               url(r'^j/activities/next/(?P<last>[-TZ:.\d]+)/?$',
                   activity_views.ActivityViewSetJwt.as_view({'get': "next_page"})),
               url(r'^j/activities/?$', activity_views.ActivityViewSetJwt.as_view({'get': "list"})),
               url(r'^j/media/eset/(?P<pk>\d+)/?$', media_views.MediaEsetViewSetJwt.as_view()),
               url(r'^j/media/org/(?P<pk>\d+)/?$', media_views.MediaOrgViewSetJwt.as_view()),

               # Archive urls
               url(r'^j/archive/entrance/types', archive_views.EntranceTypeViewSetJwt.as_view({"get": "list"})),
               url(r'^j/archive/entrance/groups/(?P<etype>\d+)/$',
                   archive_views.ExaminationGroupViewSetJwt.as_view({"get": "list"})),
               url(r'^j/archive/entrance/sets/(?P<egroup>\d+)/$',
                   archive_views.EntranceSetViewSetJwt.as_view({"get": "list"})),
               url(r'^j/archive/entrance/(?P<eset>\d+)/$', archive_views.EntrancesViewSetJwt.as_view({"get": "list"})),

               # Entrance
               url(r'^j/entrance/tags/(?P<unique_id>[0-9a-fA-F]{32})/?$',
                   entrance_views.EntranceLessonTagsViewSetJwt.as_view({"get": "get"})),
               url(r'^j/entrance/tags/(?P<unique_id>[0-9a-fA-F]*)/data/?$',
                   entrance_views.EntranceLessonTagsViewSetJwt.as_view({"get": "getPackage"})),
               url(r'^j/entrance/(?P<unique_id>[0-9a-fA-F]*)/$', entrance_views.EntranceViewSetJwt.as_view({"get": "get"})),
               url(r'^j/entrance/(?P<unique_id>[0-9a-fA-F]*)/data/init/$',
                   entrance_views.EntranceViewSetJwt.as_view({"get": "getPackageInit"})),

               # Purchase Urls
               url(r'^j/purchased/entrance/tags/(?P<unique_id>[0-9a-fA-F]{32})/?$',
                   purchase_views.UserPurchaseViewSetJwt.as_view({"get": "getEntranceLessonTags"})),
               url(r'^j/purchased/entrance/(?P<unique_id>[0-9a-fA-F]{32})/$',
                   purchase_views.UserPurchaseViewSetJwt.as_view({"get": "getEntrance"})),
               url(r'^j/purchased/entrance/(?P<unique_id>[0-9a-fA-F]{32})/update/$',
                   purchase_views.UserPurchaseViewSetJwt.as_view({"put": "putDownloadPlus"})),
               url(r'^j/purchased/list/$',
                   purchase_views.UserPurchaseViewSetJwt.as_view({"get": "getAllPurhases"})),


               # Product Urls
               url(r'^j/product/entrance/(?P<unique_id>[0-9a-fA-F]{32})/tags/(?P<bid>\d+)/?$',
                   product_views.ProductDataViewSetJwt.as_view({"get": "getEntranceTagsData"})),
               url(r'^j/product/entrance_multi/(?P<unique_id>[0-9a-fA-F]{32})/sale/?$',
                   product_views.ProductDataViewSetJwt.as_view({"get": "getEntranceMultiSale"})),
               url(r'^j/product/entrance/(?P<unique_id>[0-9a-fA-F]{32})/stat_and_sale/$',
                   product_views.ProductDataViewSetJwt.as_view({"get": "getEntranceSaleAndStat"})),
               url(r'^j/product/entrance/(?P<unique_id>[0-9a-fA-F]{32})/sale/$',
                   product_views.ProductDataViewSetJwt.as_view({"get": "getEntranceSale"})),
               url(r'^j/product/entrance/(?P<unique_id>[0-9a-fA-F]{32})/stat/$',
                   product_views.ProductDataViewSetJwt.as_view({"get": "getEntranceStat"})),
               url(r'^j/media/entrance/(?P<uid>[0-9a-fA-F]{32})/qs/bulk/?$',
                   media_views.MediaQuestionBulkViewSetJwt.as_view()),
               url(r'^j/media/entrance/(?P<uid>[0-9a-fA-F]{32})/q/(?P<qid>[0-9a-fA-F]{32})/$',
                   media_views.MediaQuestionViewSetJwt.as_view()),
               url(r'^j/product/add_to_lib/$',
                   product_views.ProductPurchaseViewSetJwt.as_view({"post": "addToLibrary"})),

                # wallet Urls
               url(r'^j/wallet/info/$',
                   wallet_views.WalletViewSetJwt.as_view({"get": "create"})),

               # Basket Urls
               url(r'^j/basket/list/$',
                   basket_views.BasketViewSetJwt.as_view({"get": "listSales"})),
               url(r'^j/basket/create/$',
                   basket_views.BasketViewSetJwt.as_view({"post": "createBasket"})),
               url(r'^j/basket/add/$',
                   basket_views.BasketViewSetJwt.as_view({"post": "postProductInBasket"})),
               url(r'^j/basket/checkout/verify/?$',
                   basket_views.BasketViewSetJwt.as_view({"post": "verifyCheckout"})),
               url(r'^j/basket/(?P<basket_uid>[0-9a-fA-F]{32})/add/$',
                   basket_views.BasketViewSetJwt.as_view({"put": "putProductInBasket"})),
               url(r'^j/basket/(?P<basket_uid>[0-9a-fA-F]{32})/sale/(?P<sale_id>\d+)/$',
                   basket_views.BasketViewSetJwt.as_view({"delete": "removeProductFormBasket"})),
               url(r'^j/basket/(?P<basket_uid>[0-9a-fA-F]{32})/checkout/$',
                   basket_views.BasketViewSetJwt.as_view({"post": "checkoutBasket"})),

                # Settings Urls
                url(r'^j/invite/$',
                    settings_views.InviteFriendsViewSetJwt.as_view({"post": "post"})),
               url(r'^j/report_bug/$', settings_views.ReportBugsViewSetJwt.as_view({'post': 'post'})),
               url(r'^j/app_version/(?P<device>\w+)/?$', settings_views.CheckVersionViewSetJwt.as_view({'get': 'get'})),

               # Devices Urls
               url(r'^j/device/create/?$', auth_views.AuthUserRegisteredDevicesViewSetJwt.as_view({'post': 'create'})),
               url(r'^j/device/lock/?$', auth_views.AuthUserRegisteredDevicesViewSetJwt.as_view({'post': 'lock'})),
               url(r'^j/device/acquire/?$',
                   auth_views.AuthUserRegisteredDevicesViewSetJwt.as_view({'post': 'acquire'})),
               url(r'^j/device/state/?$',
                   auth_views.AuthUserRegisteredDevicesViewSetJwt.as_view({'post': 'state'})),

               url(r'^j/userlog/?$', userlog_views.UserLogViewSetJwt.as_view({'post': 'sync'})),

               )
