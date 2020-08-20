import argparse
import json
import pinboard
import requests
from multiprocessing import Pool

from tqdm import tqdm
from copy import deepcopy

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}

def create_main_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
                        "--token",
                        type=str)

    return parser

def check_link(post):
    
    try:
        request = requests.get(post.url, timeout=10, headers=HEADERS)
        if request.status_code != 200:
#            tqdm.write(f"\n{post.url} Dead. STATUS CODE")
            return(post)
    except Exception as e:
#        tqdm.write(f"\n{post.url} Dead. EXCEPTION {e}")
        return post
    return None

def update_link_ia(bookmark, ia_url):
    old_bookmark = deepcopy(bookmark)
    bookmark.url = ia_url
    time = bookmark.time
    bookmark.time = time
    bookmark.save(update_time = True)
    old_bookmark.delete()
    print("Bookmark updated")

def remove_bookmark(bookmark):
    bookmark.delete()
    print("Bookmark deleted")

def process_roten_links(roten_links):
    for bookmark in roten_links:
        timestamp = bookmark.time.strftime("%Y%m%d")
        url = bookmark.url
        description = bookmark.description
        url_request=f"https://archive.org/wayback/available?url={url}&timestamp={timestamp}"
        request = requests.get(url_request, headers=HEADERS)
        request_dict = json.loads(request.content)["archived_snapshots"]
        if "closest" in request_dict:
            ia_url = request_dict["closest"]["url"]
            answer = input(f"Internet archive link available for {description}({url}). Do you want to update your bookmark? (y/n)")
            if answer == "y":
                update_link_ia(bookmark, ia_url)
        else:
            answer = input(f"Internet archive not available for {description}({url}). Do you want to delete your bookmark? (y/n)")
            if answer == "y":
                remove_bookmark(bookmark)

def main():
    parser = create_main_parser()
    args = parser.parse_args()

    pb = pinboard.Pinboard(args.token)
    print("Fetching bookmarks...")
    all_posts = pb.posts.all()
    rot_counter = 0
    print("Analyzing bookmarks...")
    with Pool(4) as p:
        r = list(tqdm(p.imap(check_link, all_posts), total=len(all_posts)))
    roten_links=list(filter(None, r))
    print(f"link rot: {len(roten_links)/len(all_posts)*100}. {len(roten_links)}/{len(all_posts)}")
    process_roten_links(roten_links)

