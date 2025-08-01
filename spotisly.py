import argparse
import logging
import random
import re
import string
import spotipy
import sys
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyOauthError
from opsec import OpSecSimulator

CLIENT_ID = "xxxxxxxxxxxx"
CLIENT_SECRET = "xxxxxxxxxxxx"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private user-library-modify user-library-read user-read-private"

RACCOON_ART = r"""
                                                                                               
                                           ▓▓▓▓▓▓▓▓                                            
                                    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                                     
                                ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                                 
                              ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                              
                           ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                            
                          ▓        ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓       ▓▓▓▓▓▓▓▓▓▓▓                          
                        ▓▓     ▓▓▓    ▓▓▓▓▓▓▓▓▓▓     ▓▓▓  ▓▓▓▓▓▓▓▓▓▓▓▓                         
                       ▓▓▓  ▓    ▓▓▓               ▓▓▓▓▓  ▓▓▓▓▓▓▓▓▓▓▓▓▓                        
                      ▓▓▓▓        ▓▓▓                ▓▓▓  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓                       
                     ▓▓▓▓▓▓        ▓                     ▓▓     ▓▓▓▓▓▓▓▓▓                      
                     ▓▓▓▓▓▓▓                            ▓▓▓▓        ▓▓▓▓▓▓                     
                    ▓▓▓▓▓▓             ▓     ▓     ▓     ▓▓▓▓▓▓▓      ▓▓▓▓                     
                    ▓▓▓▓▓        ▓▓▓▓▓▓▓▓▓▓▓▓▓▓    ▓▓▓▓▓  ▓▓▓▓▓▓▓▓▓   ▓▓▓▓▓                    
                   ▓▓▓▓▓   ▓▓▓▓▓▓▓▓▓▓▓▓      ▓▓    ▓▓   ▓  ▓ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓                    
                   ▓▓▓▓  ▓▓▓▓▓▓▓▓▓▓      ▓     ▓   ▓ ▓     ▓     ▓▓▓▓▓▓▓▓▓▓                    
                   ▓▓▓▓ ▓▓▓▓▓▓▓▓                          ▓▓▓       ▓▓▓▓▓▓▓                    
                    ▓▓▓▓▓▓▓                   ▓▓▓    ▓    ▓▓▓▓▓▓▓   ▓▓▓▓▓▓▓                    
                    ▓▓▓▓▓▓▓▓▓               ▓▓▓▓▓▓▓   ▓▓ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                     
                     ▓▓▓▓▓▓               ▓▓▓▓▓▓▓▓▓      ▓     ▓▓▓▓▓▓▓▓▓▓▓                     
                     ▓▓▓▓▓▓▓▓          ▓▓▓▓▓▓▓▓▓▓▓       ▓▓▓     ▓▓▓▓▓▓▓▓                      
                      ▓▓▓▓▓▓▓▓▓▓         ▓▓▓▓ ▓▓▓▓▓▓▓   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                       
                       ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓       ▓▓▓      ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                        
                        ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓         ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                         
                          ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                           
                            ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                            
                              ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                               
                                 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                                 
                                    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                                     
                                            ▓▓▓▓▓▓▓                                            
                                                                                               
"""

def print_banner():
    print(RACCOON_ART)
    print("Spotisly: Encode/Decode a Message Using Spotify")
    print("--quiet or -q to hide banner\n")

class BannerHelpParser(argparse.ArgumentParser):
    def print_help(self, file=None):
        print_banner()
        super().print_help(file)


