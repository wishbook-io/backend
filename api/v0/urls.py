from django.conf.urls import url, include
from api.v0 import views
#from api.v0.dropdown import views as dropdownviews
from api import tables
# from api.table import *
from rest_framework.routers import DefaultRouter
#from exporthelpers import *
from push_notifications.api.rest_framework import GCMDeviceAuthorizedViewSet, APNSDeviceAuthorizedViewSet
from django.views.decorators.csrf import csrf_exempt

from api import tbl

router = DefaultRouter()

router.register(r'device/apns', APNSDeviceAuthorizedViewSet)
router.register(r'device/gcm', GCMDeviceAuthorizedViewSet)

router.register(r'buyers', views.BuyerViewSet, base_name='buyers')

urlpatterns = [

	url(r'^sharedbyme/$', views.SharedByMe.as_view()),
	url(r'^sharedwithme/$', views.SharedWithMe.as_view()),
	
	url(r'^branddatatables1/$',tbl.BrandDatatables.as_view()),
	url(r'^companydatatables1/$',tbl.CompanyDatatables.as_view()),
	url(r'^orderdatatables1/$',tbl.OrderDatatables.as_view()),
	url(r'^companybuyersupplierdatatables1/$',tbl.CompanyBuyerSupplierDatatables.as_view()),
	url(r'^companypendingbuyersupplierdatatables1/$',tbl.CompanyPendingBuyerSupplierDatatables.as_view()),
	url(r'^branchdatatables1/$',tbl.BranchDatatables.as_view()),
	#url(r'^categorydatatables1/$',tbl.CategoryDatatables.as_view()),
	url(r'^catalogdatatables1/$',tbl.CatalogDatatables.as_view()),
	url(r'^catalogadmindatatables/$',tbl.CatalogAdminDatatables.as_view()),
	url(r'^receivedcatalogdatatables1/$',tbl.ReceivedCatalogDatatables.as_view()),
	url(r'^publiccatalogdatatables1/$',tbl.PublicCatalogDatatables.as_view()),
	url(r'^receivedselectiondatatables1/$',tbl.ReceivedSelectionDatatables.as_view()),
	url(r'^selectiondatatables1/$',tbl.SelectionDatatables.as_view()),
	url(r'^productdatatables1/$',tbl.ProductDatatables.as_view()),
	url(r'^productsdetaildatatables1/$',tbl.ProductsDetailDatatables.as_view()),
	url(r'^buyerdatatables1/$',tbl.BuyerDatatables.as_view()),
	url(r'^buyerenquirydatatables1/$',tbl.BuyerEnquiryDatatables.as_view()),
	url(r'^sellerenquirydatatables1/$',tbl.SellerEnquiryDatatables.as_view()),
	url(r'^sellerdatatables1/$',tbl.SellerDatatables.as_view()),
	url(r'^segmentationdatatables1/$',tbl.SegmentationDatatables.as_view()),
	#url(r'^inviteedatatables1/$',tbl.InviteeDatatables.as_view()),
	url(r'^salespersondatatables1/$',tbl.SalesPersonDatatables.as_view()),
	url(r'^adminisratordatatables1/$',tbl.AdminisratorDatatables.as_view()),
	url(r'^pushdatatables1/$',tbl.PushDatatables.as_view()),
	url(r'^salesorderdatatables1/$',tbl.SalesOrderDatatables.as_view()),
	url(r'^purchaseorderdatatables1/$',tbl.PurchaseDatatables.as_view()),
	url(r'^companyphonealiasdatatables1/$',tbl.CompanyPhoneAliasDatatables.as_view()),
	url(r'^companybuyergroupdatatables1/$',tbl.CompanyBuyerGroupDatatables.as_view()),
	url(r'^inventorydatatables1/$',tbl.InventoryDatatables.as_view()),
	url(r'^skumapdatatables1/$',tbl.SKUMapDatatables.as_view()),
	url(r'^stockdatatables1/$',tbl.StockDatatables.as_view()),
	url(r'^orderdetaildatatables1/$',tbl.OrderDetailDatatables.as_view()),
	url(r'^meetingdatatables1/$',tbl.MeetingDatatables.as_view()),
	url(r'^attendancedatatables/$',tbl.AttendanceDatatables.as_view()),
	url(r'^companyaccountdatatables/$',tbl.CompanyAccountDatatables.as_view()),
	url(r'^salesorderinvoicedatatables/$',tbl.SalesOrderInvoiceDatatables.as_view()),
	url(r'^purchaseorderinvoicedatatables/$',tbl.PurchaseOrderInvoiceDatatables.as_view()),
	url(r'^brokerageorderdatatables/$',tbl.BrokerageOrderDatatables.as_view()),
	
	url(r'^jobsdatatables/$',tbl.JobsDatatables.as_view()),
	url(r'^salesmanlocationdatatables/$',tbl.SalesmanLocationDatatables.as_view()),
	url(r'^buyersalesmendatatables/$',tbl.BuyerSalesmenDatatables.as_view()),
	url(r'^brandownsaledatatables/$',tbl.BrandOwnSaleDatatables.as_view()),
	url(r'^warehousedatatables/$',tbl.WarehouseDatatables.as_view()),
	url(r'^brandscatalogdatatables/$',tbl.BrandsCatalogDatatables.as_view()),
	url(r'^openingstockdatatables/$',tbl.OpeningStockDatatables.as_view()),
	url(r'^inventoryadjustmentdatatables/$',tbl.InventoryAdjustmentDatatables.as_view()),
	url(r'^pushbuyerdetaildatatables/$',tbl.PushBuyerDetailDatatables.as_view()),
	url(r'^pushproductdetaildatatables/$',tbl.PushProductDetailDatatables.as_view()),
	
	url(r'^buyermeetingdatatables/$',tbl.BuyerMeetingDatatables.as_view()),
	
	url(r'^marketingdatatables/$',tbl.MarketingDatatables.as_view()),
	
	url(r'^sellerstatisticdatatables/$',tbl.SellerStatisticDatatables.as_view()),
	
	url(r'^myenquirydatatables/$',tbl.MyEnquiryDatatables.as_view()),
	url(r'^myleaddatatables/$',tbl.MyLeadDatatables.as_view()),
	
	url(r'^', include(router.urls)),
	
	
]
