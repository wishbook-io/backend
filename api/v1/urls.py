from django.conf.urls import url, include
from api.v1 import views
from api.v1.order import views as orderviews
from rest_framework.routers import DefaultRouter

from rest_framework_nested import routers

from push_notifications.api.rest_framework import GCMDeviceAuthorizedViewSet, APNSDeviceAuthorizedViewSet
from api.notification.notification_views import *



companies = routers.SimpleRouter()
companies.register(r'companies', views.CompanyViewSet)

nestedcompanies = routers.NestedSimpleRouter(companies, r'companies', lookup='companies')
nestedcompanies.register(r'users', views.UserViewSet, base_name='companies-users')
nestedcompanies.register(r'user-platform', views.UserPlatformInfoViewSet, base_name='companies-user-platform')
nestedcompanies.register(r'brands', views.BrandViewSet, base_name='companies-brands')
nestedcompanies.register(r'catalogs', views.CatalogViewSet, base_name='companies-catalogs')
nestedcompanies.register(r'buyers', views.BuyerViewSet, base_name='companies-buyers')
nestedcompanies.register(r'suppliers', views.SupplierViewSet, base_name='companies-suppliers')
nestedcompanies.register(r'sales-orders', views.SalesOrderViewSet, base_name='companies-sales-orders')
nestedcompanies.register(r'sales-order-items', views.SalesOrderItemViewSet, base_name='companies-sales-order-items')
nestedcompanies.register(r'purchase-orders', views.PurchaseOrderViewSet, base_name='companies-purchase-orders')
nestedcompanies.register(r'purchase-order-items', views.PurchaseOrderItemViewSet, base_name='companies-purchase-order-items')
nestedcompanies.register(r'brokerage-orders', views.BrokerageOrderViewSet, base_name='companies-brokerage-orders')

nestedcompanies.register(r'catalog-enquiries', views.CatalogEnquiryViewSet, base_name='companies-catalog-enquiries')

nestedcompanies.register(r'invoice', views.WishbookInvoiceViewSet, base_name='companies-invoice')
nestedcompanies.register(r'credit', views.WishbookCreditViewSet, base_name='companies-credit')
nestedcompanies.register(r'payment', views.WishbookPaymentViewSet, base_name='companies-payment')
nestedcompanies.register(r'aliases', views.CompanyPhoneAliasViewSet, base_name='companies-aliases')
nestedcompanies.register(r'price-list', views.CompanyPriceListViewSet, base_name='companies-price-list')
nestedcompanies.register(r'group-types', views.CompanyBuyerGroupViewSet, base_name='companies-group-types')
nestedcompanies.register(r'buyer-groups', views.BuyerSegmentationViewSet, base_name='companies-buyer-groups')
nestedcompanies.register(r'types', views.CompanyTypeListViewSet, base_name='companies-types')
nestedcompanies.register(r'brand-distributor', views.BrandDistributorViewSet, base_name='companies-brand-distributor')
nestedcompanies.register(r'order-invoice', views.InvoiceViewSet, base_name='companies-order-invoice')
nestedcompanies.register(r'company-catalog-view', views.CompanyCatalogViewViewSet, base_name='companies-company-catalog-view')
nestedcompanies.register(r'kyc', views.CompanyKycTaxationViewSet, base_name='companies-kyc')
nestedcompanies.register(r'shipments', views.ShipmentViewSet, base_name='companies-shipments')
nestedcompanies.register(r'order-rating', views.OrderRatingViewSet, base_name='companies-order-rating')
nestedcompanies.register(r'brand-follow', views.CompanyBrandFollowViewSet, base_name='companies-brand-follow')
nestedcompanies.register(r'approved-credit', views.ApprovedCreditViewSet, base_name='companies-approved-credit')
nestedcompanies.register(r'loan', views.LoanViewSet, base_name='companies-loan')
nestedcompanies.register(r'address', views.AddressViewSet, base_name='companies-address')
nestedcompanies.register(r'catalog-seller', views.CatalogSellerViewSet, base_name='companies-catalog-seller')
nestedcompanies.register(r'credit-rating', views.CompanyCreditRatingViewSet, base_name='companies-credit-rating')
nestedcompanies.register(r'user-credit-submissions', views.UserCreditSubmissionViewSet, base_name='companies-user-credit-submissions')
nestedcompanies.register(r'credit-reference', views.CreditReferenceViewSet, base_name='companies-credit-reference')
nestedcompanies.register(r'solo-propreitorship-kyc', views.SolePropreitorshipKYCViewSet, base_name='companies-solo-propreitorship-kyc')