# List of genres that can be used for fall back searching
GENRE_SIMILARITY = {
    "metal": ["hard rock", "rock", "alternative metal", "industrial"],
    "rock": ["classic rock", "alternative", "indie", "punk", "metal"],
    "pop": ["dance pop", "electropop", "indie pop"],
    "hip hop": ["rap", "trap", "r&b"],
    "jazz": ["blues", "funk", "soul"],
    "electronic": ["house", "techno", "dance", "edm"],
    "classical": ["baroque", "orchestral", "romantic"],
    "indie": ["indie rock", "alternative", "bedroom pop"],
    "blues": ["jazz", "soul", "classic rock"],
    "funk": ["disco", "soul", "r&b"],
    "r&b": ["neo soul", "hip hop", "pop"],
    "country": ["folk", "americana", "bluegrass"],
    "folk": ["acoustic", "indie folk", "singer-songwriter"],
    "reggae": ["dub", "ska", "dancehall"],
    "techno": ["minimal techno", "house", "trance"],
    "house": ["deep house", "tech house", "edm"],
    "trap": ["drill", "rap", "hip hop"],
    "alternative": ["indie", "post-punk", "grunge"],
    "punk": ["hardcore", "garage rock", "post-punk"],
    "ambient": ["downtempo", "chillout", "drone"],
    "edm": ["big room", "progressive house", "electro house"],
    "latin": ["reggaeton", "salsa", "bachata"],
    "soul": ["motown", "r&b", "funk"],
    "grunge": ["alternative rock", "post-grunge", "punk"],
    "disco": ["funk", "soul", "dance"],
    "drum and bass": ["breakbeat", "jungle", "dubstep"],
    "dubstep": ["trap", "drum and bass", "brostep"],
    "k-pop": ["pop", "dance pop", "r&b"],
    "lofi": ["chillhop", "jazzhop", "instrumental"],
    "new wave": ["synthpop", "post-punk", "alternative"],
    "synthpop": ["new wave", "electropop", "indie pop"],
    "trance": ["progressive trance", "uplifting trance", "techno"],
    "opera": ["classical", "romantic", "baroque"],
    "industrial": ["metal", "ebm", "noise"],
    "emo": ["pop punk", "post-hardcore", "alternative"],
    "ska": ["punk", "reggae", "rocksteady"],
    "chillout": ["ambient", "downtempo", "lofi"],
    "hardstyle": ["trance", "techno", "edm"],
    "garage": ["uk garage", "2-step", "house"],
    "psychedelic": ["psych rock", "space rock", "progressive rock"],
    "bluegrass": ["country", "folk", "americana"],
    "singer-songwriter": ["folk", "acoustic", "indie"],
    "neo soul": ["r&b", "soul", "jazz"],
    "breakbeat": ["drum and bass", "electro", "jungle"],
}

RESET = "\033[0m"
COLORS = {
    "DEBUG": "\033[36m",     # Cyan
    "INFO": "\033[32m",      # Green
    "WARNING": "\033[33m",   # Yellow
    "ERROR": "\033[31m",     # Red
    "CRITICAL": "\033[41m",  # Red background
    "OPSEC": "\033[96m",     # Magenta
}

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        is_opsec = getattr(record, "opsec", False)
        label = "OPSEC" if is_opsec else record.levelname
        color = COLORS.get(label, "")
        return f"{color}[{label}]{RESET} {super().format(record)}"

def opsec(self, msg, *args, **kwargs):
    # Always inject "opsec" field so formatter and filter see it
    kwargs.setdefault("extra", {})["opsec"] = True
    self._log(logging.INFO, msg, args, **kwargs)

logging.Logger.opsec = opsec
logger = logging.getLogger("spotisly")

def configure_logging(level):
    """
    Configure logging output with OPSEC-colored formatting and verbosity levels.
    """
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.setLevel(logging.DEBUG)  # Let filters handle visibility

    formatter = ColoredFormatter("%(message)s")

    # Main handler: only non-opsec logs, filtered by verbosity
    main_handler = logging.StreamHandler()
    main_handler.setFormatter(formatter)
    main_handler.addFilter(lambda r: not getattr(r, "opsec", False) and r.levelno >= (
        logging.WARNING if level == 0 else logging.INFO if level == 1 else logging.DEBUG
    ))

    # OPSEC handler: show all opsec logs unconditionally
    opsec_handler = logging.StreamHandler()
    opsec_handler.setFormatter(formatter)
    opsec_handler.addFilter(lambda r: getattr(r, "opsec", False))

    root_logger.addHandler(main_handler)
    root_logger.addHandler(opsec_handler)

    # Enable HTTP debugging if -vv
    if level >= 2:
        import http.client as http_client
        http_client.HTTPConnection.debuglevel = 1
        logging.getLogger("urllib3").setLevel(logging.DEBUG)
        logging.getLogger("spotipy").setLevel(logging.DEBUG)

