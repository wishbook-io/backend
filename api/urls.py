from django.conf.urls import url, include
from api import views
from api import tables
# from api.table import *
from rest_framework.routers import DefaultRouter
from exporthelpers import *
from push_notifications.api.rest_framework import GCMDeviceAuthorizedViewSet
from django.views.decorators.csrf import csrf_exempt


router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'userprofile', views.UserProfileViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'usernumbers', views.UserNumberViewSet)
router.register(r'choices', views.ChoiceViewSet)
router.register(r'companies', views.CompanyViewSet)
router.register(r'branches', views.BranchViewSet, base_name='branches')
router.register(r'companyusers', views.CompanyUserViewSet)
router.register(r'brands', views.BrandViewSet)
router.register(r'brandapp', views.BrandAppViewSet)
router.register(r'branddistributor', views.BrandDistributorViewSet)
router.register(r'catalogs', views.CatalogViewSet)
router.register(r'catalogapp', views.CatalogAppViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'buyers', views.BuyerViewSet, base_name='buyers')
router.register(r'sellers', views.SellerViewSet)
router.register(r'salesorders', views.SalesOrderViewSet, base_name='salesorders')
router.register(r'purchseorders', views.PurchaseOrderViewSet)
router.register(r'salesordersitems', views.SalesOrderItemViewSet, base_name='salesordersitems')
router.register(r'selections', views.SelectionViewSet)
router.register(r'channeltypes', views.ChannelTypeViewSet)
router.register(r'channels', views.ChannelViewSet)
router.register(r'pushes', views.PushViewSet)
router.register(r'pushuser', views.PushUserViewSet)
#router.register(r'pushresult', views.PushResultViewSet)
router.register(r'pushcatalog', views.PushCatalogViewSet)
router.register(r'pushproducts', views.PushProductViewSet)
router.register(r'pushselection', views.PushSelectionViewSet)
router.register(r'export', views.ExportViewSet)
router.register(r'exportresult', views.ExportResultViewSet)
router.register(r'exportcatalog', views.ExportCatalogViewSet)
router.register(r'exportproduct', views.ExportProductViewSet)
router.register(r'invites', views.InviteViewSet)
router.register(r'invitees', views.InviteeViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'messagefolders', views.MessageFolderViewSet)
router.register(r'meeting', views.MeetingViewSet)
router.register(r'buyersegmentation', views.BuyerSegmentationViewSet)
router.register(r'state', views.StateViewSet)
router.register(r'city', views.CityViewSet)
router.register(r'category', views.CategoryViewSet)
#router.register(r'maincategory', views.MainCategoryViewSet)
#router.register(r'subcategory', views.SubCategoryViewSet)
router.register(r'device/gcm', GCMDeviceAuthorizedViewSet)
router.register(r'invoice', views.InvoiceViewSet)
router.register(r'invoicecredit', views.InvoiceCreditViewSet)
router.register(r'registrationopt', views.RegistrationOTPViewSet)

