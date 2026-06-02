
from typing import Dict, List, Tuple, Any
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_SYSTEM_PROMPT_PATH = os.path.join(_ROOT, "system_prompt.txt")

def _load_system_prompt() -> str:
    if os.path.exists(_SYSTEM_PROMPT_PATH):
        try:
            with open(_SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
    return ""

SYSTEM_PROMPT: str = _load_system_prompt() or (
    "Luôn trả lời bằng tiếng Việt. Không bịa thông tin. Nếu yêu cầu không an toàn thì từ chối ngay và không gọi công cụ. Nếu thiếu thông tin khách hàng thì hỏi đúng phần còn thiếu trước khi gọi công cụ."
)

# Trường tối thiểu bắt buộc trước khi gọi công cụ
REQUIRED_FIELDS = [
    "customer_name",
    "phone",
    "email",
    "shipping_address",
    "items",  # list of {sku, quantity}
]

FORBIDDEN_ACTION_KEYWORDS = [
    "bẻ khóa",
    "hack",
    "trộm",
    "tấn công",
    "số thẻ",
    "số tài khoản",
]


def missing_fields(order: Dict[str, Any]) -> List[str]:
    missing = []
    for fld in REQUIRED_FIELDS:
        if fld not in order or order[fld] in (None, "", [], {}):
            missing.append(fld)
    # items needs additional structure
    if "items" in order and isinstance(order.get("items"), list):
        bad = False
        if len(order["items"]) == 0:
            bad = True
        else:
            for it in order["items"]:
                if not isinstance(it, dict) or not it.get("sku") or not it.get("quantity"):
                    bad = True
                    break
        if bad and "items" not in missing:
            missing.append("items")
    return missing


def can_call_tools(order: Dict[str, Any]) -> Tuple[bool, str]:
    m = missing_fields(order)
    if m:
        labels = {
            "customer_name": "tên khách hàng",
            "phone": "số điện thoại",
            "email": "email",
            "shipping_address": "địa chỉ giao hàng",
            "items": "ít nhất một sản phẩm và số lượng tương ứng",
        }
        requested = ", ".join(labels.get(field, field) for field in m)
        return False, "Thiếu thông tin — không thể gọi công cụ. Vui lòng bổ sung: " + requested
    return True, ""


def is_unsafe_request(text: str) -> Tuple[bool, str]:

    if not text:
        return False, ""
    low = text.lower()
    for kw in FORBIDDEN_ACTION_KEYWORDS:
        if kw in low:
            return True, f"Yêu cầu không an toàn: phát hiện từ khóa '{kw}'."
    return False, ""


def enforce_call_order(expected: List[str], actual: List[str]) -> Tuple[bool, str]:
 
    if expected == actual:
        return True, ""
    # kiểm tra xem actual có phải là prefix theo đúng thứ tự
    if len(actual) > len(expected):
        return False, "Thứ tự gọi công cụ không hợp lệ: gọi quá nhiều bước so với yêu cầu."
    for i, a in enumerate(actual):
        if expected[i] != a:
            return False, (
                "Thứ tự gọi công cụ không hợp lệ. Yêu cầu thứ tự: " + ", ".join(expected)
            )
    return True, ""


def can_save_order(order: Dict[str, Any], checks: Dict[str, bool]) -> Tuple[bool, str]:
    required_checks = ["inventory_ok", "price_ok", "payment_ok", "customer_confirmed"]
    missing = [c for c in required_checks if c not in checks]
    if missing:
        return False, "Kiểm tra nội bộ chưa đủ: thiếu " + ", ".join(missing)
    for k in required_checks:
        if not checks.get(k):
            return False, f"Không thể lưu đơn: kiểm tra '{k}' không đạt."
    # kiểm tra trường tối thiểu thêm lần cuối
    if missing_fields(order):
        return False, "Không thể lưu đơn: thông tin đặt hàng còn thiếu hoặc không hợp lệ."
    return True, ""


__all__ = [
    "SYSTEM_PROMPT",
    "REQUIRED_FIELDS",
    "missing_fields",
    "can_call_tools",
    "is_unsafe_request",
    "enforce_call_order",
    "can_save_order",
]