CHAR_TO_DURATION_RANGE = {
    chr(i): range(120 + (i - 32) * 5, 120 + (i - 31) * 5) for i in range(32, 127)
}

DURATION_TO_CHAR_MAP = {}
for char, r in CHAR_TO_DURATION_RANGE.items():
    for duration in r:
        DURATION_TO_CHAR_MAP[duration] = char

def validate_args(args):
    """
    Validate required arguments and handle OTP key generation.
    """
    if args.otp:
        args.key = otp()
    if args.technique != "duration":
        if not args.key or not all(c in string.hexdigits for c in args.key):
            logger.error("Invalid or missing key")
            exit(1)

def expand_position_key(key):
    """
    Convert the hex key into a list of integer positions for encoding.
    """
    if key.isdigit():
        return [int(c) if c != '0' else 16 for c in key]
    elif all(c in string.hexdigits for c in key):
        return [int(c, 16) if c != '0' else 16 for c in key.lower()]
    else:
        raise ValueError("Key must be digits or hex")

def otp():
    """
    Generate and return a 32-byte hexadecimal one-time pad key.
    """
    return ''.join(random.choices('0123456789abcdef', k=64))

def get_artist_pool(sp, artist_input, fallback=False):
    logger.info(f"Fetching tracks from artists: {artist_input}")
    names = [a.strip() for a in artist_input.split(',')]
    tracks = []
    all_names = set(names)

    for name in names:
        try:
            result = sp.search(q=f"artist:{name}", type="artist", limit=1)
            artist = result['artists']['items'][0]
            artist_id = artist['id']
            top_tracks = sp.artist_top_tracks(artist_id)['tracks']
            tracks.extend(top_tracks)

            if fallback:
                related = sp.artist_related_artists(artist_id)['artists']
                for r in related:
                    if r['name'] not in all_names:
                        try:
                            related_tracks = sp.artist_top_tracks(r['id'])['tracks']
                            tracks.extend(related_tracks)
                            all_names.add(r['name'])
                        except Exception:
                            continue
        except Exception:
            logger.warning(f"Could not fetch tracks for artist: {name}")

    return tracks, list(all_names)

def get_genre_pool(sp, genre, limit=3, fallback=False, only_on_retry=False):
    genres_to_search = [genre]

    if fallback and genre in GENRE_SIMILARITY:
        fallback_genres = GENRE_SIMILARITY[genre]
        if only_on_retry:
            print(f"→ Expanding genre fallback pool...")
            genres_to_search += fallback_genres
        else:
            logger.debug(f"(preemptive genre expansion for '{genre}')")
    elif not only_on_retry:
        logger.debug(f"No fallbacks added for genre '{genre}'")

    logger.info(f"Fetching tracks from genre(s): {genres_to_search}")
    all_tracks = []

    for g in genres_to_search:
        print(f"→ Searching playlists for genre: '{g}'")
        try:
            for page in range(15):  # Search up to 15 pages (75 playlists total)
                offset = page * 5
                try:
                    results = sp.search(q=g, type='playlist', limit=5, offset=offset)
                    playlist_items = results.get('playlists', {}).get('items', [])
                except Exception as e:
                    logger.warning(f"Failed to search genre '{g}' (offset {offset}): {e}")
                    continue

                for pl in playlist_items:
                    if not isinstance(pl, dict) or 'id' not in pl:
                        logger.debug(f"Skipping malformed playlist: {pl}")
                        continue

                    playlist_id = pl['id']
                    try:
                        data = sp.playlist_tracks(playlist_id)
                        if data and 'items' in data:
                            all_tracks.extend(t['track'] for t in data['items'] if t.get('track'))
                        else:
                            logger.debug(f"Empty or malformed playlist data for ID: {playlist_id}")
                    except Exception as e:
                        logger.debug(f"Error loading playlist '{playlist_id}': {e}")
        except Exception as e:
            logger.warning(f"General error fetching genre '{g}': {e}")
    return all_tracks

