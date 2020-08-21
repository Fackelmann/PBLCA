"""PinBoard Link Checker and Archiver (PBLCA)
Checks for dead links in your Pinboard bookmarks and provides the option to
update them with an archive.org link or delete them.
"""
import argparse
import json
from copy import deepcopy
from multiprocessing import Pool

import requests
import pinboard
from tqdm import tqdm


# We need an user agent so some HTTP servers are nice to us and let us in
HEADERS = {"User-Agent":
           "Mozilla/5.0 (X11; Linux x86_64; rv:79.0) "
           "Gecko/20100101 Firefox/79.0"}


def create_main_parser():
    """ Parser for CLI arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-t",
                        "--token",
                        type=str,
                        required=True)
    return parser


def check_link(post):
    """Checks if whether link is dead or not."""
    try:
        request = requests.get(post.url, timeout=10, headers=HEADERS)
        if request.status_code != 200:
            return post
    except:
        return post
    return None


def update_archive_link(bookmark, ia_url):
    """Updates the link of a current bookmark to direct to the closest snapshot
    available in archive.org."""
    #The save is ok as long as we update any field, except the URL. Since the
    #URL acts as a key, modifying it will create a new bookmark.
    #We went around this by saving the previous bookmark, and then deleting it.
    old_bookmark = deepcopy(bookmark)
    bookmark.url = ia_url
    time = bookmark.time
    bookmark.time = time
    bookmark.save(update_time=True)
    old_bookmark.delete()
    print("Bookmark updated")


def remove_bookmark(bookmark):
    """Delete bookmark."""
    bookmark.delete()
    print("Bookmark deleted")


def process_roten_links(roten_links):
    """Process the roten links for deletion, or for updating the link with an
    archive.org snapshot."""
    for bookmark in roten_links:
        timestamp = bookmark.time.strftime("%Y%m%d")
        url = bookmark.url
        description = bookmark.description
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
                update_archive_link(bookmark, ia_url)
        else:
            answer = input(f"Internet archive not available for {description}"
                           f"({url}). Do you want to delete "
                           "your bookmark? (y/N)")
            if answer == "y":
                remove_bookmark(bookmark)


def main():
    """Main function. Parse arguments, call a pool of
    processes, yada, yada, yada."""
    parser = create_main_parser()
    args = parser.parse_args()

    pb_session = pinboard.Pinboard(args.token)
    print("Fetching bookmarks...")
    all_posts = pb_session.posts.all()
    print("Analyzing bookmarks...")
    with Pool(4) as pool:
        analysis_result = list(tqdm(pool.imap(check_link, all_posts),
                                    total=len(all_posts)))
    roten_links = list(filter(None, analysis_result))
    print(f"link rot: {len(roten_links)/len(all_posts)*100}."
          f"{len(roten_links)}/{len(all_posts)}")
    process_roten_links(roten_links)
