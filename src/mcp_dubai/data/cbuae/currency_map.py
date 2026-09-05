"""
Arabic and English currency names to ISO codes and canonical labels.

The CBUAE Umbraco exchange-rate endpoint can return Arabic or English
names, with no code column. Translating them back to ISO codes keeps the
tool response bilingual so clients can match on the ISO code without
having to recognise Arabic strings. Unknown names still pass through as
`currency_ar` so a new entry never silently drops a row.

Verified against all 77 English rows in the live response on 2026-09-05.
The earlier Arabic mappings are retained. Add new entries when
CBUAE lists additional currencies.
"""

from __future__ import annotations

from typing import Final

# Arabic name (exact, as returned by the endpoint) -> (ISO 4217, English label)
ARABIC_TO_ISO: Final[dict[str, tuple[str, str]]] = {
    "دولار امريكي": ("USD", "US Dollar"),
    "بيسو ارجنتيني": ("ARS", "Argentine Peso"),
    "دولار استرالي": ("AUD", "Australian Dollar"),
    "تاكا بنغلاديشية": ("BDT", "Bangladeshi Taka"),
    "دينار بحريني": ("BHD", "Bahraini Dinar"),
    "دولار بروناي": ("BND", "Brunei Dollar"),
    "ريال برازيلي": ("BRL", "Brazilian Real"),
    "بولا بوتسواني": ("BWP", "Botswana Pula"),
    "روبل بلاروسي": ("BYN", "Belarusian Ruble"),
    "دولار كندي": ("CAD", "Canadian Dollar"),
    "فرنك سويسري": ("CHF", "Swiss Franc"),
    "بيزو تشيلي": ("CLP", "Chilean Peso"),
    "يوان صيني - الخارج": ("CNH", "Chinese Yuan (Offshore)"),
    "يوان صيني": ("CNY", "Chinese Yuan"),
    "بيزو كولومبي": ("COP", "Colombian Peso"),
    "كرونة تشيكية": ("CZK", "Czech Koruna"),
    "كرون دانماركي": ("DKK", "Danish Krone"),
    "دينار جزائري": ("DZD", "Algerian Dinar"),
    "جينيه مصري": ("EGP", "Egyptian Pound"),
    "يورو": ("EUR", "Euro"),
    "جنيه استرليني": ("GBP", "British Pound"),
    "دولار هونج كونج": ("HKD", "Hong Kong Dollar"),
    "فورنت هنغاري": ("HUF", "Hungarian Forint"),
    "روبية اندونيسية": ("IDR", "Indonesian Rupiah"),
    "روبية هندية": ("INR", "Indian Rupee"),
    "روبية نيبالية": ("NPR", "Nepalese Rupee"),
    "كرونة آيسلندية": ("ISK", "Icelandic Krona"),
    "دينار أردني": ("JOD", "Jordanian Dinar"),
    "ين ياباني": ("JPY", "Japanese Yen"),
    "شلن كيني": ("KES", "Kenyan Shilling"),
    "ون كوري": ("KRW", "South Korean Won"),
    "دينار كويتي": ("KWD", "Kuwaiti Dinar"),
    "تينغ كازاخستاني": ("KZT", "Kazakhstani Tenge"),
    "ليرة لبنانية": ("LBP", "Lebanese Pound"),
    "روبية سريلانكي": ("LKR", "Sri Lankan Rupee"),
    "درهم مغربي": ("MAD", "Moroccan Dirham"),
    "دينار مقدوني": ("MKD", "Macedonian Denar"),
    "بيسو مكسيكي": ("MXN", "Mexican Peso"),
    "رينغيت ماليزي": ("MYR", "Malaysian Ringgit"),
    "نيرا نيجيري": ("NGN", "Nigerian Naira"),
    "كرون نرويجي": ("NOK", "Norwegian Krone"),
    "دولار نيوزيلندي": ("NZD", "New Zealand Dollar"),
    "ريال عماني": ("OMR", "Omani Rial"),
    "سول بيروفي": ("PEN", "Peruvian Sol"),
    "بيسو فلبيني": ("PHP", "Philippine Peso"),
    "روبية باكستانية": ("PKR", "Pakistani Rupee"),
    "زلوتي بولندي": ("PLN", "Polish Zloty"),
    "ريال قطري": ("QAR", "Qatari Riyal"),
    "دينار صربي": ("RSD", "Serbian Dinar"),
    "روبل روسي": ("RUB", "Russian Ruble"),
    "ريال سعودي": ("SAR", "Saudi Riyal"),
    "دينار سوداني": ("SDG", "Sudanese Pound"),
    "كرونة سويدية": ("SEK", "Swedish Krona"),
    "دولار سنغافوري": ("SGD", "Singapore Dollar"),
    "بات تايلندي": ("THB", "Thai Baht"),
    "دينار تونسي": ("TND", "Tunisian Dinar"),
    "ليرة تركية": ("TRY", "Turkish Lira"),
    "دولار تريندادي": ("TTD", "Trinidad and Tobago Dollar"),
    "دولار تايواني": ("TWD", "Taiwan Dollar"),
    "شلن تنزاني": ("TZS", "Tanzanian Shilling"),
    "شلن اوغندي": ("UGX", "Ugandan Shilling"),
    "دونغ فيتنامي": ("VND", "Vietnamese Dong"),
    "ريال يمني": ("YER", "Yemeni Rial"),
    "راند جنوب أفريقي": ("ZAR", "South African Rand"),
    "كواشا زامبي": ("ZMW", "Zambian Kwacha"),
    "مانات أذربيجاني": ("AZN", "Azerbaijani Manat"),
    "ليف بلغاري": ("BGN", "Bulgarian Lev"),
    "بر إثيوبي": ("ETB", "Ethiopian Birr"),
    "دينار عراقي": ("IQD", "Iraqi Dinar"),
    "شيكل اسرائيلي": ("ILS", "Israeli Shekel"),
    "دينار ليبي": ("LYD", "Libyan Dinar"),
    "روبي موريشي": ("MUR", "Mauritian Rupee"),
    "ليو روماني": ("RON", "Romanian Leu"),
    "ليرة سورية": ("SYP", "Syrian Pound"),
    "منات تركمانستاني": ("TMT", "Turkmenistani Manat"),
    "سوم أوزبكستاني": ("UZS", "Uzbekistani Som"),
    "ريال ايراني": ("IRR", "Iranian Rial"),
}