def strict_search(sp, char, position, genre_tracks, artist_list, used_uris):
    pool = genre_tracks[:]
    for artist in artist_list:
        try:
            result = sp.search(q=f'artist:"{artist}"', type='track', limit=25)
            pool.extend(result['tracks']['items'])
        except Exception:
            continue
    random.shuffle(pool)
    for track in pool:
        if track['uri'] in used_uris:
            continue
        title = track['name']
        if len(title) > position and title[position].lower() == char.lower():
            return track
    return None

def relaxed_search(char, pool, used_uris):
    for track in pool:
        if track['uri'] in used_uris:
            continue
        title = track['name']
        if any(c.lower() == char.lower() for c in title):
            return track
    return None

def relaxed_artist_search(char, pool, used_ids, pos=None):
    for track in pool:
        if track['id'] in used_ids:
            continue
        for artist in track['artists']:
            name = artist['name']
            if pos is not None:
                if len(name) > pos and name[pos].lower() == char.lower():
                    return track
            else:
                if char.lower() in name.lower():
                    return track
    return None

def match_in_title(track, char, pos):
    """
    Check if a given character matches the character at a position in the track title.
    """
    title = track['name']
    return len(title) > pos and title[pos].lower() == char.lower()

def match_in_artist(track, char, pos):
    """
    Check if a given character matches the character at a position in the artist name(s).
    """
    for artist in track['artists']:
        name = artist['name']
        if len(name) > pos and name[pos].lower() == char.lower():
            return True
    return False

def get_related_artists(sp, artist_name):
    result = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
    artist_id = result['artists']['items'][0]['id']
    related = sp.artist_related_artists(artist_id)['artists']
    return [a['name'] for a in related]

def ascii_to_duration_range(char):
    try:
        return CHAR_TO_DURATION_RANGE[char]
    except KeyError:
        raise ValueError(f"Character '{char}' out of printable ASCII range.")

def duration_to_char(duration):
    try:
        return DURATION_TO_CHAR_MAP[duration]
    except KeyError:
        raise ValueError(f"Duration {duration}s not mapped to any printable character.")

def describe_track(track):
    """
    Extract and return the track title and comma-separated artist string from a Spotify track object.
    """
    title = track.get("name", "")
    artists = ", ".join(artist.get("name", "") for artist in track.get("artists", []))
    return title, artists

def find_track_by_char(tracks, char):
    """
    Given a list of tracks and a target character, return a track whose duration fits the character's window.
    """
    start, end = ascii_to_duration_range(char)
    for track in tracks:
        duration_s = int(track['duration_ms'] / 1000)
        if start <= duration_s < end:
            return track
    return None

def decode_from_durations_range(tracks):
    """
    Given a list of tracks (in order), decode a message using their durations.
    """
    message = ""
    for track in tracks:
        duration_s = int(track['duration_ms'] / 1000)
        try:
            char = duration_to_char(duration_s)
        except ValueError:
            char = '?'
        message += char
    return message

