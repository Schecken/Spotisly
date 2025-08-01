import random
import time
import logging

logger = logging.getLogger(__name__)

logger = logging.getLogger("opsec")
logger.setLevel(logging.INFO)  # Always show OPSEC actions

class OpSecSimulator:
    def __init__(self, level=1):
        """
        Initialize the OPSEC simulator with a specified simulation level.
        Level 0: No simulation
        Level 1: Basic interaction
        Level 2+: Human-like behavior
        """
        self.level = level

    def sleep_with_jitter(self, base=6, jitter=9, stage=None):
        """
        Introduce randomized sleep to simulate human delay or distraction.
        """
        if self.level < 1:
            return
        delay = base + random.uniform(0, jitter)
        if stage:
            logger.opsec(f"Sleeping {delay:.2f}s during stage: {stage}")
            logger.info(f"Jitter details: base={base}, jitter={jitter}, total={delay:.2f}s")
        time.sleep(delay)

    def simulate_noise(self, sp, genre=None, artist=None):
        """
        Perform noise generation actions on Spotify to simulate a real user.
        Includes searches for genre and artist variants and exploration of related tracks.
        """
        if self.level < 1:
            return

        logger.opsec("Simulating noise: Searching unrelated queries")
        queries = []

        # 1. Genre-based noise
        if genre:
            genre_variants = [
                f"{genre} deep cuts",
                f"{genre} mix",
                f"{genre} playlist",
                f"{genre} essentials",
                f"{genre} underground",
                f"{genre} radio",
                f"{genre} new wave",
            ]

            if self.level == 1:
                queries.extend(random.sample(genre_variants, k=min(3, len(genre_variants))))
            
            elif self.level >= 2:
                # Add more queries for a more human-like browsing pattern
                unique_variants = list(set(genre_variants))  # remove accidental duplicates
                queries.extend(random.sample(unique_variants, k=min(5, len(unique_variants))))

                # Add fuzzy/human-error-like variants
                fuzzy_queries = [
                    f"{genre} sond",  # typo
                    f"{genre} list",
                    f"{genre} best songs",
                    f"{genre} vibes",
                    f"{genre} musics",
                ]
                queries.extend(random.sample(fuzzy_queries, k=min(2, len(fuzzy_queries))))

        # 2. Artist-based noise
        if artist:
            try:
                artist_results = sp.search(artist, limit=1, type="artist")
                artists = artist_results.get("artists", {}).get("items", [])
                if artists:
                    base_artist = artists[0]
                    logger.opsec(f"Exploring related artists to: {base_artist['name']}")
                    related = sp.artist_related_artists(base_artist['id'])
                    related_names = []

                    sample_size = 2 if self.level == 1 else min(4, len(related['artists']))
                    for rel_artist in random.sample(related['artists'], sample_size):
                        logger.opsec(f"Found related artist: {rel_artist['name']}")
                        related_names.append(rel_artist['name'])
                        try:
                            tracks = sp.artist_top_tracks(rel_artist['id'], country='US')
                            track_sample = 2 if self.level == 1 else min(4, len(tracks['tracks']))
                            for track in random.sample(tracks['tracks'], track_sample):
                                logger.opsec(f"Previewing top track: {track['name']}")
                                self.sleep_with_jitter(base=8, jitter=4, stage="noise")
                        except Exception as e:
                            logger.warning(f"Failed to get top tracks for {rel_artist['name']}: {e}")

                    # Related artist queries
                    queries.extend(f"{r} hits" for r in related_names)

                    # Artist-specific variants
                    basic_variants = [
                        f"{artist} acoustic",
                        f"{artist} remix",
                        f"{artist} rare tracks",
                        f"{artist} old live",
                    ]
                    queries.extend(basic_variants)

                    if self.level >= 2:
                        # Fuzzy/human-like artist queries
                        fuzzy_variants = [
                            f"{artist} best",
                            f"{artist} song",
                            f"{artist} neww",  # typo
                            f"{artist} musics",
                            f"{artist} track list",
                            f"{artist} hits",
                        ]
                        queries.extend(random.sample(fuzzy_variants, k=min(3, len(fuzzy_variants))))
            except Exception as e:
                logger.warning(f"Failed to get related info for artist '{artist}': {e}")

        # 3. Fallback queries
        if not queries:
            fallback_noise = ["calm vibes", "ambient synth", "random soundscape", "instrumental chill"]
            queries.extend(random.sample(fallback_noise, k=2))

        # Execute noise queries
        for q in random.sample(queries, min(3, len(queries))):
            logger.opsec(f"Noise query: '{q}'")
            try:
                results = sp.search(q, limit=3, type="track")
                for track in results.get("tracks", {}).get("items", []):
                    logger.opsec(f"Previewing: {track['name']} by {', '.join(a['name'] for a in track['artists'])}")
                    self.sleep_with_jitter(base=7, jitter=5, stage="noise")
            except Exception as e:
                logger.warning(f"Noise search failed for '{q}': {e}")

    def maybe_make_mistake(self, playlist_tracks):
        """
        Simulate human error by occasionally reordering or removing a track
        from the list of playlist tracks prior to submission.
        """
        if self.level < 1 or not playlist_tracks:
            return playlist_tracks
        if random.random() < 0.2:
            mistake_type = random.choice(["reorder", "remove"])
            if mistake_type == "remove" and len(playlist_tracks) > 1:
                idx = random.randint(0, len(playlist_tracks)-1)
                removed = playlist_tracks.pop(idx)
                logger.opsec(f"Simulated mistake: removed track at index {idx}")
                logger.opsec(f"Removed track: {removed['name']}")
            elif mistake_type == "reorder" and len(playlist_tracks) > 1:
                i, j = random.sample(range(len(playlist_tracks)), 2)
                playlist_tracks[i], playlist_tracks[j] = playlist_tracks[j], playlist_tracks[i]
                logger.opsec(f"Simulated mistake: reordered tracks {i} and {j}")
                logger.opsec(f"Track at {i}: {playlist_tracks[i]['name']}, Track at {j}: {playlist_tracks[j]['name']}")
        return playlist_tracks

    def simulate_human_browsing(self, sp):
        """
        Simulate a real user's browsing session by interacting with playlists, 
        albums, and saving/removing tracks to mimic genuine traffic.
        Only active at level 2 and above.
        """
        if self.level < 2:
            return

        logger.opsec("Simulating human-like browsing session...")

        # 1. Browse random playlists via search
        try:
            terms = ["chill", "vibes", "hits", "deep", "relax", "party", "mix", "mood", "focus"]
            for _ in range(2):
                q = random.choice(terms)
                logger.opsec(f"Searching for playlists with query: '{q}'")
                results = sp.search(q, limit=3, type="playlist") or {}
                playlists = results.get("playlists", {}) or {}
                items = playlists.get("items", []) or []

                if not items:
                    logger.info(f"No playlists found for query '{q}'")
                    continue

                for playlist in items:
                    name = playlist.get("name", "<unknown>")
                    logger.opsec(f"Viewing playlist: {name}")
                    self.sleep_with_jitter(base=4, jitter=9, stage="browse")

        except Exception as e:
            logger.warning(f"Playlist browsing via search failed: {e}")

        # 2. Explore random albums
        try:
            for _ in range(2):
                q = random.choice(["greatest hits", "deluxe", "anniversary", "remaster"])
                results = sp.search(q, limit=2, type="album")
                for album in results.get("albums", {}).get("items", []):
                    logger.opsec(f"Exploring album: {album['name']}")
                    tracks = sp.album_tracks(album['id'])
                    for track in random.sample(tracks['items'], min(1, len(tracks['items']))):
                        logger.opsec(f"Previewing album track: {track['name']}")
                        self.sleep_with_jitter(base=8, jitter=4, stage="preview")
        except Exception as e:
            logger.warning(f"Album browsing failed: {e}")

        # 3. Save then remove a track
        try:
            results = sp.search("chill", limit=5, type="track")
            tracks = results.get("tracks", {}).get("items", [])
            if tracks:
                track = random.choice(tracks)
                sp.current_user_saved_tracks_add([track['id']])
                logger.opsec(f"Saved track: {track['name']}")
                self.sleep_with_jitter(base=3, jitter=2, stage="save")
                sp.current_user_saved_tracks_delete([track['id']])
                logger.opsec(f"Removed track: {track['name']}")
        except Exception as e:
            logger.warning(f"Failed to save/remove track: {e}")

    def simulate_add_remove_mistake(self, sp, playlist_id, inserted_track_ids):
        """
        Simulate a user mistakenly adding and then removing a wrong track
        from the playlist to generate realistic interaction noise.
        """
        if self.level < 2:
            return

        try:
            # Simulate a bad search
            fuzzy_queries = ["cool vibe", "chilll song", "synth jam", "electro tacks", "neww hits"]
            query = random.choice(fuzzy_queries)
            logger.opsec(f"Fuzzy search query (mistake): '{query}'")
            results = sp.search(query, limit=5, type="track")
            self.sleep_with_jitter(stage="search-mistake")

            tracks = results.get("tracks", {}).get("items", [])
            if not tracks:
                return

            # Choose and add a 'wrong' track
            wrong_track = random.choice(tracks)
            sp.playlist_add_items(playlist_id, [wrong_track['id']])
            logger.opsec(f"Mistakenly added track: {wrong_track['name']}")
            self.sleep_with_jitter(stage="realise-mistake")

            # Remove the 'wrong' track
            sp.playlist_remove_all_occurrences_of_items(playlist_id, [wrong_track['id']])
            logger.opsec(f"Removed mistaken track: {wrong_track['name']}")
            self.sleep_with_jitter(stage="recover-from-mistake")

        except Exception as e:
            logger.warning(f"Failed during mistaken add/remove track: {e}")
