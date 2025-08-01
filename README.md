<img width="1280" height="400" alt="Spotisly-Banner" src="https://github.com/user-attachments/assets/58d74466-2b8d-464a-9ed1-df1296cf7e2e" />


Spotisly is a messaging tool that encodes/decodes messages into Spotify playlists using track metadata like title, artist, or duration. It can also simulate basic human behavior through OPSEC modes to make it look more normal (see note about this below).

# Why?
Dunno, felt like it

# Features
## Encode & decode messages:
- **Track Titles**: Encodes each character by finding a track whose title contains the character at a specific position (based on the key)
- **Artist Names**: Similar to track titles, but uses the concatenated artist string (e.g., `"Deadmau5, Skrillex"`) as the match field
- **Duration**: Maps characters to time windows. For example, the letter `a` may correspond to tracks 60–90 seconds long, while `z` might be 300–330 seconds. This creates a unique but looser mapping suitable for low-entropy messaging.

## Fallback Strategy:
- **Strict Position Matching**: Search playlists in the target genre(s) and extract tracks. Check if the character appears exactly at the specified position in the selected field—title, artist or duration window
- **Relaxed Position Matching**: Instead of requiring the encoded character to be at a specific position, allow it to be anywhere in the field
- **Genre Expansion**: Pull from a predefined `GENRE_SIMILARITY` map to try related genres (e.g., if `metal` fails, it may try `hard rock`, `industrial`, etc.)
- **Related Artists Expansion (Artist-Mode Only)** Use `sp.artist_related_artists()` to fetch related artists. Search tracks by those related artists for both strict and relaxed matching
- **Last Resort Random Fill**: If still no match, optionally fill the gap with a random track from the same pool, and encode a placeholder

## Multiple encoding modes:
- **One-time pad key**: If `--otp` is used, a random one-time pad is generated (32 hex chars = 32 positions)
- **Positional hex key encoding**: If `--key` is provided, it is parsed as either hex (preferred) or numeric digits
- Each position determines where in the field the encoded character must appear

Example:
```bash
Message: HELLO
Key:     a1b2c3...

Means:  Encode 'H' at pos 10, 'E' at pos 1, 'L' at pos 11, etc.
```

## OPSEC simulation
| Level | Behavior                                                                 |
| ----- | ------------------------------------------------------------------------ |
| 1     | Random noise searches, track previews, and delays                        |
| 2     | Additional browsing, add/remove mistakes, track previews                 |


# Requirements
- Spotify account (free or premium)
- Spotify Developer App:
	- Go to Spotify Developer Dashboard
	- Create an app with the following and copy the Client ID and Client Secret
```yaml
Name: Anything you want
Description: Anything you want
Redirect URIs: http://127.0.0.1:8888/callback
```

- Python libraries:
```bash
pip install spotipy --break-system-packages

OR
python3 -m venv venv
source venv/bin/activate
pip install spotipy
```

# Usage
Encode:
```bash
python3 spotisly.py encode -m "secret msg" -t track -p "Chill Vibes" --genre rock --otp --publish
```

Decode:
```bash
python3 spotisly.py decode -t track -p "Chill Vibes" --key a1b2c3
```

| Option                     | Description                                                                   |
| -------------------------- | ------------------------------------------------------------------------------ |
| `--technique` / `-t`      | Encoding method: `track`, `artist`, `duration`                                |
| `--key` / `-k` / `--otp`  | Manual key or auto-generated one-time pad                                     |
| `--genre` / `-g`          | Filter by genre (with fallback expansion)                                     |
| `--artist` / `-a`         | Filter by artist(s), separate by comma for multiple (`'Deadmau5, Skrillex'`)  |
| `--playlist` / `-p`       | Playlist name to create or decode                                             |
| `--highlight` / `-H`      | Underline the encoded character                                               |
| `--opsec` / `-o`          | OPSEC level: `1` or `2`                                                      |
| `--dry-run`               | Simulate without creating the playlist                                        |
| `--publish`               | Make playlist public                                                          |
| `--quiet` / `-q`          | Suppress ASCII banner                                                         |
| `--verbose` / `-v`        | Increase logging verbosity (`-vv` max)                                        |