def display_encoding_results(args, tracks, user_id, key, technique=None, playlist_url=None):
    """
    Display the results of an encoding operation, including track listing and encoding key.
    """
    header = "PLAYLIST CREATED" if playlist_url else "TEST MODE"
    print(f"\n{header}\n{'=' * len(header)}")
    if playlist_url:
        print(f"URL: {playlist_url}")
    print(f"User ID: {user_id}")
    print(f"Key: {key}")
    print(f"Playlist Name: {args.playlist}")
    print(f"Message: {args.message}")
    if technique:
        print(f"Technique: {technique}")
    print("Tracks:")

    positions = expand_position_key(key)

    for i, track in enumerate(tracks):
        title, artists = describe_track(track)
        pos_raw = positions[i % len(positions)]
        pos = 15 if pos_raw == 0 else pos_raw - 1

        if args.highlight:
            field_to_highlight = title if technique == "track" else artists
            if 0 <= pos < len(field_to_highlight):
                underlined_char = f"\033[4m{field_to_highlight[pos]}\033[0m"
                highlighted_field = field_to_highlight[:pos] + underlined_char + field_to_highlight[pos + 1:]
            else:
                highlighted_field = field_to_highlight

            if technique == "track":
                print(f"- {highlighted_field} - {artists}")
            else:
                print(f"- {title} - {highlighted_field}")
        else:
            print(f"- {title} - {artists}")

def run_opsec(opsec, sp, genre=None, artist=None, stage=None):
    if not opsec:
        return
    if stage:
        opsec.sleep_with_jitter(stage=stage)
    opsec.simulate_noise(sp, genre=genre, artist=artist)
    if opsec.level >= 2:
        opsec.simulate_human_browsing(sp)

def generic_encoder(sp, args, match_function, opsec=None):
    """
    Generic encoder used by specific encoding strategies, builds a playlist based on message and matching logic.
    """
    if not args.message:
        logger.error("Missing message.")
        exit(1)
    if not args.genre and not args.artist:
        logger.error("You must provide --genre or --artist")
        exit(1)

    positions = expand_position_key(args.key)
    logger.debug(f"Key positions: {positions}")

    run_opsec(opsec, sp, genre=args.genre, artist=args.artist, stage="pre-search")

    artist_pool, artist_list = get_artist_pool(sp, args.artist, fallback=True) if args.artist else ([], [])
    genre_pool = get_genre_pool(sp, args.genre, fallback=False) if args.genre else []
    full_pool = artist_pool + genre_pool

    if not full_pool:
        logger.error("No usable tracks found.")
        exit(1)

    used_uris = set()
    used_ids = set()
    result_tracks = []

    for i, char in enumerate(args.message):
        pos_raw = positions[i % len(positions)]
        pos = 15 if pos_raw == 0 else pos_raw - 1

        logger.info(f"[{i+1}/{len(args.message)}] Encoding '{char}' at position {pos} (key digit: {pos_raw})")

        found = False
        attempts = 0
        max_attempts = 5
        while not found and attempts < max_attempts:
            attempts += 1
            random.shuffle(full_pool)

            for track in full_pool:
                if track['uri'] in used_uris or track['id'] in used_ids:
                    continue
                if match_function(track, char, pos):
                    result_tracks.append(track)
                    used_uris.add(track['uri'])
                    used_ids.add(track['id'])
                    logger.info(f"→ Found in pool: '{track['name']}'")
                    found = True
                    break

            if found:
                break

            track = strict_search(sp, char, pos, genre_pool, artist_list, used_uris)
            if track:
                result_tracks.append(track)
                used_uris.add(track['uri'])
                used_ids.add(track['id'])
                logger.info(f"→ Strict fallback: '{track['name']}'")
                found = True
                break

            track = relaxed_artist_search(char, full_pool, used_ids, pos)
            if track:
                result_tracks.append(track)
                used_uris.add(track['uri'])
                used_ids.add(track['id'])
                logger.info(f"→ Relaxed fallback: '{track['name']}' (any position in artist)")
                found = True
                break

            if args.genre and attempts == 1:
                print(f"→ Expanding genre fallback pool...")
                extra_genre_tracks = get_genre_pool(sp, args.genre, limit=10, fallback=True, only_on_retry=True)
                genre_pool.extend(extra_genre_tracks)
                full_pool = artist_pool + genre_pool

        if not found:
            logger.error(f"   The key you provided is incompatible with your message.")
            logger.error(f"   Tried to find '{char}' at position {pos + 1} in a {'track title' if match_function.__name__ == 'match_in_title' else 'artist name'}, but failed after 5 attempts.")
            logger.error(f"   Try using a different key or changing your message.")
            exit(1)

    user_id = sp.me()['id']

    if args.publish:
        playlist = sp.user_playlist_create(user=user_id, name=args.playlist, public=True)
        sp.playlist_add_items(playlist_id=playlist['id'], items=[t['uri'] for t in result_tracks])

        run_opsec(opsec, sp, genre=args.genre, artist=args.artist, stage="pre-search")

        display_encoding_results(args, result_tracks, user_id, args.key, technique="track", playlist_url=playlist['external_urls']['spotify'])
    else:
        display_encoding_results(args, result_tracks, user_id, args.key, technique="track")