nestedcompanies.register(r'carts', orderviews.CartViewSet, base_name='companies-carts')
nestedcompanies.register(r'cart-items', orderviews.CartItemViewSet, base_name='companies-cart-items')
#nestedcompanies.register(r'cart-payments', orderviews.CartPaymentViewSet, base_name='companies-cart-payment')
nestedcompanies.register(r'bank-details', views.CompanyBankDetailsViewSet, base_name='companies-bank-details')


catalogs = routers.SimpleRouter()
catalogs.register(r'catalogs', views.CatalogViewSet)

nestedcatalogs = routers.NestedSimpleRouter(catalogs, r'catalogs', lookup='catalogs')
nestedcatalogs.register(r'products', views.ProductViewSet, base_name='catalogs-products')
nestedcatalogs.register(r'upload-options', views.CatalogUploadOptionViewSet, base_name='catalogs-upload-options')



users = routers.SimpleRouter()
users.register(r'users', views.UserViewSet)

nestedusers = routers.NestedSimpleRouter(users, r'users', lookup='users')
nestedusers.register(r'meetings', views.MeetingViewSet, base_name='users-meetings')
nestedusers.register(r'attendance', views.AttendanceViewSet, base_name='users-attendance')
nestedusers.register(r'salesmanlocation', views.SalesmanLocationViewSet, base_name='users-salesman-location')
nestedusers.register(r'buyersalesmen', views.BuyerSalesmenViewSet, base_name='users-buyer-salesmen')
nestedusers.register(r'assigngroups', views.AssignGroupsViewSet, base_name='users-assign-groups')
nestedusers.register(r'platform', views.UserPlatformInfoViewSet, base_name='users-platform')
nestedusers.register(r'wishlist', views.UserWishlistViewSet, base_name='users-wishlist')
nestedusers.register(r'viewfollowers', views.ViewFollowerViewSet, base_name='view-followers')

products = routers.SimpleRouter()
products.register(r'products', views.ProductViewSet)

nestedproducts = routers.NestedSimpleRouter(products, r'products', lookup='products')
nestedproducts.register(r'likes', views.ProductLikeViewSet, base_name='products-likes')


brands = routers.SimpleRouter()
brands.register(r'brands', views.BrandViewSet)

nestedbrands = routers.NestedSimpleRouter(brands, r'brands', lookup='brands')
#nestedbrands.register(r'distributor', views.BrandDistributorViewSet, base_name='brands-likes')




router = DefaultRouter()

router.register(r'device/apns', APNSDeviceAuthorizedViewSet)
router.register(r'device/gcm', GCMDeviceAuthorizedViewSet)

#router.register(r'companies', views.CompanyViewSet)
#router.register(r'users', views.UserViewSet)

router.register(r'catalog-lists', views.CatalogListViewSet)
router.register(r'meetings', views.MeetingViewSet)
router.register(r'attendance', views.AttendanceViewSet)
router.register(r'selections', views.SelectionViewSet)
router.register(r'shares', views.PushViewSet)
router.register(r'country', views.CountryViewSet)
router.register(r'state', views.StateViewSet)
router.register(r'city', views.CityViewSet)
router.register(r'category', views.CategoryViewSet)
router.register(r'group-types', views.GroupTypeViewSet)
router.register(r'warehouse', views.WarehouseV1ViewSet, base_name='warehouse')






router.register(r'app', views.AppV1ViewSet)
router.register(r'app/(?P<app_id>\d+)/instance', views.AppMapInstanceV1ViewSet)
router.register(r'appinstance', views.AppInstanceV1ViewSet)
router.register(r'skumap', views.SKUMapV1ViewSet)
#router.register(r'skumap/sku/(?P<sku>\d+)', views.SKUMapSkuV1ViewSet)
#router.register(r'salesorders', views.SalesOrderV1ViewSet, base_name='salesorders')
#router.register(r'salesordersitems', views.SalesOrderItemV1ViewSet, base_name='salesordersitems')
#router.register(r'purchseorders', views.PurchaseOrderV1ViewSet, base_name='purchseorders')
#router.register(r'purchseordersitems', views.PurchaseOrderItemV1ViewSet, base_name='purchseordersitems')
#router.register(r'warehouse', views.WarehouseV1ViewSet, base_name='warehouse')
router.register(r'inventory', views.StockV1ViewSet, base_name='inventory')
router.register(r'barcode', views.BarcodeV1ViewSet, base_name='barcode')
router.register(r'openingstock', views.OpeningStockViewSet)
router.register(r'openingstockqty', views.OpeningStockQtyViewSet)
router.register(r'inventoryadjustment', views.InventoryAdjustmentViewSet)
router.register(r'inventoryadjustmentqty', views.InventoryAdjustmentQtyViewSet)
router.register(r'companyaccount', views.CompanyAccountViewSet)
router.register(r'promotion', views.PromotionViewSet)
router.register(r'promotions', views.PromotionViewSet)
router.register(r'user-reviews', views.UserReviewViewSet)
router.register(r'promotional-tags', views.PromotionalTagViewSet)
router.register(r'predefined-filters', views.PreDefinedFilterViewSet)

