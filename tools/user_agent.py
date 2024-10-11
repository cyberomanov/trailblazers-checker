import random

from user_agents import parse


def generate_random_user_agent():
    browsers = [
        "Chrome/{}".format(random.randint(70, 126)),
        "Firefox/{}".format(random.randint(60, 90)),
        "Safari/{}".format(random.randint(10, 15)),
        "Edge/{}".format(random.randint(80, 90)),
    ]

    os_platforms = [
        "Windows NT 10.0; Win64; x64",
        "Macintosh; Intel Mac OS X 10_15_{}".format(random.randint(1, 7)),
        "X11; Linux x86_64",
    ]

    user_agent = "Mozilla/5.0 ({}) AppleWebKit/537.36 (KHTML, like Gecko) {} Safari/537.36".format(
        random.choice(os_platforms), random.choice(browsers))

    return user_agent


def generate_headers():
    sec_ch_ua_options = [
        '"Not/A)Brand";v="8", "Chromium";v="126"',
        '"Google Chrome";v="126"',
        '"Microsoft Edge";v="90"',
    ]

    user_agent = generate_random_user_agent()
    parsed_ua = parse(user_agent)
    platform = parsed_ua.os.family
    if platform == "Windows":
        platform = "Windows"
    elif platform == "Mac OS X":
        platform = "macOS"
    elif platform == "Linux":
        platform = "Linux"

    return {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en,en-US;q=0.9",
        "Connection": "keep-alive",
        "Sec-Ch-Ua": random.choice(sec_ch_ua_options),
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"{}"'.format(platform),
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": user_agent
    }
