# THE IDOLM@STER MILLION LIVE ANIMATION STAGE Fan Subs

This repo stores fansubs of *THE IDOLM@STER MILLION LIVE ANIMATION STAGE* made by `KitaujiSub`. Read below to get more information.

## Prerequisites

+ Aegisub
  + [DependencyControl (optional)](https://github.com/TypesettingTools/DependencyControl)
  + [Merge Scripts](https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts)

It is strongly advised to install `Merge Scripts` via `DependencyControl`, but you can always manual add all requirements and install the marco.

## Workflow

### File Structure

For each episode we have the following graph:

```
epxx → main folder
├── insert
│   ├── insert0x.ass
│   └── insert0x_tc.ass
├── screen
│   ├── screen.ass
│   └── screen_tc.ass
├── staff
│   ├── stf_kitauji.ass
│   └── stf_lolihouse.ass
├── epxx_sc.ass
└── epxx_tc.ass
```

Each episode should have an independent main folder, and similarly organized structure.

*Note: for insert and screen lines, traditionalization could be done after merging files, so _tc.ass is not necessary.*

Insert asses contain insert songs ONLY, so as other asses, except for the main file, epxx_sc/tc.ass. Files should be imported accordingly using `Merge Scripts` and transformed into the final release candidate.

### Procedure

1. Create a new `epxx_sc.ass`, fill in translated lines, and complete timing. Then copy these lines and fill in Japanese Subs.
2. Process any screen text or insert song in their independent files, then import them in the main file using `Merge Scripts`. *(Also import OP at this time!)*
3. Quality Control for the main file.
4. Merge all files and save to other place.
5. Clean up and generate release candidate, ZHT-ization...