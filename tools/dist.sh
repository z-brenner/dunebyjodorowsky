#!/bin/sh
# Assemble the publishable site into dist/ (used by the Cloudflare Pages build).
# Only the page, its assets and the images are published; tools/ and docs are not.
set -e
rm -rf dist
mkdir dist
cp index.html dist/
cp -r assets art plates thumbs dist/
cat > dist/_headers <<'H'
/art/*
  Cache-Control: public, max-age=2592000
/plates/*
  Cache-Control: public, max-age=2592000
/thumbs/*
  Cache-Control: public, max-age=86400
/assets/*
  Cache-Control: public, max-age=300
H
echo "dist: $(find dist -type f | wc -l) files, $(du -sh dist | cut -f1)"
