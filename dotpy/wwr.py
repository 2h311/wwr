import re
import pprint
from typing import Optional

import requests
from lxml import etree


weworkremotely_feed_links = {
    "All Other Remote Jobs": "https://weworkremotely.com/categories/all-other-remote-jobs.rss",
    "DevOps and Sysadmin Jobs": "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
    "Full-Stack Programming Jobs": "https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss",
    "Front-End Programming Jobs": "https://weworkremotely.com/categories/remote-front-end-programming-jobs.rss",
    "Back-End Programming Jobs": "https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss",
}


def gettext(xml_element: etree.Element) -> str:
    return xml_element[-1].text


def get_text_from_channel_item(channel_item: etree.Element) -> dict:
    job_dict = dict()
    job_region = gettext(channel_item.xpath("./region"))
    if re.search(r"anywhere|africa", job_region, re.IGNORECASE):
        job_dict["Region"] = job_region
        job_dict["Title"] = gettext(channel_item.xpath("./title"))
        job_dict["Category"] = gettext(channel_item.xpath("./category"))
        job_dict["Type"] = gettext(channel_item.xpath("./type"))
        job_dict["Description"] = gettext(channel_item.xpath("./description"))
        job_dict["Publication Date"] = gettext(channel_item.xpath("./pubDate"))
        job_dict["Link"] = gettext(channel_item.xpath("./link"))
        job_dict["Expiry Date"] = gettext(channel_item.xpath("./expires_at"))
    return job_dict


def get_request(rss_feed_link: str) -> Optional[requests.Response]:
    content = ""
    response = requests.get(rss_feed_link)
    if response.ok:
        content = etree.fromstring(response.content)
    return content


def get_total_job_count(job_dict: dict) -> dict:
    return sum([len(job_dict.get(key)) for key in job_dict])


def get_all_jobs() -> dict:
    job_dict = dict()
    for key, url in weworkremotely_feed_links.items():
        root = get_request(url)
        channel_items = root.xpath("//channel //item")

        jobs = list()
        for channel_item in channel_items:
            response = get_text_from_channel_item(channel_item)
            if response:
                jobs.append(response)
        job_dict[key] = jobs

    return {
        "Jobs": job_dict,
        "Total Job Count": get_total_job_count(job_dict),
        "Platform": "We Work Remotely",
    }


if __name__ == "__main__":
    import json
    import datetime

    jobs = get_all_jobs()
    json.dump(
        jobs, open(f"jobs-{ str(datetime.datetime.now()).replace(' ', '-') }.json", "w")
    )
    pprint.pprint(jobs)
