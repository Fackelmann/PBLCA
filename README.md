# Pinboard Link Checker and Archiver (PBLCA)
Lately I have become increasingly worried about the problem of [link rot](https://www.gwern.net/Archiving-URLs). I've been using Pinboard for more than 5 years, and I have over 1200 bookmarks, so out of curisoity I decided to check how many of these links were dead. The result was that more than 5% of the links didn't exist any more, or redirected to a 403 page. This is worrying. Since I have been continously adding bookmarks over this time, this means that the link rot rate is (significantly) larger than 5% per 5 years.

I've also added the option to look for the closest snapshot (to the bookmark creation date) of the dead link in the [internet archive](archive.org) and update the bookmark to redirect to it. If no snapshot exists, the script will ask you whether you want to delete the bookmark or keep it.

PBLCA uses multiprocessing to query all your bookmarks, so it should be relatively fast. Checking 1250 of my bookmarks takes around 6 minutes.

## Usage

Clone the repo and `cd` to the folder:

```
git clone https://github.com/Fackelmann/PBLCA
cd PBLCA
```

Create the `poetry` virtual environment:

```
poetry update
```

And run it, providing your [Pinboard API token](https://pinboard.in/settings/password)

```
cd pblca
poetry run pblca --token USERNAME:API_TOKEN
```

If you don't have poetry installed, you'll need to install it first:

```
pip3 install poetry
```

## TODO
- [ ] Add options for batch processing

## Known issues
- There is no real way to update a bookmark via the Pinboard API, as the URL is the key. PBLCA will create a new bookmark with the same attributes (including creation date), and delete the old one.
- A (very) few bookmarks will show up as dead even though you can still access the page with your browser. It seems to be an issue with the headers.

## Disclaimer
- Please use at your own risk. ALWAYS have a [backup](https://pinboard.in/settings/backup) of your data.