urlpatterns = [
	url(r'^picasaimport/$',csrf_exempt(views.picasaImport)),
	
	
	url(r'^importcsvproduct/$',views.importCSVProduct),
	url(r'^importcsvcatalog/$',views.importCSVCatalog),
	url(r'^importcsvcompany/$',views.importCSVCompany),
	url(r'^importcsvbuyer/$',views.importCSVBuyer),
	url(r'^importcsvinvite/$',views.importCSVInvite),
	url(r'^importcsvsalesperson/$',views.importCSVSalesPerson),

	url(r'^ExportCSVUser/$',views.exportCSVUser),
	url(r'^ExportCSVChoice/$',views.exportCSVChoice),
	url(r'^ExportCSVCompany/$',views.exportCSVCompany),
	url(r'^ExportCSVBranch/$',views.exportCSVBranch),
	url(r'^ExportCSVCompanyUser/$',views.exportCSVCompanyUser),
	url(r'^ExportCSVBrand/$',views.exportCSVBrand),
	url(r'^ExportCSVCatalog/$',views.exportCSVCatalog),
	url(r'^ExportCSVProduct/$',views.exportCSVProduct),
	url(r'^ExportCSVBuyer/$',views.exportCSVBuyer),
	url(r'^ExportCSVSalesOrder/$',views.exportCSVSalesOrder),
	url(r'^ExportCSVSalesOrderItem/$',views.exportCSVSalesOrderItem),
	url(r'^ExportCSVSelection/$',views.exportCSVSelection),
	url(r'^ExportCSVChannelType/$',views.exportCSVChannelType),
	url(r'^ExportCSVChannel/$',views.exportCSVChannel),
	url(r'^ExportCSVPush/$',views.exportCSVPush),
	url(r'^ExportCSVExport/$',views.exportCSVExport),
	url(r'^ExportCSVInvite/$',views.exportCSVInvite),
	url(r'^ExportCSVSalesPerson/$',views.exportCSVSalesPerson),
	
	url(r'^resendinvite/$',views.resendInvite),
	url(r'^makebuyeroninviteregistration/$',views.makeBuyerOnInviteRegistration),
	url(r'^makedefaultsegmentation/$',views.makeDefaultSegmentation),
	url(r'^checkuserexist/$',views.checkUserExist),
	url(r'^checkotpandmobile/$',views.checkOTPandMobile),
	url(r'^apptable/$',views.appTable),
	
	
	url(r'^userdatatables/$',tables.UserDatatables.as_view()),
	url(r'^citydatatables/$',tables.CityDatatables.as_view()),
	url(r'^statedatatables/$',tables.StateDatatables.as_view()),
	url(r'^branddatatables/$',tables.BrandDatatables.as_view()),
	url(r'^companydatatables/$',tables.CompanyDatatables.as_view()),
	url(r'^branchdatatables/$',tables.BranchDatatables.as_view()),
	url(r'^categorydatatables/$',tables.CategoryDatatables.as_view()),
	url(r'^catalogdatatables/$',tables.CatalogDatatables.as_view()),
	url(r'^productdatatables/$',tables.ProductDatatables.as_view()),
	url(r'^buyerdatatables/$',tables.BuyerDatatables.as_view()),
	url(r'^sellerdatatables/$',tables.SellerDatatables.as_view()),
	url(r'^segmentationdatatables/$',tables.SegmentationDatatables.as_view()),
	url(r'^inviteedatatables/$',tables.InviteeDatatables.as_view()),
	url(r'^salespersondatatables/$',tables.SalesPersonDatatables.as_view()),
	url(r'^adminisratordatatables/$',tables.AdminisratorDatatables.as_view()),
	url(r'^pushdatatables/$',tables.PushDatatables.as_view()),
	url(r'^salesorderdatatables/$',tables.SalesOrderDatatables.as_view()),
	

	url(r'^messages/received/$', (views.ReceivedMessageList.as_view()), name='received-message-list'),
	url(r'^messages/received/(?P<pk>[0-9]+)/$', (views.ReceivedMessageDetail.as_view()), name='received-message-detail'),
	url(r'^messages/sent/$', (views.SentMessageList.as_view()), name='sent-message-list'),
	url(r'^messages/sent/(?P<pk>[0-9]+)/$', (views.SentMessageDetail.as_view()), name='sent-message-detail'),
	
	#function
	#url(r'^buyersegmentation/peopletargeted/(?P<pk>[0-9]+)/$', views. PeopleTargetedView.as_view(), name='people-targeted'),

	url(r'^', include(router.urls)),

	# url(r'^UserDatatable/$', (UserDatatable.as_view())),
	# url(r'^User_NumberDatatable/$', (User_NumberDatatable.as_view())),
	# url(r'^CompanyDatatable/$', (CompanyDatatable.as_view())),
	# url(r'^Company_UserDatatable/$', (Company_UserDatatable.as_view())),
	# url(r'^BuyerDatatable/$', (BuyerDatatable.as_view())),
	# url(r'^BrandDatatable/$', (BrandDatatable.as_view())),
	# url(r'^CatalogDatatable/$', (CatalogDatatable.as_view())),
	# url(r'^Sales_OrderDatatable/$', (Sales_OrderDatatable.as_view())),
	# url(r'^ProductDatatable/$', (ProductDatatable.as_view())),
	# url(r'^Sales_Order_ItemDatatable/$', (Sales_Order_ItemDatatable.as_view())),
	# url(r'^SelectionDatatable/$', (SelectionDatatable.as_view())),
	# url(r'^Selection_ProductDatatable/$', (Selection_ProductDatatable.as_view())),
	# url(r'^Channel_TypeDatatable/$', (Channel_TypeDatatable.as_view())),
	# url(r'^ChannelDatatable/$', (ChannelDatatable.as_view())),
	# url(r'^PushDatatable/$', (PushDatatable.as_view())),
	# url(r'^Push_UserDatatable/$', (Push_UserDatatable.as_view())),
	# url(r'^Push_ResultDatatable/$', (Push_ResultDatatable.as_view())),
	# url(r'^Push_CatalogDatatable/$', (Push_CatalogDatatable.as_view())),
	# url(r'^Push_ProductDatatable/$', (Push_ProductDatatable.as_view())),
	# url(r'^ExportDatatable/$', (ExportDatatable.as_view())),
	# url(r'^Export_ResultDatatable/$', (Export_ResultDatatable.as_view())),
	# url(r'^Export_CatalogDatatable/$', (Export_CatalogDatatable.as_view())),
	# url(r'^Export_ProductDatatable/$', (Export_ProductDatatable.as_view())),
	# url(r'^ChoiceListDatatable/$', (ChoiceListDatatable.as_view())),
	# url(r'^ChoiceList_UserDatatable/$', (ChoiceList_UserDatatable.as_view())),
	# url(r'^InviteDatatable/$', (InviteDatatable.as_view())),
	# url(r'^InviteeDatatable/$', (InviteeDatatable.as_view())),
]