# How it works
## Encoding
Uses the Spotify API to:
- Search for playlists related to the genre or artist specified (the API endpoint for searching genres directly is depreciated)

Encodes the message using a key. If your message is longer than the key, it will just loop on the key
- You can specify with `--key/-k` (hex only)
- You can generate a one time pad with `--otp` which will randomly generate a 32 character key

> ![TIP]
> For both encode/decode, it won't work if you have letters in positions that aren't common for tracks/artists
> If your key has a 1 or 2 at the same position as a space in your message, it probably won't work

<img width="972" height="577" alt="Screenshot 2025-08-02 074608" src="https://github.com/user-attachments/assets/0efab487-803f-4536-9e72-cfff5418e212" />
<img width="1192" height="702" alt="Screenshot 2025-08-02 074703" src="https://github.com/user-attachments/assets/bf31d52b-0d2d-41eb-b19d-1ff65ca6c4a3" />

## Decoding
Uses the Spotify API to:
- Find the user (requires the username, not the display name which is kinda annoying)
- Find the user's playlist by its name

Decodes the message using a key
- You can specify with `--key/-k` (hex characters only)
- You can specify the user and playlist name

<img width="1408" height="58" alt="Screenshot 2025-08-02 074843" src="https://github.com/user-attachments/assets/c4ba2a27-d1e7-4b43-a14d-f603106e2732" />

## OPSEC:
I did this just to muck around a see whether it could be done
| **Feature**                        | **Level 0** | **Level 1** | **Level 2+** |
| ---------------------------------- | :---------: | :---------: | :----------: |
| Genre/Artist noise                 |      ❌     |      ✅    |       ✅     |
| Random jitter delays               |      ❌     |      ✅    |       ✅     |
| Related artist exploration         |      ❌     |      ✅    |       ✅     |
| Fuzzy queries & typos              |      ❌     |      ❌    |       ✅     |
| Human-like playlist/album browsing |      ❌     |      ❌    |       ✅     |
| Add/remove mistake simulation      |      ❌     |      ❌    |       ✅     |

> ![IMPORTANT]
> Even though I implemented the OPSEC levels, it is still sending requests to `api.spotify.com` and not `open.spotify.com` (where normal user traffic goes) so if someone was actually looking, they can probably tell it isn't a real user. Oh well.

`sleep_with_jitter()`
Simulates human pause/delay using random sleep durations:
- Combines a base delay with a random jitter

`simulate_noise()`
Simulates fake search and preview activity. Behaviors by OPSEC Level:
- **Level 1**:
	- Performs 2–3 genre queries like `"electronic mix"`, `"rock essentials"`
	- Finds related artists to the target and previews 1–2 tracks
- **Level 2**:
- Adds fuzzy typos and more noisy variants (e.g., `"electronic neww"`, `"artist musics"`)
- Increases the sample size of searches and track previews

It randomly chooses 3 final noise queries and simulates previewing those tracks

`maybe_make_mistake()`
Randomly:
- Reorders two tracks or
- Removes one track from the playlist

`simulate_human_browsing()`
Only used in OPSEC Level 2. Simulates a full browsing session:
- **Playlist Search** – looks up random playlist search terms
- **Album Exploration** – browses albums and previews sample tracks
- **Track Save/Remove** – saves and unsaves a track to simulate noise in user library actions

`simulate_add_remove_mistake()`
Used at OPSEC Level 2:
- Fuzzy searches a nonsense track (e.g., `"chilll song"`)
- Adds it to the playlist, simulates a delay, then removes it

This mimics an accidental misclick and recovery, helping disguise automation with “believable error patterns”