def encode_with_durations(sp, args, opsec=None):
    """
    Encode the message using characters mapped to track durations.
    """
    if not args.message:
        logger.error("Missing message.")
        exit(1)
    if not args.genre and not args.artist:
        logger.error("You must provide --genre or --artist")
        exit(1)

    # Show encoding plan before track fetching
    logger.info("\nEncoding Plan:")
    for i, char in enumerate(args.message):
        ascii_code = ord(char)
        dur_min, dur_max = ascii_to_duration_range(char).start, ascii_to_duration_range(char).stop
        logger.info(f"[{i+1}/{len(args.message)}] '{char}' → ASCII {ascii_code} → duration: {dur_min}-{dur_max-1}s")

    run_opsec(opsec, sp, genre=args.genre, artist=args.artist, stage="pre-search")
    
    # Fetch tracks
    artist_pool, _ = get_artist_pool(sp, args.artist, fallback=True) if args.artist else ([], [])
    genre_pool = get_genre_pool(sp, args.genre, fallback=False) if args.genre else []
    pool = artist_pool + genre_pool

    used_uris = set()
    result_tracks = []

    for i, char in enumerate(args.message):
        dur_min, dur_max = ascii_to_duration_range(char).start, ascii_to_duration_range(char).stop
        found = False
        attempts = 0
        max_attempts = 2

        while not found and attempts < max_attempts:
            attempts += 1

            for track in pool:
                if track['uri'] in used_uris:
                    continue
                duration_s = int(track['duration_ms'] / 1000)
                if dur_min <= duration_s < dur_max:
                    result_tracks.append(track)
                    used_uris.add(track['uri'])
                    title, artist_str = describe_track(track)
                    logger.info(f"→ Match: '{title}' - {artist_str} ({duration_s}s) for '{char}'")
                    found = True
                    break

            if not found and attempts == 1 and args.genre:
                # Retry with fallback genres
                extra_tracks = get_genre_pool(sp, args.genre, fallback=True, only_on_retry=True)
                pool.extend(extra_tracks)

        if not found:
            logger.error(f"Could not find track for '{char}' ({dur_min}-{dur_max-1}s)")
            exit(1)

    # Create playlist or test mode
    user_id = sp.me()['id']

    if opsec:
        opsec.sleep_with_jitter(stage="pre-playlist")

    if args.publish:
        playlist = sp.user_playlist_create(user=user_id, name=args.playlist, public=True)
        sp.playlist_add_items(playlist_id=playlist['id'], items=[t['uri'] for t in result_tracks])

        if opsec and opsec.level >= 2:
            opsec.simulate_add_remove_mistake(sp, playlist['id'], [t['uri'] for t in result_tracks])

        display_encoding_results(args, result_tracks, user_id, args.key, technique="track", playlist_url=playlist['external_urls']['spotify'])
    else:
        display_encoding_results(args, result_tracks, user_id, args.key, technique="track")

def encode_with_track_titles(sp, args, opsec=None):
    """
    Encode the message using characters matched in track titles.
    """
    if opsec:
        opsec.sleep_with_jitter(stage="pre-search")
        opsec.simulate_noise(sp, genre=args.genre, artist=args.artist)
        if opsec.level >= 2:
            opsec.simulate_human_browsing(sp)
    return generic_encoder(sp, args, match_in_title, opsec)

