import httpx
from settings import get_settings

def send_otp(mobile: str) -> dict:
    settings = get_settings()

    if not mobile:
        return {
            "ResponseCode": "401",
            "Result": "false",
            "ResponseMsg": "Mobile number is required!"
        }

    url = (
        f"{settings.AFRO_MESSAGE_BASE_URL}/challenge?"
        f"from={settings.AFRO_MESSAGE_IDENTIFIER_ID}"
        f"&sender={settings.AFRO_MESSAGE_SENDER_NAME}"
        f"&to={mobile}"
        f"&ps="
        f"&sb={settings.AFRO_MESSAGE_SB}"
        f"&sa={settings.AFRO_MESSAGE_SA}"
        f"&ttl={settings.AFRO_MESSAGE_TTL}"
        f"&len={settings.AFRO_MESSAGE_LEN}"
        f"&t={settings.AFRO_MESSAGE_T}"
        f"&callback={settings.AFRO_MESSAGE_CALLBACK}"
    )

    headers = {
        "Authorization": f"Bearer {settings.AFRO_MESSAGE_API_KEY}"
    }

    try:
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data.get("acknowledge") == "success":
            return {
                "ResponseCode": "200",
                "Result": "true",
                "ResponseMsg": "Check your message!"
            }
        else:
            return {
                "ResponseCode": "200",
                "Result": "false",
                "ResponseMsg": "Please try again!"
            }

    except httpx.HTTPError as e:
        return {
            "ResponseCode": "500",
            "Result": "false",
            "ResponseMsg": f"HTTP error occurred: {str(e)}"
        }