router.register(r'salesmanlocation', views.SalesmanLocationViewSet)
router.register(r'buyersalesmen', views.BuyerSalesmenViewSet)
router.register(r'assigngroups', views.AssignGroupsViewSet)

router.register(r'catalog-upload-options', views.CatalogUploadOptionViewSet)
router.register(r'order-rating', views.OrderRatingViewSet)

router.register(r'company-brand-follow', views.CompanyBrandFollowViewSet)

router.register(r'approved-credit', views.ApprovedCreditViewSet)
router.register(r'loan', views.LoanViewSet)

router.register(r'buyer-discount', views.CompanyBuyerGroupViewSet)
router.register(r'payment-method', views.PaymentMethodViewSet)

router.register(r'discount-rule', views.DiscountRuleViewSet)
#router.register(r'discount-rule-brand', views.DiscountRuleBrandViewSet)
#router.register(r'discount-rule-buyer-group', views.DiscountRuleBuyerGroupViewSet)



router.register(r'config', views.ConfigViewSet)
router.register(r'address', views.AddressViewSet)

router.register(r'brokerage-orders', views.BrokerageOrderViewSet)
router.register(r'languages', views.LanguageViewSet)

router.register(r'category-eav-attribute', views.CategoryEavAttributeViewSet)
router.register(r'company-sells-to-state', views.CompanySellsToStateViewSet)
router.register(r'catalog-seller', views.CatalogSellerViewSet)
router.register(r'catalog-seller-admin', views.CatalogSellerAdminViewSet)

router.register(r'action-log', views.ActionLogViewSet)
router.register(r'user-saved-filter', views.UserSavedFilterViewSet)
router.register(r'app-version', views.AppVersionViewSet)

router.register(r'marketing', views.MarketingViewSet)


router.register(r'seller-policy', views.SellerPolicyViewSet)
router.register(r'image-test', views.ImageTestViewSet)

router.register(r'stories', views.StoryViewSet)

router.register(r'viewfollowers', views.ViewFollowerViewSet)

#notification related urlShortener
router.register(r'notification', NotificationViewSet)
router.register(r'notification-entity', NotificationEntityViewSet)
router.register(r'notification-entity-type', NotificationEntityTypeViewSet)





