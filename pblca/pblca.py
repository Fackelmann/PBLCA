"""PinBoard Link Checker and Archiver (PBLCA)
Checks for dead links in your Pinboard bookmarks and provides the option to
update them with an archive.org link or delete them.
"""
import argparse
from datetime import datetime
import json
from multiprocessing import Pool

import requests
from tqdm import tqdm # type: ignore
from typing import List, Optional
from pblca.pinboard_api import PinboardAPI

# We need an user agent so some HTTP servers are nice to us and let us in
HEADERS = {"User-Agent":
           "Mozilla/5.0 (X11; Linux x86_64; rv:79.0) "
           "Gecko/20100101 Firefox/79.0"}


def create_main_parser() -> argparse.ArgumentParser:
    """ Parser for CLI arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-t",
                        "--token",
                        type=str,
                        required=True)
    return parser


def check_link(post: dict) -> Optional[dict]:
    """Checks if whether link is dead or not."""
    try:
        request = requests.get(post["href"], timeout=10, headers=HEADERS)
        if request.status_code != 200:
            return post
    except Exception as e:
        print(f"Exception {e} at post {post}")
        return post
    return None


def create_add_parameters_from_bookmark(bookmark: dict) -> dict:
    params = {}
    params["url"] = bookmark["href"]
    params["description"] = bookmark["description"]
    params["extended"] = bookmark["extended"]
    params["dt"] = bookmark["time"]
    params["shared"] = bookmark["shared"]
    params["toread"] = bookmark["toread"]
    params["tags"] = bookmark["tags"]
    return params


def update_archive_link(bookmark: dict,
                        ia_url: str,
                        pb_session: PinboardAPI) -> None:
    """Updates the link of a current bookmark to direct to the closest snapshot
    available in archive.org."""
    old_bookmark_url = bookmark["href"]
    params = create_add_parameters_from_bookmark(bookmark)
    params["url"] = ia_url
    pb_session.add_post(**params)
    params = {"url": old_bookmark_url}
    pb_session.delete_post(**params)
    print("Bookmark updated")


def remove_bookmark(bookmark: dict, pb_session: PinboardAPI) -> None:
    """Delete bookmark."""
    params = {"url": bookmark["href"]}
    pb_session.delete_post(**params)
    print("Bookmark deleted")


def convert_bookmark_time_to_iso(bookmark_time: str) -> str:
    bookmark_dt = datetime.strptime(bookmark_time, "%Y-%m-%dT%H:%M:%SZ")
    return bookmark_dt.strftime("%Y%m%d")


def process_roten_links(roten_links: list, pb_session: PinboardAPI) -> None:
    """Process the roten links for deletion, or for updating the link with an
    archive.org snapshot."""
    for bookmark in roten_links:
        timestamp = convert_bookmark_time_to_iso(bookmark["time"])
        url = bookmark["href"]
        description = bookmark["description"]
        url_request = "https://archive.org/wayback/available?"\
            f"url={url}&timestamp={timestamp}"
        request = requests.get(url_request, headers=HEADERS)
        request_dict = json.loads(request.content)["archived_snapshots"]
        if "closest" in request_dict:
            ia_url = request_dict["closest"]["url"]
            answer = input(f"Internet archive link available for {description}"
                           f"({url}). Do you want to update "
                           "your bookmark? (y/N)")
            if answer == "y":
                update_archive_link(bookmark, ia_url, pb_session)
        else:
            answer = input(f"Internet archive not available for {description}"
                           f"({url}). Do you want to delete "
                           "your bookmark? (y/N)")
            if answer == "y":
                remove_bookmark(bookmark, pb_session)


def main() -> None:
    """Main function. Parse arguments, call a pool of
    processes, yada, yada, yada."""
    parser = create_main_parser()
    args = parser.parse_args()

    pb_session = PinboardAPI(args.token)
    print("Fetching bookmarks...")
    all_posts = pb_session.get_all_posts()
    print("Analyzing bookmarks...")
    with Pool(4) as pool:
        analysis_result = list(tqdm(pool.imap(check_link, all_posts),
                                    total=len(all_posts)))
    roten_links: List[dict] = list(filter(None, analysis_result))
    print(f"link rot: {len(roten_links)/len(all_posts)*100}."
          f"{len(roten_links)}/{len(all_posts)}")
    process_roten_links(roten_links, pb_session)