def encode_with_artist_names(sp, args, opsec=None):
    """
    Encode the message using characters matched in artist names.
    """
    if opsec:
        opsec.sleep_with_jitter(stage="pre-search")
        opsec.simulate_noise(sp, genre=args.genre, artist=args.artist)
        if opsec.level >= 2:
            opsec.simulate_human_browsing(sp)
    return generic_encoder(sp, args, match_in_artist, opsec)

def resolve_user_id(sp, display_name):
    """Resolve Spotify user ID from display name."""
    me = sp.me()
    if me.get("display_name", "").lower() == display_name.lower():
        return me["id"]
    
    uri = me.get("uri", "")
    match = re.match(r"spotify:user:([a-zA-Z0-9]+)", uri)
    if match:
        return match.group(1)

    raise ValueError(f"Unable to resolve user ID for display name: {display_name}")

def decode_from_track_titles(sp, args):
    """
    Decode a message by extracting characters from track titles at given key positions.
    """
    positions = expand_position_key(args.key)
    playlist_name = args.playlist

    # Automatically resolve display name to user ID if provided
    user = None
    if args.user:
        try:
            user_info = sp.user(args.user)
            user = user_info['id']
        except Exception:
            logger.warning(f"Could not resolve user '{args.user}', assuming it's a user ID")
            user = args.user

    playlist = None
    playlists = sp.user_playlists(user=user, limit=50) if user else sp.current_user_playlists(limit=50)
    for p in playlists['items']:
        if p['name'] == playlist_name:
            playlist = p
            break

    if not playlist:
        logger.error("Playlist not found")
        return

    items = sp.playlist_tracks(playlist_id=playlist['id'])['items']
    chars = []

    for i, item in enumerate(items):
        title = item['track']['name']
        pos = positions[i % len(positions)]
        if len(title) >= pos:
            chars.append(title[pos - 1])
            logger.info(f"{i+1:02d}. {title} → '{title[pos - 1]}'")
        else:
            chars.append("?")
            logger.warning(f"{i+1:02d}. {title} → position {pos} out of range")

    print(f"\nDecoded Message: {''.join(chars)}\n")

def decode_from_durations(sp, args):
    """
    Decode a message by interpreting track durations as character values.
    """
    playlist_name = args.playlist

    # Automatically resolve display name to user ID if provided
    user = None
    if args.user:
        try:
            user_info = sp.user(args.user)
            user = user_info['id']
        except Exception:
            logger.warning(f"Could not resolve user '{args.user}', assuming it's a user ID")
            user = args.user

    playlist = None
    playlists = sp.user_playlists(user=user, limit=50) if user else sp.current_user_playlists(limit=50)
    for p in playlists['items']:
        if p['name'] == playlist_name:
            playlist = p
            break

    if not playlist:
        logger.error("Playlist not found")
        return

    items = sp.playlist_tracks(playlist_id=playlist['id'])['items']
    decoded_chars = []

    if args.verbose:
        print("\nDecoded Playlist Table")
        print("======================")
        print(f"{'No.':<4} {'Track':<40} {'Duration':<9} {'Char'}")
        print("-" * 60)

    for i, item in enumerate(items):
        track = item['track']
        duration = int(track['duration_ms'] / 1000)
        title = track['name']
        try:
            char = duration_to_char(duration)
        except ValueError:
            char = '?'
        decoded_chars.append(char)

        if args.verbose:
            print(f"{i+1:<4} {title[:40]:<40} {duration:<9} {char}")

    if args.verbose:
        print("\nDecoded Message")
        print("---------------")
        print("".join(decoded_chars))
    else:
        print("\nDecoded Message")
        print("===============")
        print("".join(decoded_chars))