urlpatterns = [
	url(r'^syncopeninginventorycsv/$',views.syncOpeningInventoryCSV),
	url(r'^importcsvskumap/$',views.importCSVSKUMap),
	url(r'^importcsvcompanymap/$',views.importCSVCompanyMap),
	url(r'^importcsvopeninginventory/$',views.importCSVOpeningInventory),
	url(r'^importcsvadjustmentinventory/$',views.importCSVAdjustmentInventory),
	url(r'^importcsvcatalog/$',views.importCSVCatalog),
	url(r'^importbulkcsvcatalog/$',views.importBulkCSVCatalog),
	url(r'^importcsvproduct/$',views.importCSVProduct),

	url(r'^importcsvorder/$',views.importCSVOrder),
	url(r'^importcsvinvoice/$',views.importCSVShipment),
	url(r'^importcsvshipmentdispatch/$',views.importCSVShipmentDispatch),

	url(r'^export-order/',views.order_for_ship),

	url(r'^importcsvorderinvoicestatusadmin/$',views.importCSVOrderInvoiceStatusAdmin),



	url(r'^catalogs/urlkey/(?P<pk>.+)/$', views.CatalogUrlindexView.as_view()),
	#import pdb; pdb.set_trace()
	url(r'^contacts/invites/$', views.ImportArrayInvitee.as_view()),
	url(r'^contacts/onwishbook/$', views.OnWishbook.as_view()),
	url(r'^sync/$', views.SyncData.as_view()),
	url(r'^tnc/$', views.Tnc.as_view()),
	url(r'^syncactivitylog/$', views.SyncActivityLog.as_view()),
	url(r'^auth/password-reset/$', views.PasswordReset.as_view()),
	url(r'^auth/generate-otp/$', views.GenerateOtp.as_view()),
	url(r'^generate-checksum/$', views.GenerateChecksum.as_view()),
	url(r'^generate-checksum-v2/$', views.GenerateChecksum_V2.as_view()),
	url(r'^verify-checksum/$', views.VerifyChecksum.as_view()),
	url(r'^paytm/response/$', views.PaytmResponse.as_view()),
	url(r'^checkpaytmstatus/$', views.CheckPaytmStatus.as_view()),
	url(r'^shipping-charges/$', views.ShippingCharge.as_view()),

	url(r'^zaakpay/initiate/$', views.ZaakpayInitiate.as_view()),
	url(r'^zaakpay/response/$', views.ZaakpayResponse),
	url(r'^zaakpay/success/$', views.ZaakpayStatus),
	url(r'^zaakpay/failure/$', views.ZaakpayStatus),

	url(r'^cashfree/checksum/$', views.CashFreeGenerateChecksum.as_view()),


	url(r'^user-campaign-click/$', views.SetUserCampaignClick),


	url(r'^multiorder/$', views.MultiOrder.as_view()),
	url(r'^notify/$', views.Notify.as_view()),

	url(r'^mobikwik/$', views.Mobikwik),

	url(r'^inventoryupdatefromserver/$', views.InventoryUpdateFromServer.as_view()),
	url(r'^updateorderstatus/$', views.UpdateOrderStatus.as_view()),

	url(r'^dailysharesms/$', views.DailyShareSMS.as_view()),
	url(r'^dailysharesmscron/$', views.DailyShareSMS.as_view()),
	url(r'^trustedsortorder/$', views.TrustedSortOrder.as_view()),
	url(r'^trustedsortordercron/$', views.TrustedSortOrder.as_view()),
	url(r'^disablecatalogcron/$', views.DisableCatalogCron.as_view()),
	url(r'^producteavcron/$', views.ProductEAVCron.as_view()),
	url(r'^catalogeavcron/$', views.CatalogEAVCron.as_view()),
	url(r'^brandtotalcatalogcron/$', views.BrandTotalCatalogCron.as_view()),
	url(r'^companysellstostatecron/$', views.CompanySellsToStateCron.as_view()),
	url(r'^geocodelocationcron/$', views.GEOCodeLocationCron.as_view()),
	url(r'^cron/inactive-user-notification/$', views.InActiveUserNotificationCron.as_view()),
	url(r'^cron/inactive-user-notification-before-30-days/$', views.InActiveUserNotificationBefore30DaysCron.as_view()),
	url(r'^cron/user-contact-registration/$', views.UserContactRegistrationCron.as_view()),
	url(r'^cron/mobile-state-mapping/$', views.MobileStateMappingCron.as_view()),
	url(r'^cron/seller-statistic/$', views.SellerStatisticCron.as_view()),
	url(r'^cron/user-campaign-click/$', views.UserCampaignClickCron.as_view()),
	url(r'^cron/meetingscsv/$', views.MeetingCSVeMailCron.as_view()),
	url(r'^cron/dailyordercsv/$', views.DailyOrderCSVeMailCron.as_view()),
	#for exporting order for shiprocket
	url(r'^cron/sugarupdate/$', views.SugarUpdateCron.as_view()),
	url(r'^cron/sugarcallupdate/$', views.SugarCallUpdateCron.as_view()),
	url(r'^cron/updateuninstallusers/$', views.UpdateUninstallUsersCron.as_view()),
	#WB-2198 - create new function in task.py file for cron
	url(r'^cron/dailyunsubcriberscsv/$', views.DailyUnsubscribedNumbersCSVreaderCron.as_view()),

	url(r'^send-sms/$', views.SendSMSDemo.as_view()),
	url(r'^send-notification/$', views.SendNotificationDemo.as_view()),

	url(r'^assigncatalogtocompany/$', views.AssignCatalogToCompany.as_view()),

	url(r'^enumgroup/$', views.GetEnumGroup.as_view()),

	#url(r'^sendsmserror/$', views.sendSmsError.as_view()),

	url(r'^applozicgroupcreate/$', views.ApplozicGroupCreate.as_view()),
	url(r'^deeplink/$', views.Deeplink.as_view()),

	#url(r'^user-campaign-click/$', views.SetUserCampaignClick.as_view()),



	url(r'^reset-to-guest-user/$', views.ResetToGuestUser.as_view()),
	url(r'^user-authentication/$', views.UserAuthentication.as_view()),



	url(r'^', include(router.urls)),

	url(r'^', include(companies.urls)),
	url(r'^', include(nestedcompanies.urls)),

	url(r'^', include(catalogs.urls)),
	url(r'^', include(nestedcatalogs.urls)),

	url(r'^', include(users.urls)),
	url(r'^', include(nestedusers.urls)),

	url(r'^', include(products.urls)),
	url(r'^', include(nestedproducts.urls)),

	url(r'^', include(brands.urls)),
	url(r'^', include(nestedbrands.urls)),

	#url(r'^silver/', include('silver.urls')),

]
