import re


def split_list(q: list, size: int):
    result = []
    for i in range(0, len(q), size):
        result.append(q[i:i + size])
    return result


def extract_user_ids(profiles):
    user_ids = []
    for profile in profiles:
        uri = profile["uri"]
        user_id = uri.split(":")[-1]
        user_ids.append(user_id)
    return user_ids


def extract_access_token(html_source):
    # Regular expression pattern to extract accessToken
    pattern = r'"accessToken":"(.*?)"'

    # Extracting accessToken using regex
    match = re.search(pattern, html_source)

    # Check if match is found
    if match:
        access_token = match.group(1)
        return access_token
    else:
        return None


def merge_lists_without_duplicates(list1, list2):
    merged_list = list1 + list2
    merged_set = set(merged_list)
    merged_list_without_duplicates = list(merged_set)
    return merged_list_without_duplicates
