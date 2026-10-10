# srt-tools

Small subtitle utilities. Pure Python, no dependencies.

## Commands

```bash
# shift all timestamps by +/- seconds (fix out-of-sync subs)
python srttools.py shift in.srt out.srt --seconds 1.5
python srttools.py shift in.srt out.srt --seconds -0.8

# merge multi-part subtitles, auto-sorted and renumbered
python srttools.py merge out.srt part1.srt part2.srt

# renumber entries sequentially
python srttools.py renum in.srt out.srt

# strip <i>/<b>/<u>/<font> formatting tags
python srttools.py strip in.srt out.srt
```

Timestamps are clamped at 00:00:00,000 so negative shifts never break the file.