_CANONICAL_BY_ISO: Final[dict[str, str]] = dict(ARABIC_TO_ISO.values())
ARABIC_BY_ISO: Final[dict[str, str]] = {
    iso: arabic_name for arabic_name, (iso, _) in ARABIC_TO_ISO.items()
}
_ENGLISH_TO_ISO: Final[dict[str, str]] = {
    name.casefold(): iso for iso, name in ARABIC_TO_ISO.values()
}
# Exact spelling variants in the official English feed, including upstream
# abbreviations and the "Bahrani" spelling. Avoid fuzzy currency matching.
_ENGLISH_TO_ISO.update(
    {
        "bangladesh taka": "BDT",
        "bahrani dinar": "BHD",
        "belarus rouble": "BYN",
        "chinese yuan - offshore": "CNH",
        "egypt pound": "EGP",
        "gb pound": "GBP",
        "hongkong dollar": "HKD",
        "indonesia rupiah": "IDR",
        "iceland krona": "ISK",
        "jordan dinar": "JOD",
        "kenya shilling": "KES",
        "korean won": "KRW",
        "kazakhstan tenge": "KZT",
        "lebanon pound": "LBP",
        "sri lanka rupee": "LKR",
        "macedonia denar": "MKD",
        "malaysia ringgit": "MYR",
        "newzealand dollar": "NZD",
        "peru sol": "PEN",
        "philippine piso": "PHP",
        "pakistan rupee": "PKR",
        "russia rouble": "RUB",
        "trin tob dollar": "TTD",
        "tanzania shilling": "TZS",
        "uganda shilling": "UGX",
        "vietnam dong": "VND",
        "yemen rial": "YER",
        "south africa rand": "ZAR",
        "azerbaijan manat": "AZN",
        "israeli new shekel": "ILS",
        "turkmen manat": "TMT",
    }
)


def lookup(currency_name: str) -> tuple[str | None, str | None]:
    """Return (iso_code, english_name) for an Arabic or English feed label."""
    normalized = " ".join(currency_name.split())
    entry = ARABIC_TO_ISO.get(normalized)
    if entry is not None:
        return entry
    iso = _ENGLISH_TO_ISO.get(normalized.casefold())
    if iso is not None:
        return iso, _CANONICAL_BY_ISO[iso]
    return (None, None)
