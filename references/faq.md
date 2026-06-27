# FAQ

## How do I add a new journal?
Use create_venue_profile.py with the journal's official width guidelines, then validate.

## Can I use my own colour palette?
Not yet — palette is selected from built-in options. Custom palette support is planned.

## Why is my figure blank?
Check column names match exactly. Run validate_request.py first.

## How do I update a profile?
Edit the YAML file and update verified_at to today's date.

## What if my journal requires CMYK?
Set color_mode: "cmyk" in the profile. RGB is default.
