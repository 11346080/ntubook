from django.utils import timezone


def update_status_with_timestamp(obj, new_status):
    """
    對 Listing 或 PurchaseRequest 執行狀態更新，
    同時寫入對應的時間戳記欄位。

    語意對照（保守實作）：

    Listing：
      - RESERVED  →  reserved_at
      - SOLD      →  sold_at
      - DELETED   →  deleted_at
      - OFF_SHELF / REMOVED → 不動 deleted_at

    PurchaseRequest：
      - ACCEPTED  →  responded_at + contact_released_at
      - REJECTED  →  responded_at
      - CANCELLED_* →  cancelled_at
    """
    from listings.models import Listing
    from purchase_requests.models import PurchaseRequest

    changed = ['status', 'updated_at']

    if isinstance(obj, Listing):
        obj.status = new_status

        if new_status == Listing.Status.RESERVED:
            obj.reserved_at = timezone.now()
            changed.append('reserved_at')
        elif new_status == Listing.Status.SOLD:
            obj.sold_at = timezone.now()
            changed.append('sold_at')
        elif new_status == Listing.Status.DELETED:
            obj.deleted_at = timezone.now()
            changed.append('deleted_at')

        obj.save(update_fields=changed)

    elif isinstance(obj, PurchaseRequest):
        obj.status = new_status

        if new_status == PurchaseRequest.Status.ACCEPTED:
            obj.responded_at = timezone.now()
            obj.contact_released_at = timezone.now()
            changed.extend(['responded_at', 'contact_released_at'])
        elif new_status == PurchaseRequest.Status.REJECTED:
            obj.responded_at = timezone.now()
            changed.append('responded_at')
        elif new_status in (
            PurchaseRequest.Status.CANCELLED_BY_BUYER,
            PurchaseRequest.Status.CANCELLED_BY_SELLER,
        ):
            obj.cancelled_at = timezone.now()
            changed.append('cancelled_at')

        obj.save(update_fields=changed)