def parse_args():
    p = argparse.ArgumentParser(
        usage="spotisly.py {encode,decode} --technique {track,artist,duration} [options]"
    )

    p.add_argument("mode", choices=["encode", "decode"], help="Mode of operation: encode or decode a message")

    p.add_argument("--technique", "-t", choices=["track", "artist", "duration"], required=True,
                   help="Encoding technique to use")
    p.add_argument("--key", "-k", help="Specify hex or digit key for encoding/decoding (used with track/artist techniques)")
    p.add_argument("--otp", help="Generate a one-time pad key automatically", action="store_true")
    p.add_argument("--genre", "-g", help="Genre to use for track selection")
    p.add_argument("--artist", "-a", help="Artist(s) to use for filtering tracks (comma-separated)")
    p.add_argument("--playlist", "-p", help="Name of playlist to create (encode) or read (decode)")
    p.add_argument("--message", "-m", help="Message to encode (required for encode mode)")
    p.add_argument("--user", "-u", help="Spotify username or user ID to decode from (defaults to current user)")
    p.add_argument("--dry-run", action="store_true", help="Preview playlist without creating it")
    p.add_argument("--publish", action="store_true", help="Publish playlist to your public profile")
    p.add_argument("--highlight", "-H", action="store_true", help="Underline the encoded character in output")
    p.add_argument("--opsec", "-o", type=int, choices=[1, 2], help="Enable OPSEC behavior simulation (1 or 2)")
    p.add_argument("--verbose", "-v", action="count", default=0, help="Increase output verbosity (can repeat: -vv)")
    p.add_argument("--quiet", "-q", action="store_true", help="Suppress ASCII art banner")

    return p.parse_args()

def explain_opsec_level(level):
    if level == 1:
        print("OPSEC Level 1: Simulating mild noise (searching unrelated artists/genres).")
    elif level == 2:
        print("OPSEC Level 2: Simulating human-like browsing, album views, and add/remove mistakes.")

def get_spotify_client():
    """
    Authenticate and return a Spotify client instance using OAuth.
    """
    def create_auth_manager(show_dialog=False, cache_handler=None):
        return SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            show_dialog=show_dialog,
            cache_handler=cache_handler
        )

    try:
        auth_manager = create_auth_manager()
        sp = spotipy.Spotify(auth_manager=auth_manager)
        sp.me()
        return sp

    except SpotifyOauthError:
        logger.warning("Token expired or invalid, starting fresh auth flow...")
        cache_handler = create_auth_manager().cache_handler
        cache_handler.delete_cached_token()
        auth_manager = create_auth_manager(show_dialog=True, cache_handler=cache_handler)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        sp.me()
        return sp

def main():
    """
    Main entry point for parsing arguments, executing encode/decode logic, and handling OPSEC behavior.
    """
    args = parse_args()
    
    # Configure logging
    configure_logging(args.verbose)

    # Show banner early for no args or help
    if len(sys.argv) == 1 or any(arg in sys.argv for arg in ['-h', '--help']):
        print_banner()

    # Optional banner after parse unless --quiet
    if not args.quiet:
        print_banner()

    validate_args(args)

    # OPSEC info blurb
    if args.otp:
        print(f"Generated key: {args.key}")

    # OPSEC info blurb
    if args.opsec:
        explain_opsec_level(args.opsec)

    # Auth and dispatch
    sp = get_spotify_client()
    user = sp.current_user()
    logger.info(f"Logged in as: {user['display_name']} ({user['id']})")

    if args.mode == "encode":
        if args.technique == "track":
            encode_with_track_titles(sp, args, OpSecSimulator(level=args.opsec or 0))
        elif args.technique == "artist":
            encode_with_artist_names(sp, args, OpSecSimulator(level=args.opsec or 0))
        elif args.technique == "duration":
            encode_with_durations(sp, args, OpSecSimulator(level=args.opsec or 0))
        else:
            logger.error("Unsupported encoding technique")

    elif args.mode == "decode":
        if args.technique == "duration":
            decode_from_durations(sp, args)
        else:
            decode_from_track_titles(sp, args)

if __name__ == "__main__":
    main()