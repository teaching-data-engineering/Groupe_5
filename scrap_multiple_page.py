import requests


def scrap_one_page(page_idx):
    event_list = []
    return event_list


def scrap_multiple_pages(start_date, end_date, max_page):
    l_pages = list()
    response1 = scrap_one_page(start_date, end_date, 1)
    for i in range(max_page):
        response2 = scrap_one_page(start_date, end_date, i + 1)
        if (
            response1.json()["events"] == response2.json()["events"]
            and len(response1.json()["events"]) > 0
        ):
            break
            # date = response2[-1]["StartsAt"]
            # start_date = date
        save_json(response1, i, response1[-1]["StartsAt"])
        l_pages.extend(response1)
        response1 = response2
    return l_pages
