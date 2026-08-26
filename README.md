# vonkagaoan.com

Personal portfolio. Plain HTML and CSS, no build step, no dependencies.
Hosted on GitHub Pages from the `vonimatic` account.

## Why it is built this way

- **No framework.** It is images, text and video embeds. React buys nothing here and
  something to maintain in two years.
- **Anchored sections, not JS tabs.** `#realtime` and `#software` are deep-linkable, so each
  CV variant can point at the section its audience cares about:
  - 3D CV links `vonkagaoan.com/#realtime`
  - Technical CV links `vonkagaoan.com/#software`
- **Public repo on purpose.** The repo is itself part of the pitch. It is the visible GitHub
  presence, since everything else on the account is private.

## Setup

```bash
git init
git add -A
git commit -m "Initial portfolio"
gh repo create vonimatic/vonimatic.github.io --public --source=. --push
```

Named `vonimatic.github.io` so it serves from the root rather than `/reponame`.
Pages then goes live at `https://vonimatic.github.io` with no configuration.

### Custom domain

1. Buy `vonkagaoan.com`
2. Add a `CNAME` file at the repo root containing exactly `vonkagaoan.com`
3. At the registrar, add four A records for the apex pointing at
   `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
4. In repo Settings > Pages, set the custom domain and tick **Enforce HTTPS**

## Video

**Do NOT use Git LFS.** GitHub Pages does not resolve LFS and will serve the pointer file
instead of the video, so clips silently break. Keep them as normal git objects, under 100MB
each, which the compression below makes easy.

### Short silent loops: self-host

Five to fifteen seconds, no audio, autoplaying. A ten second 720p clip lands around 1 to 2MB.

```bash
# H.264 fallback. -an strips audio, +faststart lets it play before fully downloading
ffmpeg -i in.mov -vf "scale=1280:-2,fps=30" -c:v libx264 -crf 28 -preset slow -an -movflags +faststart media/clip.mp4

# VP9, roughly 30% smaller, list this one FIRST in the <source> order
ffmpeg -i in.mov -vf "scale=1280:-2,fps=30" -c:v libvpx-vp9 -crf 33 -b:v 0 -an media/clip.webm

# poster frame, grabbed at 1s
ffmpeg -i in.mov -ss 1 -vframes 1 -vf "scale=1280:-2" -q:v 3 media/clip-poster.jpg
```

`muted` and `playsinline` on the `<video>` tag are not optional. Without `muted`, Chrome and
Safari refuse to autoplay. Without `playsinline`, iOS forces fullscreen.

### The full reel: Vimeo

Not YouTube. Vimeo is what the animation, VFX and real-time industry uses, and it is the link
format a studio expects to be handed. YouTube brings branding, an end screen of unrelated
videos and possible ads. Uncomment the iframe in `index.html` and drop the video id in.

## Before it goes live

- [ ] Make `voniikag/cv` **private**. It is a live 2023 Pages site that says Von currently
      works at Yoobee, omits SkillsVR and GeneXR, and rates Python at one star
- [ ] Turn on *Include private contributions on my profile* in `vonimatic` settings, so the
      profile does not look dormant when every repo is private
- [ ] Replace the placeholder cards with real captured media
- [ ] Add a 1200x630 `og:image` so pasted links preview properly

## GeneXR material

Permission covers **public** use, confirmed 2026-08-26. Still exclude anything commercially
sensitive, plus **client names and the product name**. Describe the work, do not label it.

System access ends **25 September 2026**. Capture before then.
