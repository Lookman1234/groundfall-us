# Publish guide: get the GroundFall-US DOI

*Plain-language note: GroundFall-US v1.0 is already on GitHub. These steps turn it into a permanent, citable record on Zenodo with a DOI. You do them yourself because Zenodo needs your login. Time: about 10 minutes.*

**Order matters: do Step 1 before Step 2.** Zenodo only archives releases created after its switch is on.

## Copy-ready text

- **Release tag:** `v1.0.0`
- **Release title:** `GroundFall-US v1.0.0`
- **Release description:** `First public release. Ground-failure incidents at U.S. mines, 2000 to 2026, built from the MSHA 2026-10-09 data edition. See README, docs/SUMMARY.md, and docs/LIMITATIONS.md.`

(Title, authors, ORCID, license, and keywords for Zenodo are already in the repository's `.zenodo.json` file, so Zenodo fills them in for you.)

## Step 1: Switch on Zenodo for the repository (3 min)

1. Go to https://zenodo.org and click **Log in**. Choose **Log in with ORCID** so your ORCID iD is attached.
2. Click your name (top right), then **GitHub**.
3. If asked, click **Connect** and approve access to your GitHub account.
4. Find **Lookman1234/groundfall-us** in the list. If it isn't there, click **Sync now** and wait a few seconds.
5. Flip its switch to **On**. It should turn green.

## Step 2: Create the release on GitHub (3 min)

1. Open https://github.com/Lookman1234/groundfall-us/releases/new
2. Click **Choose a tag**, type `v1.0.0`, and click **Create new tag: v1.0.0 on publish**. Target: **main**.
3. Paste the release title and description from above.
4. Click **Publish release**.

## Step 3: Collect the DOI (2 to 5 min wait)

1. Back on Zenodo, go to your name → **GitHub**. Next to groundfall-us, a DOI badge appears within a few minutes. It looks like `10.5281/zenodo.1234567`.
2. Click the badge to open the record. Check that the authors are Lukman Alabede (with ORCID) and Kayode Komolafe, and that the license is CC BY 4.0.
3. **Send the DOI to Claude.** Claude adds it to the README, `CITATION.cff`, and your evidence log the same day.

## Optional, before Step 2

- **Repository visibility.** The repository is Public, which Zenodo needs. Leave it Public.
- **Kayode's ORCID.** If you want his ORCID on the Zenodo record, send it to Claude before Step 2 so it goes into `.zenodo.json`.
